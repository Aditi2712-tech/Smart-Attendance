# Attendance System — React Native (Expo) Frontend

Mobile client for a face-recognition attendance system backed by a FastAPI
server. The backend is **not** included — it must already be running on your
computer (default port `8000`).

## 1. Point the app at your backend

`localhost` / `127.0.0.1` will NOT work from a physical device (it points at
the phone itself). Use your computer's LAN IP instead.

Find your LAN IP:

- **macOS**: `ipconfig getifaddr en0`
- **Linux**: `hostname -I`
- **Windows**: `ipconfig` → look for *IPv4 Address*

Then edit **`config.js`**:

```js
export const BASE_URL = 'http://192.168.1.42:8000'; // your LAN IP + port 8000
```

Make sure the phone/emulator and the computer are on the **same Wi-Fi
network**, and that no firewall blocks port 8000.

## 2. Install & run

```bash
npm install
npx expo start
```

Scan the QR code with the Expo Go app (Android/iOS) or press `a` / `i` to
launch an emulator.

## 3. Screens

| Tab | Function |
|---|---|
| **Register** | POST `/students/`, list all students (GET `/students/`), delete a student (DELETE `/students/{reg_no}`) with confirmation |
| **Attendance** | Take/choose photo → multipart POST `/recognize-and-mark/` (field `file`) → summary cards + color-coded logs (green = Present, red = Absent) |
| **History** | GET `/history/`, Export Excel (GET `/export-excel/{id}` → `expo-file-system` download → `expo-sharing` share), Delete session (DELETE `/history/{id}`) with confirmation |

## 4. File system note (Expo SDK 52+)

The History screen uses the classic async API
(`FileSystem.downloadAsync`). Starting with **Expo SDK 52** it is exported
from `expo-file-system/legacy`:

```js
import * as FileSystem from 'expo-file-system/legacy';
```

On SDK 51 and below, import as in this project:

```js
import * as FileSystem from 'expo-file-system';
```

## 5. Backend endpoints expected

- `POST /students/` — body `{ "reg_no": "...", "name": "..." }`
- `GET  /students/`
- `DELETE /students/{reg_no}`
- `POST /recognize-and-mark/` — multipart/form-data, field `file` →
  `{ total, present, absent, logs: [{ reg_no, name, status, confidence }] }`
- `GET  /history/` — sessions with `id, date, total, present, absent`
- `GET  /export-excel/{session_id}` — xlsx download
- `DELETE /history/{session_id}`

Errors surfaced from FastAPI `HTTPException` `detail` fields via
`Alert.alert` (see `api.js` → `getApiErrorMessage`).

## 6. Project structure

```
attendance-app/
├── App.js                    # Bottom tab navigator (Register | Attendance | History)
├── config.js                 # BASE_URL constant  ← set your LAN IP here
├── api.js                    # Axios instance + FastAPI error extractor
├── package.json
├── app.json                  # Camera/media permission strings
├── babel.config.js
├── screens/
│   ├── RegisterScreen.js
│   ├── AttendanceScreen.js
│   └── HistoryScreen.js
└── README.md
```
