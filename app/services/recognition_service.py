"""
Backend-side face matching logic.

This module assumes Member 1's AI code exposes a function with this shape
(agree on this exact contract with them on Day 7 morning):

    def recognize_classroom_faces(image_path: str) -> list[dict]:
        return [
            {"embedding": [512 floats], "bbox": [x1,y1,x2,y2], "det_score": 0.94},
            ...
        ]

i.e. the AI module returns raw embeddings per detected face; the BACKEND
does the comparison against registered students and applies the threshold.
This division of labor is deliberate: it keeps the AI module stateless and
DB-agnostic, and keeps the threshold tunable from one place (here) without
redeploying the AI code.

If Member 1's module instead does the matching itself and returns
student_ids directly, skip straight to `dedupe_matches` below with their
output reshaped to match `MatchResult`.
"""

import json
import numpy as np
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Student

SIMILARITY_THRESHOLD = 0.45  # tune this during Day 8 testing, see notes below


@dataclass
class MatchResult:
    student_id: Optional[int]
    registration_number: Optional[str]
    similarity: float
    bbox: list


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a, b))


def load_registered_embeddings(db: Session) -> dict[int, np.ndarray]:
    """Load all registered students' embeddings once per request."""
    students = db.query(Student).all()
    return {
        s.id: np.array(json.loads(s.embedding), dtype=np.float32)
        for s in students
    }


def match_faces_to_students(
    detected_faces: list[dict],
    db: Session,
    threshold: float = SIMILARITY_THRESHOLD,
) -> list[MatchResult]:
    """
    detected_faces: output of Member 1's recognize_classroom_faces()
    Returns one MatchResult per detected face (student_id=None => Unknown).
    """
    registered = load_registered_embeddings(db)
    students_by_id = {s.id: s for s in db.query(Student).all()}

    results = []
    for face in detected_faces:
        face_emb = np.array(face["embedding"], dtype=np.float32)

        best_id, best_sim = None, -1.0
        for student_id, reg_emb in registered.items():
            sim = cosine_similarity(face_emb, reg_emb)
            if sim > best_sim:
                best_id, best_sim = student_id, sim

        if best_sim >= threshold:
            reg_number = students_by_id[best_id].registration_number
            results.append(MatchResult(best_id, reg_number, best_sim, face.get("bbox", [])))
        else:
            # Below threshold -> Unknown. Still record the best similarity
            # for debugging/threshold-tuning purposes.
            results.append(MatchResult(None, None, best_sim, face.get("bbox", [])))

    return results


def dedupe_matches(matches: list[MatchResult]) -> dict[int, MatchResult]:
    """
    Same student can be detected twice (e.g. two overlapping boxes).
    Keep only the highest-similarity match per student_id.
    Unknown faces (student_id=None) are dropped here - they don't count
    toward present/absent, just toward the "unknown faces detected" count.
    """
    best_by_student: dict[int, MatchResult] = {}
    for m in matches:
        if m.student_id is None:
            continue
        existing = best_by_student.get(m.student_id)
        if existing is None or m.similarity > existing.similarity:
            best_by_student[m.student_id] = m
    return best_by_student