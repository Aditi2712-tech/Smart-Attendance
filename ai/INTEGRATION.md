# AI Integration Contract

## Purpose

This document defines how other project modules can use the AI face
recognition module.

The AI module is responsible for:

- Face detection
- Face embeddings
- Student registration
- Face recognition
- Confidence calculation
- Unknown-face handling
- Duplicate-safe recognition results

Attendance recording, database operations, authentication, APIs, and
mobile UI are handled by the respective team members.

---

## 1. Import

```python
from ai.engine import FaceEngine