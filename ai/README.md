# AI Face Recognition Module

## 1. Overview

This module provides the AI and Computer Vision functionality for the
AI-Powered Student Attendance Management System.

It detects faces from images, generates face embeddings, registers
students, recognizes registered students, identifies unknown faces,
and processes classroom images containing multiple people.

---

## 2. Technology Stack

- Python 3
- OpenCV
- InsightFace
- ONNX Runtime
- NumPy

The InsightFace `buffalo_l` model is used for face detection,
face alignment, and face recognition.

---

## 3. AI Pipeline

The AI pipeline is:

```text
Image
  ↓
Face Detection
  ↓
Face Alignment
  ↓
Face Embedding Generation
  ↓
Compare with Registered Embeddings
  ↓
Cosine Similarity
  ↓
Similarity Threshold
  ↓
Recognized Student / Unknown Face
  ↓
Attendance-ready Recognition Result