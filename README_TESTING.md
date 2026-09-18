# Running & Testing This Backend in VS Code

## 1. Install dependencies
```bash
pip install fastapi uvicorn sqlalchemy pandas openpyxl python-multipart numpy pytest httpx psycopg2-binary
```

## 2. Wire up the AI module
In `app/main.py`, this line assumes Member 1's code lives at `ai/recognize.py`
relative to your project root, exposing:
```python
def recognize_classroom_faces(image_path: str) -> list[dict]:
    # returns [{"embedding": [...512 floats...], "bbox": [...], "det_score": 0.9}, ...]
```
Adjust the import path if their module is named/located differently.

## 3. Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
using this 
```bash
http://localhost:8000/docs
```
- `/docs` gives you Swagger UI — the fastest way to manually test each endpoint.
- Use `0.0.0.0` (not `127.0.0.1`) so Member 3's emulator/device can reach it.
- Android emulator hits your machine at `10.0.2.2:8000`; a physical device needs your LAN IP.

## 4. Run the automated tests (Day 8)
```bash
pytest tests/test_backend.py -v
```
These use an in-memory SQLite DB and a mocked AI function, so they run in
seconds and don't need Postgres or InsightFace installed to pass. They cover:
- unregistered student → Unknown, not crash
- duplicate attendance prevented at the DB level
- two detections of the same student → deduped to one Present record
- large class (120 students) Excel export
- invalid/empty file upload → clean 4xx, not a 500

## 5. Manual tests you still need to do (can't be automated meaningfully)
Run these through `/docs` with real photos, and log similarity scores to
pick your final `SIMILARITY_THRESHOLD` in `app/recognition.py`:
- 1 / 3 / 5 / 10+ faces in a classroom photo
- different lighting conditions
- different face angles / distances
- a genuinely unknown person walking through the shot
- the same student's photo taken twice, slightly different pose

## 6. Day 9 cleanup checklist
- [ ] `grep -rn "print(" app/` → should return nothing (use `logger` instead)
- [ ] Confirm DB errors roll back and return a clean error, not a stack trace
- [ ] Confirm `DATABASE_URL` isn't hardcoded with real credentials in committed code
- [ ] Run `pytest` one more time after any last-minute changes
