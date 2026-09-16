"""
Day 8 edge-case tests.

Run with:  pytest tests/test_backend.py -v

Uses an in-memory SQLite DB and MOCKS the AI recognition call, so these
run in seconds without needing real photos or InsightFace installed.
Keep a *separate* small manual test session with real classroom photos
for the actual accuracy/threshold tuning (see notes at the bottom).
"""

import json
import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import get_db
from app.main import app

from sqlalchemy.pool import StaticPool

# --- Test DB setup (SQLite in-memory, fresh per test run) -------------

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def fake_embedding(seed: int) -> list:
    """Deterministic fake 512-d embedding so cosine similarity is predictable."""
    import numpy as np
    rng = np.random.RandomState(seed)
    vec = rng.randn(512)
    return vec.tolist()


def add_student(db, reg_no, name, embedding):
    student = models.Student(
        registration_number=reg_no,
        name=name,
        embedding=json.dumps(embedding),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


# ------------------------------------------------------------------
# Test 1: Unregistered student's photo -> should come back Unknown,
# not crash, and not be marked present for anyone.
# ------------------------------------------------------------------
def test_unregistered_face_is_unknown(client, monkeypatch):
    db = TestingSessionLocal()
    emb_a = fake_embedding(1)
    add_student(db, "21CS001", "Alice", emb_a)
    db.close()

    # Simulate an AI detection of a face that matches NOBODY
    # (a random, very different embedding).
    unregistered_face_embedding = fake_embedding(999)

    def mock_recognize(image_path):
        return [{"embedding": unregistered_face_embedding, "bbox": [0, 0, 10, 10], "det_score": 0.9}]

    monkeypatch.setattr("app.main.recognize_classroom_faces", mock_recognize)

    response = client.post(
        "/recognize-and-mark/",
        data={"class_name": "CS101"},
        files={"image": ("test.jpg", io.BytesIO(b"fake image bytes"), "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["unknown_faces_detected"] == 1
    assert body["present_count"] == 0
    assert body["absent_count"] == 1  # Alice is absent, correctly


# ------------------------------------------------------------------
# Test 2: Duplicate prevention - calling the endpoint twice for what
# should be the same session shouldn't double-count a student, and
# the DB unique constraint should hold even if app logic is bypassed.
# ------------------------------------------------------------------
def test_duplicate_attendance_prevention_at_db_level(client):
    db = TestingSessionLocal()
    add_student(db, "21CS002", "Bob", fake_embedding(2))
    session = models.ClassSession(class_name="CS101")
    db.add(session)
    db.commit()
    db.refresh(session)

    record1 = models.AttendanceRecord(
        student_id=1, class_session_id=session.id,
        status=models.AttendanceStatus.PRESENT, similarity_score=0.8,
    )
    db.add(record1)
    db.commit()

    # Attempt to insert a second PRESENT record for the same student + session.
    record2 = models.AttendanceRecord(
        student_id=1, class_session_id=session.id,
        status=models.AttendanceStatus.PRESENT, similarity_score=0.75,
    )
    db.add(record2)

    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.close()


# ------------------------------------------------------------------
# Test 3: Two detected faces resolve to the SAME registered student
# (e.g. overlapping bounding boxes) -> should dedupe to one PRESENT
# record, keeping the higher-similarity match.
# ------------------------------------------------------------------
def test_duplicate_detection_same_student_dedupes(client, monkeypatch):
    db = TestingSessionLocal()
    emb = fake_embedding(3)
    add_student(db, "21CS003", "Carol", emb)
    db.close()

    def mock_recognize(image_path):
        # Same student detected twice with slightly different embeddings/boxes
        return [
            {"embedding": emb, "bbox": [0, 0, 10, 10], "det_score": 0.9},
            {"embedding": emb, "bbox": [50, 50, 60, 60], "det_score": 0.85},
        ]

    monkeypatch.setattr("app.main.recognize_classroom_faces", mock_recognize)

    response = client.post(
        "/recognize-and-mark/",
        data={"class_name": "CS101"},
        files={"image": ("test.jpg", io.BytesIO(b"fake"), "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["present_count"] == 1  # not 2


# ------------------------------------------------------------------
# Test 4: Large class Excel export doesn't error and contains
# expected row count.
# ------------------------------------------------------------------
def test_excel_export_large_class(client):
    from app.services.excel_service import generate_attendance_excel
    import pandas as pd

    db = TestingSessionLocal()
    session = models.ClassSession(class_name="CS101")
    db.add(session)
    db.commit()
    db.refresh(session)

    N = 120  # simulate a large class
    for i in range(N):
        s = add_student(db, f"21CS{i:04d}", f"Student{i}", fake_embedding(i))
        record = models.AttendanceRecord(
            student_id=s.id,
            class_session_id=session.id,
            status=models.AttendanceStatus.PRESENT if i % 2 == 0 else models.AttendanceStatus.ABSENT,
            similarity_score=0.6 if i % 2 == 0 else None,
        )
        db.add(record)
    db.commit()

    buffer = generate_attendance_excel(db, session.id)
    df = pd.read_excel(buffer)
    assert len(df) == N
    db.close()


# ------------------------------------------------------------------
# Test 5: Bad input handling - corrupt/non-image upload should return
# a clean 4xx, not a 500.
# ------------------------------------------------------------------
def test_invalid_file_type_rejected(client):
    response = client.post(
        "/recognize-and-mark/",
        data={"class_name": "CS101"},
        files={"image": ("notes.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert response.status_code == 415


def test_empty_file_rejected(client, monkeypatch):
    monkeypatch.setattr("app.main.recognize_classroom_faces", lambda path: [])
    response = client.post(
        "/recognize-and-mark/",
        data={"class_name": "CS101"},
        files={"image": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
    )
    assert response.status_code == 400


# ------------------------------------------------------------------
# NOTE on real accuracy testing (not something pytest can automate):
# For the 1/3/5/10+ faces, lighting/angle, and threshold-tuning tests
# from the plan, run manual tests against /recognize-and-mark/ with
# real classroom photos through Swagger UI (/docs) or curl, and log
# the similarity scores for correct vs incorrect matches into a CSV.
# That's what you'll use to pick SIMILARITY_THRESHOLD in recognition.py.
# ------------------------------------------------------------------