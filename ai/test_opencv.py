import cv2

image_path = "dataset/test.jpg"

image = cv2.imread(image_path)

if image is None:
    print("ERROR: Image could not be loaded")
else:
    print("Image loaded successfully!")
    print("Image shape:", image.shape)