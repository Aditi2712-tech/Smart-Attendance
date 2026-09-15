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

# Register one clean image per student.
print("\nRegistering 20 students...")

for index, person in enumerate(STUDENTS, start=4):

    reg_no = f"TEST{index:03d}"
    files = sorted((DATASET / person).glob("*.jpg"))

    for file in files:
        image = cv2.imread(str(file))

        try:
            result = engine.register_student(reg_no, image)
            engine.save_embedding(reg_no, result["embedding"])
            print(f"PASS {reg_no} <- {person} ({file.name})")
            break
        except ValueError:
            continue


# Evaluate thresholds using unseen images.
thresholds = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

print("\n========================================")
print("       FINAL THRESHOLD EVALUATION")
print("========================================")

for threshold in thresholds:

    total = 0
    correct = 0

    for index, person in enumerate(STUDENTS, start=4):

        expected = f"TEST{index:03d}"
        files = sorted((DATASET / person).glob("*.jpg"))

        # 0001 is registration for most students.
        # For Junichiro and Tony, 0002 was used.
        for file in files:

            image = cv2.imread(str(file))
            faces = engine.detect_faces(image)

            if len(faces) != 1:
                continue

            result = engine.recognize_faces(
                image,
                threshold=threshold
            )

            recognized = [
                x["registration_number"]
                for x in result["recognized_students"]
            ]

            # Exclude the registration image.
            registration_embedding = engine.load_embedding(expected)
            current_embedding = faces[0].embedding

            similarity = float(
                current_embedding @ registration_embedding
                / (
                    (current_embedding @ current_embedding) ** 0.5
                    * (registration_embedding @ registration_embedding) ** 0.5
                )
            )

            if similarity > 0.9999:
                continue

            total += 1

            if expected in recognized:
                correct += 1

    accuracy = correct / total * 100 if total else 0

    print(
        f"Threshold {threshold:.1f}: "
        f"{correct}/{total} correct "
        f"({accuracy:.2f}%)"
    )

print("\n========================================")
print("Threshold evaluation complete")
print("========================================")
