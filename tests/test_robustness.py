import cv2
import numpy as np

from ai.engine import FaceEngine


engine = FaceEngine()

source = cv2.imread("dataset/student1.png")

if source is None:
    raise ValueError("Could not load dataset/student1.png")


def test_image(name, image):
    faces = engine.detect_faces(image)

    if len(faces) != 1:
        print(f"{name:25s} DETECTION FAIL ({len(faces)} faces)")
        return

    result = engine.recognize_faces(image, threshold=0.5)

    recognized = [
        r["registration_number"]
        for r in result["recognized_students"]
    ]

    unknown = len(result["unknown_faces"])

    if recognized:
        print(
            f"{name:25s} "
            f"PASS  Recognized: {recognized}"
        )
    else:
        print(
            f"{name:25s} "
            f"FAIL  Unknown faces: {unknown}"
        )


print("\n========================================")
print("       ROBUSTNESS TESTING")
print("========================================")


# 1. Original
test_image("Original", source)


# 2. Dark lighting
dark = cv2.convertScaleAbs(
    source,
    alpha=0.6,
    beta=-30
)
test_image("Dark lighting", dark)


# 3. Bright lighting
bright = cv2.convertScaleAbs(
    source,
    alpha=1.4,
    beta=30
)
test_image("Bright lighting", bright)


# 4. Rotated left
h, w = source.shape[:2]
center = (w // 2, h // 2)

matrix = cv2.getRotationMatrix2D(
    center,
    -15,
    1.0
)

rotated_left = cv2.warpAffine(
    source,
    matrix,
    (w, h)
)

test_image("Angle -15 degrees", rotated_left)


# 5. Rotated right
matrix = cv2.getRotationMatrix2D(
    center,
    15,
    1.0
)

rotated_right = cv2.warpAffine(
    source,
    matrix,
    (w, h)
)

test_image("Angle +15 degrees", rotated_right)


# 6. Smaller image / distance simulation
small = cv2.resize(
    source,
    None,
    fx=0.5,
    fy=0.5
)

canvas = np.zeros_like(source)

sh = small.shape[:2]

y = (h - sh[0]) // 2
x = (w - sh[1]) // 2

canvas[
    y:y + sh[0],
    x:x + sh[1]
] = small

test_image("Smaller face", canvas)


# 7. Blur
blurred = cv2.GaussianBlur(
    source,
    (7, 7),
    0
)

test_image("Blurred image", blurred)


print("\n========================================")
print("Robustness testing complete")
print("Threshold used: 0.5")
print("========================================")
