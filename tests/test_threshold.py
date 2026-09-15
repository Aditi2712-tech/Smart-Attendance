import cv2

from ai.engine import FaceEngine


engine = FaceEngine()

known_images = [
    "dataset/student1.png",
    "dataset/student2.jpeg",
    "dataset/student3.png"
]

unknown_image = cv2.imread("dataset/unknown.png")

print("\n=== THRESHOLD TEST ===")

for threshold in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:

    print(f"\nThreshold: {threshold}")

    known_count = 0

    for image_path in known_images:
        image = cv2.imread(image_path)
        result = engine.recognize_faces(image, threshold)

        if len(result["recognized_students"]) == 1:
            known_count += 1

    unknown_result = engine.recognize_faces(
        unknown_image,
        threshold
    )

    unknown_rejected = (
        len(unknown_result["recognized_students"]) == 0
    )

    print("Known students recognized:", known_count, "/ 3")
    print("Unknown correctly rejected:", unknown_rejected)

print("\n=== THRESHOLD TEST COMPLETE ===")