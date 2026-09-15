import cv2
import time
from statistics import mean

from ai.engine import FaceEngine


engine = FaceEngine()


print("\n========================================")
print("          AI PERFORMANCE TEST")
print("========================================")


# Test images
test_images = {
    "1 face": "dataset/student1.png",
    "3 faces": "dataset/face_count_3.jpg",
    "5 faces": "dataset/face_count_5.jpg",
    "10+ faces": "dataset/face_count_10.jpg",
    "classroom": "dataset/classroom.png",
}


# Number of repetitions
RUNS = 3


for name, image_path in test_images.items():

    image = cv2.imread(image_path)

    if image is None:
        print(f"\nERROR: Could not load {image_path}")
        continue

    print(f"\n--- {name} ---")
    print(f"Image: {image_path}")

    detection_times = []
    recognition_times = []
    total_times = []

    for i in range(RUNS):

        # Detection timing
        start = time.perf_counter()

        faces = engine.detect_faces(image)

        detection_time = time.perf_counter() - start

        detection_times.append(detection_time)


        # Recognition timing
        start = time.perf_counter()

        result = engine.recognize_faces(image)

        recognition_time = time.perf_counter() - start

        recognition_times.append(recognition_time)


        total_time = detection_time + recognition_time

        total_times.append(total_time)


    avg_detection = mean(detection_times)
    avg_recognition = mean(recognition_times)
    avg_total = mean(total_times)

    fps = 1 / avg_total if avg_total > 0 else 0


    print(f"Detected faces       : {len(faces)}")
    print(
        f"Average detection    : "
        f"{avg_detection:.4f} seconds"
    )
    print(
        f"Average recognition  : "
        f"{avg_recognition:.4f} seconds"
    )
    print(
        f"Average total        : "
        f"{avg_total:.4f} seconds"
    )
    print(
        f"Approx processing FPS: "
        f"{fps:.2f}"
    )


print("\n========================================")
print("       PERFORMANCE TEST COMPLETE")
print("========================================")