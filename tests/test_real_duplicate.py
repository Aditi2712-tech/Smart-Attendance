import cv2
from collections import Counter

from ai.engine import FaceEngine


engine = FaceEngine()

print("\n=== REAL DUPLICATE STUDENT TEST ===")


# Load the same student's image twice
image = cv2.imread("dataset/student1.png")

if image is None:
    raise ValueError("Could not load student1.png")


# Create an image containing the same student twice
image = cv2.resize(image, (300, 300))

duplicate_image = cv2.hconcat([
    image,
    image
])


# Recognize both faces
result = engine.recognize_faces(duplicate_image)


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


print("Detected faces:", result["face_count"])
print("Recognized IDs:", recognized_ids)
print("ID counts:", dict(counts))
print("Duplicate IDs:", duplicates)


# We expect the same student to appear only once
assert len(recognized_ids) == 1

assert recognized_ids[0] == "TEST001"

assert len(duplicates) == 0


print("\nReal duplicate prevention: PASS")