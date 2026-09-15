# AI Recognition Results

## 1. Overview

The AI module uses InsightFace for face detection, face alignment,
and face embedding generation.

Cosine similarity is used to compare detected face embeddings with
registered student embeddings.

The module supports:

- Face detection
- 512-dimensional face embeddings
- Student registration
- Embedding persistence
- Face recognition
- Unknown-face handling
- Multi-face classroom recognition
- Duplicate-safe attendance-ready results
- Bounding-box visualization
- Confidence scores

---

## 2. Environment

- Python: 3.13.7
- OpenCV: 5.0.0
- NumPy: 2.5.2
- InsightFace: 1.0.1
- ONNX Runtime: 1.28.0
- Model: buffalo_l
- Execution provider: CPUExecutionProvider

The system was successfully tested on macOS.

The CUDA provider warning is expected because CUDA is not available
on the development machine. CPUExecutionProvider is used successfully.

---

## 3. Student Registration

The registration pipeline requires:

1. A valid registration number.
2. A valid image.
3. Exactly one detected face.

If no face is detected, registration fails.

If multiple faces are detected, registration fails.

This prevents ambiguous student registrations.

---

## 4. 20-Student Registration Test

Twenty selected LFW identities were used for controlled AI validation.

Registration results:

```text
Students registered : 20/20
Registration failures: 0