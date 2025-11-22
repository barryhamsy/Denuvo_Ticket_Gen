# Denuvo_Ticket_Gen

<img width="480" height="508" alt="image" src="https://github.com/user-attachments/assets/1b687048-b13d-429c-9d31-0dbea4b77d0d" />

A small helper tool to automate **Denuvo ticket generation** using  
`steam-ticket-generator.exe` and a per-user `configs.user.ini` file.

Instead of manually typing credentials and tickets every time, this script:
- Generates a config file for Denuvo (`configs.user.ini`)
- Auto-types into `steam-ticket-generator.exe` using `pyautogui`
- Organizes everything into a folder named after the **AppID**

---

## Features

- 🔐 **Automatic Denuvo config generation**  
  Creates/updates `configs.user.ini` for each game.

- 🎮 **Per-game folder output**  
  Every run creates/uses a folder named with the game’s **AppID**  
  (e.g. `3405690/configs.user.ini`).

- 🤖 **Auto typing into `steam-ticket-generator.exe`**  
  Uses `pyautogui` to input the generated Denuvo ticket and username.

- 👤 **Per-user setup**  
  Prompts for the username and binds the ticket to that user in the config.

- 🔎 **Automatic EXE detection**  
  Attempts to detect the target game exe name and fill it into the config.

---

## Requirements

- **OS:** Windows (required for `steam-ticket-generator.exe` and Steam)
- **Python:** 3.8+  
- **Python packages:**
  - `pyautogui`
- **Tools & accounts:**
  - `steam-ticket-generator.exe` (placed in the same folder as the script, or where the script expects it)
  - A **Steam account that owns the game** you’re generating the Denuvo ticket for
  - Steam logged in and running

Install dependencies:

```bash
pip install pyautogui

Denuvo_Ticket_Gen/
├─ DenuvoTicketGen.py
├─ steam-ticket-generator.exe
├─ configs.user.ini        # (created/updated automatically)
├─ 3405690/                # Example AppID folder (created automatically)
│  └─ configs.user.ini
└─ README.md
