import requests
import time
import os
import re

# Configuration
URL = "https://www.frigost.dev/download/Dofus%203.0/"
WEBHOOK_URL = "https://discord.com/api/webhooks/1445474215141708056/FOb-Dr08Jn9iXgSPsFYaG8DFePb-J9tjpwFw9mY8IA5EfWoVf99XUTTnlQ9YdhOEXkBK"
CHECK_INTERVAL = 300
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

def send_discord_notification(new_filename):
    data = {
        "content": f"🚨 **Update detected!** 🚨\n\nNew version: **{new_filename}**"
    }
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
            print(f"Last known version loaded: {last_known_version}")
    
    # Mode GitHub Actions (une seule exécution) ou Local (boucle infinie)
    run_once = os.environ.get('GITHUB_ACTIONS') == 'true'
    
    while True:
        current_filename = get_remote_filename()
        
        if current_filename:
            if last_known_version is None:
                print(f"[{time.strftime('%H:%M:%S')}] Initialisation avec la version : {current_filename}")
                last_known_version = current_filename
                with open(STATE_FILE, "w") as f:
                    f.write(current_filename)
            
            elif current_filename != last_known_version:
                print(f"[{time.strftime('%H:%M:%S')}] CHANGEMENT DÉTECTÉ : {last_known_version} -> {current_filename}")
                send_discord_notification(current_filename)
                
                last_known_version = current_filename
                with open(STATE_FILE, "w") as f:
                    f.write(current_filename)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Pas de changement (Version actuelle : {current_filename})")
                # Envoyer une notification Discord pour confirmer que le monitoring fonctionne
                data = {
                    "content": f"✅ **Monitoring active** ✅\n\nCurrent version: **{current_filename}**\n_No changes detected_"
                }
                try:
                    requests.post(WEBHOOK_URL, json=data)
                    print(f"[{time.strftime('%H:%M:%S')}] Status notification sent.")
                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] Error sending status: {e}")
        
        if run_once:
            break
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
