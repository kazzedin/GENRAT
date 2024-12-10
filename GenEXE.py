import subprocess
import sys
import os

# Fonction pour générer un fichier .exe à partir d'un script Python
def create_exe(input_file):
    try:
        # Vérifiez si PyInstaller est installé, sinon installez-le
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

        # Commande PyInstaller pour créer l'exécutable
        command = [
            sys.executable, 
            "-m", "PyInstaller", 
            "--onefile",   # Crée un fichier exécutable unique
            "--noconsole", # Supprime la fenêtre de console si c'est une application GUI
            input_file     # Le script Python que vous souhaitez convertir
        ]

        # Exécuter la commande PyInstaller
        subprocess.check_call(command)

        print(f"L'exécutable a été généré avec succès à partir de {input_file} !")

    except subprocess.CalledProcessError as e:
        print(f"Une erreur est survenue lors de l'exécution de PyInstaller: {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Nom du fichier Python que vous souhaitez transformer en .exe
    input_file = "client.py"  # Remplacez par votre fichier .py
    create_exe(input_file)
