import cv2
import numpy as np

from ai.engine import FaceEngine


def test_face_detection():
    engine = FaceEngine()

    image = cv2.imread("dataset/student1.png")
    faces = engine.detect_faces(image)

    assert len(faces) == 1
    print("Face detection: PASS")


def test_embedding_generation():
    engine = FaceEngine()

    image = cv2.imread("dataset/student1.png")
    embeddings = engine.get_embeddings(image)

    assert len(embeddings) == 1
    assert embeddings[0].shape == (512,)

    print("Embedding generation: PASS")


def test_registration_and_persistence():
    engine = FaceEngine()

    image = cv2.imread("dataset/student1.png")

    student = engine.register_student("TEST001", image)

    engine.save_embedding(
        student["registration_number"],
        student["embedding"]
    )

    loaded = engine.load_embedding("TEST001")

    assert loaded.shape == (512,)
    assert np.allclose(student["embedding"], loaded)

    print("Registration and persistence: PASS")


def test_known_face_recognition():
    engine = FaceEngine()

    image = cv2.imread("dataset/student1.png")

    student = engine.register_student("TEST001", image)

    engine.save_embedding(
        student["registration_number"],
        student["embedding"]
    )

    # Generate embedding again from the image
    embeddings = engine.get_embeddings(image)

    result = engine.recognize_face(embeddings[0])

    assert result["registration_number"] == "TEST001"
    assert result["status"] == "recognized"

    print("Known-face recognition: PASS")


def test_unknown_face_recognition():
    engine = FaceEngine()

    image = cv2.imread("dataset/unknown.png")

    result = engine.recognize_faces(image)

    assert result["face_count"] == 1
    assert len(result["recognized_students"]) == 0
    assert len(result["unknown_faces"]) == 1

    print("Unknown-face recognition: PASS")


def test_classroom_recognition():
    engine = FaceEngine()

    image = cv2.imread("dataset/classroom.png")

    result = engine.recognize_faces(image)

    assert result["face_count"] > 1
    assert len(result["recognized_students"]) >= 1

    print("Classroom recognition: PASS")
    print("Detected faces:", result["face_count"])
    print("Recognized:", result["recognized_students"])
    print("Unknown:", len(result["unknown_faces"]))


if __name__ == "__main__":
    test_face_detection()
    test_embedding_generation()
    test_registration_and_persistence()
    test_known_face_recognition()
    test_unknown_face_recognition()
    test_classroom_recognition()

    print("\nALL AI TESTS PASSED")