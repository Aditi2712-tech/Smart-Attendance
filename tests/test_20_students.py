import cv2
from pathlib import Path

from ai.engine import FaceEngine


DATASET = Path("dataset/lfw_selected")

STUDENTS = [
    "Ariel_Sharon",
    "Arnold_Schwarzenegger",
    "Bill_Clinton",
    "Colin_Powell",
    "Condoleezza_Rice",
    "David_Beckham",
    "Donald_Rumsfeld",
    "George_W_Bush",
    "Gerhard_Schroeder",
    "Gloria_Macapagal_Arroyo",
    "Hugo_Chavez",
    "Jacques_Chirac",
    "Jean_Chretien",
    "John_Ashcroft",
    "John_Kerry",
    "Junichiro_Koizumi",
    "Luiz_Inacio_Lula_da_Silva",
    "Serena_Williams",
    "Tony_Blair",
    "Vladimir_Putin",
]

engine = FaceEngine()

print("\n========================================")
print("     20-STUDENT REGISTRATION TEST")
print("========================================")

registration_results = {}
registration_failures = []

for index, person in enumerate(STUDENTS, start=4):

    registration_number = f"TEST{index:03d}"
    files = sorted((DATASET / person).glob("*.jpg"))

    registered = False

    for file in files:

        image = cv2.imread(str(file))

        try:
            result = engine.register_student(
                registration_number,
                image
            )

            engine.save_embedding(
                registration_number,
                result["embedding"]
            )

            registration_results[person] = registration_number

            print(
                f"PASS: {registration_number} <- "
                f"{person} ({file.name})"
            )

            registered = True
            break

        except ValueError as e:

            if "Multiple faces detected" in str(e):
                continue

            print(
                f"FAIL: {registration_number} <- "
                f"{person}"
            )
            print(f"Reason: {e}")
            break

    if not registered:
        registration_failures.append(person)

print("\n========================================")
print("       UNSEEN IMAGE RECOGNITION")
print("========================================")

total_tests = 0
correct = 0
failed = 0

for person in STUDENTS:

    registration_number = registration_results.get(person)

    if registration_number is None:
        continue

    files = sorted((DATASET / person).glob("*.jpg"))

    for file in files:

        # Find the registration image used above.
        image = cv2.imread(str(file))

        faces = engine.detect_faces(image)

        # Skip images that contain multiple faces.
        if len(faces) != 1:
            continue

        # Skip the actual registration image by checking its embedding.
        registration_embedding = engine.load_embedding(
            registration_number
        )

        current_embedding = faces[0].embedding

        similarity = float(
            current_embedding @ registration_embedding
            / (
                (current_embedding @ current_embedding) ** 0.5
                * (registration_embedding @ registration_embedding) ** 0.5
            )
        )

        # Registration image has essentially perfect similarity.
        # We need unseen images only.
        if similarity > 0.9999:
            continue

        total_tests += 1

        result = engine.recognize_faces(image)

        recognized = [
            r["registration_number"]
            for r in result["recognized_students"]
        ]

        if registration_number in recognized:
            correct += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(
            f"{person:28s} "
            f"{file.name:35s} "
            f"Expected: {registration_number} "
            f"Recognized: {recognized} "
            f"[{status}]"
        )

print("\n========================================")
print("           FINAL RESULTS")
print("========================================")

print(
    f"Students registered : "
    f"{len(registration_results)}/20"
)

print(f"Registration failures: {len(registration_failures)}")

print(f"Recognition tests   : {total_tests}")
print(f"Correct recognitions: {correct}")
print(f"Failed recognitions : {failed}")

if total_tests:
    accuracy = correct / total_tests * 100
    print(f"Recognition accuracy: {accuracy:.2f}%")
else:
    print("Recognition accuracy: N/A")

print("\nRegistration failures:")

if registration_failures:
    for person in registration_failures:
        print(f"- {person}")
else:
    print("None")

print("\n========================================")

if len(registration_results) == 20:
    print("20-student registration: PASS")
else:
    print("20-student registration: FAIL")

if failed == 0 and total_tests > 0:
    print("20-student recognition: PASS")
else:
    print("20-student recognition: FAIL")

print("20-STUDENT AI TEST COMPLETE")
print("========================================")
