import cv2
from ai.engine import FaceEngine

engine = FaceEngine()

for person in ["Junichiro_Koizumi", "Tony_Blair"]:
    print(f"\n===== {person} =====")

    import glob
    files = sorted(glob.glob(f"dataset/lfw_selected/{person}/*.jpg"))

    for file in files:
        image = cv2.imread(file)
        faces = engine.detect_faces(image)
        print(f"{file}: {len(faces)} face(s)")
