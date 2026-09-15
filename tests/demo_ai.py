import cv2
from ai.engine import FaceEngine


print("=" * 50)
print("       AI ATTENDANCE SYSTEM DEMO")
print("=" * 50)

# Initialize AI
engine = FaceEngine()

# Load classroom image
image = cv2.imread("dataset/classroom.png")

if image is None:
    raise ValueError("Could not load classroom.png")

# Run recognition
result = engine.recognize_faces(
    image,
    threshold=0.5
)

# Print results
print("\nAI RESULTS")
print("-" * 50)

print("Total faces detected:", result["face_count"])

print("\nRecognized Students:")

if result["recognized_students"]:
    for student in result["recognized_students"]:
        print(
            f"  {student['registration_number']} "
            f"(confidence: {student['confidence']:.3f})"
        )
else:
    print("  None")

print("\nUnknown Faces:")

print("  Count:", len(result["unknown_faces"]))

# Draw boxes and labels
output = engine.draw_results(
    image,
    threshold=0.5
)

# Save result
output_path = "dataset/final_ai_demo_result.jpg"

cv2.imwrite(output_path, output)

print("\nOutput saved to:")
print(output_path)

print("\n" + "=" * 50)
print("             DEMO COMPLETE")
print("=" * 50)