import requests
import os
import re
import time

# Configuration
URL = "https://www.frigost.dev/download/Dofus%203.0/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1445474215141708056/FOb-Dr08Jn9iXgSPsFYaG8DFePb-J9tjpwFw9mY8IA5EfWoVf99XUTTnlQ9YdhOEXkBK"
STATE_FILE = "v7wX2yZ_a7B9x2D4fG1hJ6kL0mN3pQ8rS5tV.dat"

def get_remote_filename():
    try:
        response = requests.head(URL, allow_redirects=True)
        response.raise_for_status()
        content_disposition = response.headers.get("content-disposition", "")
        match = re.search(r'filename="?([^";]+)"?', content_disposition)
        if match:
            return match.group(1)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Impossible de trouver le nom de fichier dans les en-têtes.")
            return None
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Erreur lors de la vérification : {e}")
        return None

def send_discord_notification(message):
    data = {"content": message}
    try:
        requests.post(WEBHOOK_URL, json=data)
        print(f"[{time.strftime('%H:%M:%S')}] Notification Discord envoyée.")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Erreur lors de l'envoi Discord : {e}")

def main():
    print(f"Starting monitor for {URL}...")
    last_known_version = None
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_known_version = f.read().strip()

    current_filename = get_remote_filename()

    if current_filename:
        if last_known_version is None:
            last_known_version = current_filename
            with open(STATE_FILE, "w") as f:
                f.write(current_filename)
            send_discord_notification(f"✅ Monitoring started. Current version: **{current_filename}**")
        elif current_filename != last_known_version:
            send_discord_notification(f"🚨 Update detected! 🚨\nOld version: **{last_known_version}**\nNew version: **{current_filename}**")
            last_known_version = current_filename
            with open(STATE_FILE, "w") as f:
                f.write(current_filename)
        else:
            send_discord_notification(f"✅ Monitoring active. No change detected. Current version: **{current_filename}**")
            print(f"No change: {current_filename}")

if __name__ == "__main__":
    main()
