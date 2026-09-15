import cv2
import numpy as np
from pathlib import Path

from ai.engine import FaceEngine


engine = FaceEngine()

DATASET = Path("dataset/lfw_selected")

PERSON = "George_W_Bush"
IMAGE_PATH = DATASET / PERSON / "George_W_Bush_0002.jpg"


print("\n========================================")
print("       FACE DETECTION EDGE CASE TEST")
print("========================================")


image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise ValueError(
        f"Could not load {IMAGE_PATH}"
    )


# ------------------------------------------------
# ORIGINAL
# ------------------------------------------------

faces = engine.detect_faces(image)

print("\n--- ORIGINAL ---")
print("Detected faces:", len(faces))


# ------------------------------------------------
# SMALL FACE
# ------------------------------------------------

small = cv2.resize(
    image,
    None,
    fx=0.5,
    fy=0.5
)

small_path = Path(
    "dataset/edge_small.jpg"
)

cv2.imwrite(
    str(small_path),
    small
)

small_faces = engine.detect_faces(small)

print("\n--- SMALL FACE ---")
print("Detected faces:", len(small_faces))
print("Saved:", small_path)


# ------------------------------------------------
# ROTATED / ANGLED FACE
# ------------------------------------------------

height, width = image.shape[:2]

center = (
    width // 2,
    height // 2
)

matrix = cv2.getRotationMatrix2D(
    center,
    25,
    1.0
)

angled = cv2.warpAffine(
    image,
    matrix,
    (width, height)
)

angled_path = Path(
    "dataset/edge_angled.jpg"
)

cv2.imwrite(
    str(angled_path),
    angled
)

angled_faces = engine.detect_faces(
    angled
)

print("\n--- ANGLED FACE ---")
print("Detected faces:", len(angled_faces))
print("Saved:", angled_path)


# ------------------------------------------------
# PARTIALLY VISIBLE FACE
# ------------------------------------------------

partial = image.copy()

# Remove approximately the lower half
partial[
    partial.shape[0] // 2:
] = 0

partial_path = Path(
    "dataset/edge_partial.jpg"
)

cv2.imwrite(
    str(partial_path),
    partial
)

partial_faces = engine.detect_faces(
    partial
)

print("\n--- PARTIALLY VISIBLE FACE ---")
print("Detected faces:", len(partial_faces))
print("Saved:", partial_path)


# ------------------------------------------------
# SUMMARY
# ------------------------------------------------

print("\n========================================")
print("              SUMMARY")
print("========================================")

print(
    "Original:",
    len(faces)
)

print(
    "Small:",
    len(small_faces)
)

print(
    "Angled:",
    len(angled_faces)
)

print(
    "Partially visible:",
    len(partial_faces)
)

print("\nEDGE CASE TEST COMPLETE")