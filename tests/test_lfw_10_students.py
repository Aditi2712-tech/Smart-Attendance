import cv2
from pathlib import Path

from ai.engine import FaceEngine


# ============================================================
# LFW DATASET
# ============================================================

DATASET = Path("dataset/lfw_selected")


# Map LFW identities to project registration numbers
STUDENTS = {
    "Ariel_Sharon": "TEST004",
    "Colin_Powell": "TEST005",
    "Donald_Rumsfeld": "TEST006",
    "George_W_Bush": "TEST007",
    "Gerhard_Schroeder": "TEST008",
    "Hugo_Chavez": "TEST009",
    "Jean_Chretien": "TEST010",
    "John_Ashcroft": "TEST011",
    "Junichiro_Koizumi": "TEST012",
    "Tony_Blair": "TEST013",
}


# ============================================================
# INITIALIZE AI ENGINE
# ============================================================

engine = FaceEngine()


print("\n========================================")
print("       LFW 10-STUDENT AI TEST")
print("========================================")


# ============================================================
# STEP 1: REGISTER STUDENTS
# ============================================================

print("\n--- REGISTRATION ---")

registered_students = 0

for person, registration_number in STUDENTS.items():

    person_folder = DATASET / person

    if not person_folder.exists():
        print(f"ERROR: Dataset folder not found: {person}")
        continue

    images = sorted(person_folder.glob("*.jpg"))

    if len(images) < 2:
        print(f"ERROR: Not enough images for {person}")
        continue

    registration_image = None
    registration_path = None

    # Find an image containing exactly one face
    for image_path in images:

        image = cv2.imread(str(image_path))

        if image is None:
            continue

        faces = engine.detect_faces(image)

        if len(faces) == 1:
            registration_image = image
            registration_path = image_path
            break

    # No suitable image found
    if registration_image is None:

        print(
            f"FAIL: {person} - "
            f"no single-face registration image found"
        )

        continue

    # Register student
    student = engine.register_student(
        registration_number,
        registration_image
    )

    # Save embedding
    engine.save_embedding(
        registration_number,
        student["embedding"]
    )

    registered_students += 1

    print(
        f"PASS: {registration_number} <- {person} "
        f"({registration_path.name})"
    )


# ============================================================
# STEP 2: RECOGNITION TEST
# ============================================================

print("\n--- RECOGNITION ON UNSEEN IMAGES ---")

total_tests = 0
correct_recognitions = 0
failed_recognitions = 0

results = []


for person, registration_number in STUDENTS.items():

    person_folder = DATASET / person

    images = sorted(person_folder.glob("*.jpg"))

    if len(images) < 2:
        continue

    # The registration image is the first suitable image.
    # Test the remaining images.
    registration_path = None

    for image_path in images:

        image = cv2.imread(str(image_path))

        if image is None:
            continue

        faces = engine.detect_faces(image)

        if len(faces) == 1:
            registration_path = image_path
            break

    if registration_path is None:
        continue

    test_images = [
        image_path
        for image_path in images
        if image_path != registration_path
    ]

    for image_path in test_images:

        image = cv2.imread(str(image_path))

        if image is None:
            print(
                f"FAIL: Could not load {image_path}"
            )
            continue

        result = engine.recognize_faces(image)

        total_tests += 1

        recognized_ids = [
            item["registration_number"]
            for item in result["recognized_students"]
        ]

        # Check whether the correct student was recognized
        if registration_number in recognized_ids:

            correct_recognitions += 1
            status = "PASS"

        else:

            failed_recognitions += 1
            status = "FAIL"

        results.append({
            "person": person,
            "expected": registration_number,
            "image": image_path.name,
            "recognized": recognized_ids,
            "status": status
        })

        print(
            f"{person:22} "
            f"{image_path.name:25} "
            f"Expected: {registration_number:8} "
            f"Recognized: {recognized_ids} "
            f"[{status}]"
        )


# ============================================================
# STEP 3: CALCULATE ACCURACY
# ============================================================

if total_tests > 0:

    accuracy = (
        correct_recognitions / total_tests
    ) * 100

else:

    accuracy = 0.0


# ============================================================
# STEP 4: FINAL RESULTS
# ============================================================

print("\n========================================")
print("             FINAL RESULTS")
print("========================================")

print(
    f"Students registered : {registered_students}/"
    f"{len(STUDENTS)}"
)

print(
    f"Recognition tests   : {total_tests}"
)

print(
    f"Correct recognitions: {correct_recognitions}"
)

print(
    f"Failed recognitions : {failed_recognitions}"
)

print(
    f"Recognition accuracy: {accuracy:.2f}%"
)

print("========================================")


# ============================================================
# STEP 5: SIMPLE INTERPRETATION
# ============================================================

print("\n--- TEST INTERPRETATION ---")

if registered_students == len(STUDENTS):
    print("10-student registration: PASS")
else:
    print(
        f"10-student registration: "
        f"PARTIAL ({registered_students}/10)"
    )

if correct_recognitions == total_tests and total_tests > 0:
    print("Unseen-image recognition: PASS")
elif correct_recognitions > 0:
    print("Unseen-image recognition: PARTIAL")
else:
    print("Unseen-image recognition: FAIL")

print("\nLFW TEST COMPLETE.")