import cv2
from pathlib import Path
import numpy as np


BASE = Path("dataset")


# --------------------------------------------------
# TEST001 - TEST003
# Original student images
# --------------------------------------------------

sources = {
    "TEST001": BASE / "student1.png",
    "TEST002": BASE / "student2.jpeg",
    "TEST003": BASE / "student3.png",
}


# --------------------------------------------------
# TEST004 - TEST023
# LFW identities
# --------------------------------------------------

mapping = {
    "TEST004": "Ariel_Sharon",
    "TEST005": "Arnold_Schwarzenegger",
    "TEST006": "Bill_Clinton",
    "TEST007": "Colin_Powell",
    "TEST008": "Condoleezza_Rice",
    "TEST009": "David_Beckham",
    "TEST010": "Donald_Rumsfeld",
    "TEST011": "George_W_Bush",
    "TEST012": "Gerhard_Schroeder",
    "TEST013": "Gloria_Macapagal_Arroyo",
    "TEST014": "Hugo_Chavez",
    "TEST015": "Jacques_Chirac",
    "TEST016": "Jean_Chretien",
    "TEST017": "John_Ashcroft",
    "TEST018": "John_Kerry",
    "TEST019": "Junichiro_Koizumi",
    "TEST020": "Luiz_Inacio_Lula_da_Silva",
    "TEST021": "Serena_Williams",
    "TEST022": "Tony_Blair",
    "TEST023": "Vladimir_Putin",
}


# --------------------------------------------------
# Find the correct LFW image
# --------------------------------------------------

for test_id, person in mapping.items():

    person_dir = BASE / "lfw_selected" / person

    # Junichiro and Tony Blair used 0002
    # because their 0001 images contained multiple faces.
    if test_id in ["TEST019", "TEST022"]:
        image_number = "0002"
    else:
        image_number = "0001"

    filename = f"{person}_{image_number}.jpg"

    sources[test_id] = person_dir / filename


# --------------------------------------------------
# Create 5 x 5 grid
# --------------------------------------------------

tile_width = 320
tile_height = 320

columns = 5
rows = 5

canvas = np.ones(
    (rows * tile_height, columns * tile_width, 3),
    dtype=np.uint8
) * 255


# --------------------------------------------------
# Load all images
# --------------------------------------------------

loaded = 0
failed = []


for index, (test_id, path) in enumerate(sources.items()):

    print(f"{test_id}: {path}")

    image = cv2.imread(str(path))

    if image is None:
        print(f"ERROR: Could not read {path}")
        failed.append(test_id)
        continue

    # Resize image to fit grid
    image = cv2.resize(
        image,
        (tile_width, tile_height)
    )

    # Calculate grid position
    row = index // columns
    col = index % columns

    y1 = row * tile_height
    y2 = y1 + tile_height

    x1 = col * tile_width
    x2 = x1 + tile_width

    # Place image on canvas
    canvas[y1:y2, x1:x2] = image

    # IMPORTANT:
    # No TEST001 / TEST002 labels are added here.
    # This creates a clean input image.

    loaded += 1


# --------------------------------------------------
# Save clean group image
# --------------------------------------------------

output = BASE / "group_23.png"

cv2.imwrite(
    str(output),
    canvas
)


# --------------------------------------------------
# Final report
# --------------------------------------------------

print()
print("==============================")
print("23 PERSON GROUP CREATED")
print("==============================")
print("Expected images:", len(sources))
print("Loaded images:", loaded)
print("Failed images:", failed)
print("Output:", output)