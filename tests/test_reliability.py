import cv2

from ai.engine import FaceEngine


engine = FaceEngine()


print("\n========================================")
print("       AI RELIABILITY TEST")
print("========================================")


# ------------------------------------------------
# TEST 1: UNKNOWN FACE
# ------------------------------------------------

print("\n--- UNKNOWN FACE TEST ---")

unknown_image = cv2.imread("dataset/unknown.png")

if unknown_image is None:
    raise ValueError("Could not load unknown.png")

unknown_result = engine.recognize_faces(
    unknown_image,
    threshold=0.5
)

print("Detected faces:", unknown_result["face_count"])
print(
    "Recognized:",
    unknown_result["recognized_students"]
)
print(
    "Unknown:",
    unknown_result["unknown_faces"]
)

if len(unknown_result["recognized_students"]) == 0:
    print("Unknown face handling: PASS")
else:
    print("Unknown face handling: FAIL")


# ------------------------------------------------
# TEST 2: HIGH THRESHOLD
# ------------------------------------------------

print("\n--- HIGH THRESHOLD TEST ---")

known_image = cv2.imread("dataset/student1.png")

if known_image is None:
    raise ValueError("Could not load student1.png")

result_high = engine.recognize_faces(
    known_image,
    threshold=0.95
)

print(
    "Recognized at threshold 0.95:",
    result_high["recognized_students"]
)

print(
    "Unknown at threshold 0.95:",
    result_high["unknown_faces"]
)


# ------------------------------------------------
# TEST 3: DIFFERENT THRESHOLDS
# ------------------------------------------------

print("\n--- THRESHOLD RELIABILITY TEST ---")

for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:

    result = engine.recognize_faces(
        known_image,
        threshold=threshold
    )

    recognized = len(
        result["recognized_students"]
    )

    unknown = len(
        result["unknown_faces"]
    )

    print(
        f"Threshold {threshold:.1f}: "
        f"Recognized={recognized}, "
        f"Unknown={unknown}"
    )


# ------------------------------------------------
# TEST 4: CLASSROOM
# ------------------------------------------------

print("\n--- CLASSROOM RELIABILITY TEST ---")

classroom = cv2.imread(
    "dataset/classroom.png"
)

if classroom is None:
    raise ValueError(
        "Could not load classroom.png"
    )

classroom_result = engine.recognize_faces(
    classroom,
    threshold=0.5
)

print(
    "Detected faces:",
    classroom_result["face_count"]
)

print(
    "Recognized students:",
    classroom_result["recognized_students"]
)

print(
    "Unknown faces:",
    len(
        classroom_result["unknown_faces"]
    )
)


print("\n========================================")
print("       RELIABILITY TEST COMPLETE")
print("========================================")