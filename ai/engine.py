import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


class FaceEngine:

    def __init__(self):
        self.app = FaceAnalysis(name="buffalo_l")
        self.app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

        # Directory for storing registered student embeddings
        self.embedding_dir = Path("embeddings")
        self.embedding_dir.mkdir(exist_ok=True)

    def detect_faces(self, image):
        if image is None:
            raise ValueError("Invalid image")

        faces = self.app.get(image)
        return faces

    def get_embeddings(self, image):
        faces = self.detect_faces(image)

        embeddings = []

        for face in faces:
            embeddings.append(face.embedding)

        return embeddings

    def register_student(self, registration_number, image):
        if not registration_number:
            raise ValueError("Registration number is required")

        if image is None:
            raise ValueError("Invalid image")

        faces = self.detect_faces(image)

        if len(faces) == 0:
            raise ValueError("No face detected in image")

        if len(faces) > 1:
            raise ValueError(
                "Multiple faces detected. Registration requires exactly one face"
            )

        embedding = faces[0].embedding

        return {
            "registration_number": registration_number,
            "embedding": embedding
        }

    def save_embedding(self, registration_number, embedding):
        if not registration_number:
            raise ValueError("Registration number is required")

        if embedding is None:
            raise ValueError("Embedding is required")

        embedding = np.asarray(embedding)

        if embedding.shape != (512,):
            raise ValueError("Embedding must have shape (512,)")

        file_path = self.embedding_dir / f"{registration_number}.npy"

        np.save(file_path, embedding)

        return file_path

    def load_embedding(self, registration_number):
        if not registration_number:
            raise ValueError("Registration number is required")

        file_path = self.embedding_dir / f"{registration_number}.npy"

        if not file_path.exists():
            raise FileNotFoundError(
                f"No embedding found for {registration_number}"
            )

        return np.load(file_path)

    def load_all_embeddings(self):
        embeddings = {}

        for file_path in self.embedding_dir.glob("*.npy"):
            registration_number = file_path.stem
            embeddings[registration_number] = np.load(file_path)

        return embeddings

    def recognize_face(self, embedding, threshold=0.5):
        if embedding is None:
            raise ValueError("Embedding is required")

        embedding = np.asarray(embedding)

        if embedding.shape != (512,):
            raise ValueError("Embedding must have shape (512,)")

        registered = self.load_all_embeddings()

        if not registered:
            return {
                "registration_number": None,
                "confidence": 0.0,
                "status": "unknown"
            }

        embedding_norm = np.linalg.norm(embedding)

        if embedding_norm == 0:
            raise ValueError("Invalid zero embedding")

        best_registration_number = None
        best_similarity = -1.0

        for registration_number, stored_embedding in registered.items():

            stored_norm = np.linalg.norm(stored_embedding)

            if stored_norm == 0:
                continue

            similarity = float(
                np.dot(embedding, stored_embedding)
                / (embedding_norm * stored_norm)
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_registration_number = registration_number

        if best_similarity >= threshold:
            return {
                "registration_number": best_registration_number,
                "confidence": best_similarity,
                "status": "recognized"
            }

        return {
            "registration_number": None,
            "confidence": best_similarity,
            "status": "unknown"
        }

    def recognize_faces(self, image, threshold=0.5):
        if image is None:
            raise ValueError("Invalid image")

        faces = self.detect_faces(image)

        recognized_students = []
        unknown_faces = []

        # Keep track of students already recognized
        seen_students = set()

        for face in faces:

            result = self.recognize_face(
                face.embedding,
                threshold
            )

            if result["status"] == "recognized":

                student_id = result["registration_number"]

                # Prevent duplicate attendance
                if student_id not in seen_students:
                    seen_students.add(student_id)
                    recognized_students.append(result)

            else:

                unknown_faces.append(result)

        return {
            "face_count": len(faces),
            "recognized_students": recognized_students,
            "unknown_faces": unknown_faces
        }

    def draw_results(self, image, threshold=0.5):
        if image is None:
            raise ValueError("Invalid image")

        output = image.copy()
        faces = self.detect_faces(output)

        for face in faces:

            result = self.recognize_face(
                face.embedding,
                threshold
            )

            box = face.bbox.astype(int)

            x1, y1, x2, y2 = box

            if result["status"] == "recognized":

                label = (
                    f'{result["registration_number"]} '
                    f'{result["confidence"]:.2f}'
                )

                box_color = (0, 255, 0)

            else:

                label = "Unknown"
                box_color = (0, 0, 255)

            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                box_color,
                2
            )

            cv2.putText(
                output,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                box_color,
                2
            )

        return output