import cv2
from collections import Counter

from ai.engine import FaceEngine


engine = FaceEngine()

print("\n=== DUPLICATE ATTENDANCE TEST ===")

image = cv2.imread("dataset/classroom.png")

result = engine.recognize_faces(image)

recognized_ids = [
    student["registration_number"]
    for student in result["recognized_students"]
]

counts = Counter(recognized_ids)

duplicates = {
    student_id: count
    for student_id, count in counts.items()
    if count > 1
}

print("Recognized IDs:", recognized_ids)
print("Total recognized:", len(recognized_ids))
print("Duplicate IDs:", duplicates)

assert len(duplicates) == 0

print("\nDuplicate attendance prevention: PASS")