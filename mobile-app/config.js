/**
 * ────────────────────────────────────────────────────────────────
 *  Base URL configuration
 * ────────────────────────────────────────────────────────────────
 *  "localhost" / "127.0.0.1" will NOT work from a physical device
 *  — they would point at the phone itself, not your computer.
 *
 *  Use your machine's LAN IP instead. To find it:
 *    macOS/Linux : `ipconfig getifaddr en0`  or  `hostname -I`
 *    Windows     : `ipconfig`  (look for IPv4 Address)
 *
 *  Make sure the phone and the computer are on the SAME Wi-Fi
 *  network, then replace <YOUR_LAN_IP> below, e.g.:
 *      export const BASE_URL = 'http://192.168.1.42:8000';
 */
export const BASE_URL = 'http://<YOUR_LAN_IP>:8000';
