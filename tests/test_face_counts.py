import cv2
from pathlib import Path

from ai.engine import FaceEngine


DATASET = Path("dataset/lfw_selected")

PEOPLE = [
    "Ariel_Sharon",
    "Colin_Powell",
    "Donald_Rumsfeld",
    "George_W_Bush",
    "Gerhard_Schroeder",
    "Hugo_Chavez",
    "Jean_Chretien",
    "John_Ashcroft",
    "Junichiro_Koizumi",
    "Tony_Blair",
]


engine = FaceEngine()


def get_image(person):
    folder = DATASET / person
    images = sorted(folder.glob("*.jpg"))

    if not images:
        raise FileNotFoundError(
            f"No images found for {person}"
        )

    image = cv2.imread(str(images[0]))

    if image is None:
        raise ValueError(
            f"Could not load image: {images[0]}"
        )

    return image


def combine_faces(count):
    images = []

    for person in PEOPLE[:count]:
        image = get_image(person)

        # Resize all faces to the same size
        image = cv2.resize(image, (250, 250))

        images.append(image)

    # Arrange faces horizontally
    combined = cv2.hconcat(images)

    return combined


print("\n===================================")
print("       MULTI-FACE DETECTION TEST")
print("===================================")


test_counts = [1, 3, 5, 10]

for expected_count in test_counts:

    image = combine_faces(expected_count)

    detected_faces = engine.detect_faces(image)

    actual_count = len(detected_faces)

    if actual_count == expected_count:
        status = "PASS"
    else:
        status = "FAIL"

    print(
        f"Expected faces: {expected_count:2} | "
        f"Detected faces: {actual_count:2} | "
        f"{status}"
    )

    output_path = (
        Path("dataset")
        / f"face_count_{expected_count}.jpg"
    )

    cv2.imwrite(str(output_path), image)

    print(f"Saved test image: {output_path}")


print("\n===================================")
print("       MULTI-FACE TEST COMPLETE")
print("===================================")