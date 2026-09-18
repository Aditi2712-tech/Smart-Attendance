# # app/services/ai_service.py
# from typing import List, Dict, Any

# def process_classroom_image(image_bytes: bytes) -> List[Dict[str, Any]]:
#     """
#     Placeholder bridge for Member 1's InsightFace/OpenCV pipeline.
    
#     When Member 1 sends their AI code, replace the mock logic inside 
#     this function with their actual model call:
#     embeddings = insightface_model.get(image_bytes)
#     matches = compare_embeddings(embeddings)
#     """
    
#     # Mock output simulating detected registration numbers and confidence scores
#     # This keeps your backend 100% functional for testing right now!
#     mock_detected_students = [
#         {"reg_no": "24BCB7105", "confidence": 0.94},
#         # You can add more mock reg numbers here to test multi-student cases
#     ]
    
#     return mock_detected_students

import cv2
import numpy as np
from ai.engine import FaceEngine

# One shared instance - loading InsightFace is expensive, don't do it per-request
_engine = FaceEngine()

RECOGNITION_THRESHOLD = 0.5  # matches engine.py's own default; tune during Day 8 testing


def recognize_classroom_image(image_path: str, threshold: float = RECOGNITION_THRESHOLD) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    return _engine.recognize_faces(image, threshold)


def register_student_face(registration_number: str, image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    result = _engine.register_student(registration_number, image)
    _engine.save_embedding(registration_number, result["embedding"])
    return result

# deletion of student data
def delete_student_embedding(registration_number: str) -> bool:
    """Remove the .npy embedding file for a student. Returns True if a file was deleted."""
    file_path = _engine.embedding_dir / f"{registration_number}.npy"
    if file_path.exists():
        file_path.unlink()
        return True
    return False