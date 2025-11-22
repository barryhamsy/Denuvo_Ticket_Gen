import os
import shutil
import subprocess
import time
import requests
import threading
import webview

def fetch_exe_name(appid):
    url = f"https://api.steamcmd.net/v1/info/{appid}"
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if data["data"] and str(appid) in data["data"]:
            info = data["data"][str(appid)]
            exe_name = info.get('common', {}).get('exe')
            if exe_name:
                return exe_name
            launch = info.get('config', {}).get('launch')
            if launch and isinstance(launch, dict):
                for k, v in launch.items():
                    if isinstance(v, dict) and 'executable' in v:
                        return v['executable']
        return None
    except Exception:
        return None


def update_coldclient_ini(ini_path, appid, exe_name):
    if not os.path.exists(ini_path):
        return False

    lines = []
    found_appid = False
    found_exe = False

    with open(ini_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("AppId="):
                lines.append(f"AppId={appid}\n")
                found_appid = True
            elif line.strip().startswith("Exe="):
                lines.append(f"Exe={exe_name}\n")
                found_exe = True
            else:
                lines.append(line)

    if not found_appid:
        lines.append(f"AppId={appid}\n")
    if not found_exe:
        lines.append(f"Exe={exe_name}\n")

    with open(ini_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


def update_user_ini(ini_path, username):
    """
    Ensure account_name={username} exists under [user::general].
    """
    if not os.path.exists(ini_path):
        return False

    lines = []
    found_section = False
    found_account = False

    with open(ini_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.lower() == "[user::general]":
                found_section = True
                lines.append(line)
                continue
            if stripped.startswith("account_name="):
                lines.append(f"account_name={username}\n")
                found_account = True
            else:
                lines.append(line)

    if found_section and not found_account:
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if line.strip().lower() == "[user::general]":
                new_lines.append(f"account_name={username}\n")
        lines = new_lines

    if not found_section:
        lines.append("\n[user::general]\n")
        lines.append(f"account_name={username}\n")

    with open(ini_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


class Api:
    def automate(self, appid, username):
        try:
            if not appid.isdigit():
                return {"ok": False, "msg": "AppID must be a number."}
            if not username:
                return {"ok": False, "msg": "Username cannot be empty."}

            working_dir = os.path.dirname(os.path.abspath(__file__))
            base_folder = os.path.join(working_dir, "Base")
            parent_folder = working_dir
            ticket_generator_exe = os.path.join(working_dir, "steam-ticket-generator.exe")

            if not os.path.exists(base_folder):
                return {"ok": False, "msg": f"Base folder not found at {base_folder}"}
            if not os.path.exists(ticket_generator_exe):
                return {"ok": False, "msg": f"Cannot find {ticket_generator_exe}"}

            new_folder = os.path.join(parent_folder, appid)

            # Step 1: Copy Base folder to AppID folder
            if os.path.exists(new_folder):
                shutil.rmtree(new_folder)
            shutil.copytree(base_folder, new_folder)

            # Step 2: Run ticket generator
            def run_ticket():
                proc = subprocess.Popen(
                    [ticket_generator_exe],
                    cwd=working_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                time.sleep(1.7)
                import pyautogui
                pyautogui.typewrite(str(appid))
                pyautogui.press('enter')
                time.sleep(1)
                pyautogui.typewrite("yes")
                pyautogui.press('enter')
                proc.wait(timeout=20)

            t = threading.Thread(target=run_ticket)
            t.start()
            t.join(timeout=30)

            # Step 3: Move configs.user.ini to new AppID/steam_settings
            src_ini = os.path.join(working_dir, "configs.user.ini")
            dst_settings = os.path.join(new_folder, "steam_settings")
            os.makedirs(dst_settings, exist_ok=True)
            dst_ini = os.path.join(dst_settings, "configs.user.ini")

            waited = 0
            while not os.path.exists(src_ini) and waited < 10:
                time.sleep(0.5)
                waited += 0.5

            if os.path.exists(src_ini):
                shutil.move(src_ini, dst_ini)
            else:
                found_path = None
                for search_dir in [working_dir, base_folder]:
                    for root, dirs, files in os.walk(search_dir):
                        if "configs.user.ini" in files:
                            found_path = os.path.join(root, "configs.user.ini")
                            break
                    if found_path:
                        break
                if found_path:
                    shutil.move(found_path, dst_ini)
                else:
                    return {"ok": False, "msg": "configs.user.ini not found."}

            # Step 4: Inject account_name
            if not update_user_ini(dst_ini, username):
                return {"ok": False, "msg": "Failed to add account_name to configs.user.ini."}

            # Step 5: Update ColdClientLoader.ini
            exe_name = fetch_exe_name(appid)
            coldclient_ini = os.path.join(new_folder, "ColdClientLoader.ini")
            if not exe_name or not update_coldclient_ini(coldclient_ini, appid, exe_name):
                return {"ok": False, "msg": "Failed to update ColdClientLoader.ini."}

            return {"ok": True, "msg": f"Completed for AppID {appid} (user: {username})."}
        except Exception as e:
            return {"ok": False, "msg": f"Error: {e}"}


def start_webview():
    api = Api()
    window = webview.create_window(
        "Steam Ticket Automation",
        html=HTML,
        js_api=api,
        width=500, height=520,
        min_size=(500, 520),
        resizable=False
    )
    webview.start()


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Steam Ticket Automation</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { background: #181c24; color: #fff; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
    .main { max-width: 400px; margin: 50px auto 0; background: #232736; border-radius: 18px; box-shadow: 0 4px 32px #0005; padding: 36px 32px 30px 32px; }
    h2 { text-align: center; margin-bottom: 20px; color: #7ecfff; }
    label { font-weight: bold; display: block; margin-bottom: 8px; margin-top: 18px; color: #b9f; }
    input[type="text"] {
      width: 100%; border: none; border-radius: 9px;
      padding: 12px; font-size: 1.1rem; margin-bottom: 14px;
      background: #151822; color: #e3e7ee;
    }
    button {
      width: 100%; padding: 13px; border-radius: 9px; border: none;
      font-size: 1.1rem; background: #40d16f;
      color: #fff; font-weight: 600; cursor: pointer; transition: 0.2s;
    }
    button:hover { background: #2eb357; }
    .status { text-align: center; margin-top: 18px; font-size: 1.08em; }
    .ok { color: #7ecfff; }
    .fail { color: #fd6060; }
  </style>
</head>
<body>
  <div class="main">
    <h2>Steam Ticket Automation</h2>
    <label for="username">Enter Steam Username</label>
    <input id="username" type="text" maxlength="64" autocomplete="off" placeholder="e.g. suga_player" />

    <label for="appid">Enter Steam AppID</label>
    <input id="appid" type="text" maxlength="12" autocomplete="off" placeholder="e.g. 1091500" />

    <button onclick="runAutomation()" id="runBtn">Run Automation</button>
    <div id="status" class="status"></div>
  </div>

  <script>
    function setStatus(msg, ok) {
      var s = document.getElementById("status");
      s.innerText = msg;
      s.className = "status " + (ok ? "ok" : "fail");
    }
    function disableBtn(disabled) {
      document.getElementById("runBtn").disabled = disabled;
    }
    async function runAutomation() {
      var appid = document.getElementById("appid").value.trim();
      var username = document.getElementById("username").value.trim();
      if (!appid.match(/^\\d+$/)) {
        setStatus("Please enter a valid numeric AppID.", false);
        return;
      }
      if (!username) {
        setStatus("Please enter your Steam username.", false);
        return;
      }
      setStatus("Processing, please wait...", true);
      disableBtn(true);
      let res = await window.pywebview.api.automate(appid, username);
      setStatus(res.msg, res.ok);
      disableBtn(false);
    }
  </script>
</body>
</html>
"""

if __name__ == '__main__':
    start_webview()
