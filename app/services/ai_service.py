# app/services/ai_service.py
from typing import List, Dict, Any

def process_classroom_image(image_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Placeholder bridge for Member 1's InsightFace/OpenCV pipeline.
    
    When Member 1 sends their AI code, replace the mock logic inside 
    this function with their actual model call:
    embeddings = insightface_model.get(image_bytes)
    matches = compare_embeddings(embeddings)
    """
    
    # Mock output simulating detected registration numbers and confidence scores
    # This keeps your backend 100% functional for testing right now!
    mock_detected_students = [
        {"reg_no": "24BCB7105", "confidence": 0.94},
        # You can add more mock reg numbers here to test multi-student cases
    ]
    
    return mock_detected_students