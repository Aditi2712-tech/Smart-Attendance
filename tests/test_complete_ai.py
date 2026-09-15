import cv2

from ai.engine import FaceEngine


engine = FaceEngine()

image = cv2.imread("dataset/classroom.png")

result = engine.recognize_faces(image)

print("\n=== AI ATTENDANCE RESULT ===")
print("Total faces:", result["face_count"])

print("\nRecognized students:")
for student in result["recognized_students"]:
    print(
        student["registration_number"],
        "confidence:",
        round(student["confidence"], 3)
    )

print("\nUnknown faces:", len(result["unknown_faces"]))

output = engine.draw_results(image)

cv2.imwrite("dataset/classroom_result.png", output)

print("\nAnnotated image saved successfully.")
print("=== AI WORKFLOW COMPLETE ===")