import cv2

from ai.engine import FaceEngine


engine = FaceEngine()

image = cv2.imread("dataset/classroom.png")

result = engine.draw_results(image)

cv2.imwrite("dataset/classroom_result.png", result)

print("Visualization test: PASS")
print("Saved: dataset/classroom_result.png")