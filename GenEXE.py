import subprocess
import sys
import os
import shutil

def create_exe_with_nuitka(input_file: str, exe_name: str = None):
    """
    Génère un fichier .exe à partir d'un script Python en utilisant Nuitka avec nettoyage automatique.
    
    :param input_file: Chemin vers le fichier Python source.
    :param exe_name: Nom de l'exécutable généré (facultatif).
    """
    try:
        # Vérification des prérequis
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Le fichier spécifié '{input_file}' n'existe pas.")

        # Nom par défaut pour l'exécutable
        if not exe_name:
            exe_name = os.path.splitext(os.path.basename(input_file))[0] + ".exe"
        basename=os.path.basename(input_file)
        if(basename=="server"):
        # Commande Nuitka pour la création de l'exécutable
            command = [
                sys.executable,
                "-m", "nuitka",
                "--standalone",       # Crée un exécutable autonome
                "--onefile",          # Génère un seul fichier exécutable
                "--mingw64",          # Utilise le compilateur MinGW64
                "--nofollow-imports" # Importer seullment les bib importants
            ]
        else:
             command = [
                sys.executable,
                "-m", "nuitka",
                "--standalone",       # Crée un exécutable autonome
                "--onefile",          # Génère un seul fichier exécutable
                "--mingw64",          # Utilise le compilateur MinGW64
                "--windows-disable-console", # ne pas affiche le terminal
                "--nofollow-imports*=" # Importer seullment les bib importants
            ]
        # Ajouter le fichier d'entrée
        command.append(input_file)

        # Exécuter la commande Nuitka
        print(f"Exécution de la commande : {' '.join(command)}")
        result = subprocess.run(command, text=True, capture_output=True)

        # Vérifier le statut de retour
        if result.returncode == 0:
            print("Compilation réussie.")

            # Déplacer l'exécutable généré vers le dossier courant
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
                print(f"Fichier exécutable déplacé dans le dossier courant : {exe_name}")
            else:
                print("Fichier généré introuvable.")
            
            # Nettoyer les dossiers temporaires
            for folder in ["dist", "build", "__pycache__"]:
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                    print(f"Dossier '{folder}' supprimé.")
        else:
            print(f"Erreur lors de l'exécution de Nuitka : {result.stderr}")
            print(f"Sortie standard : {result.stdout}")

    except FileNotFoundError as e:
        print(f"Erreur : {e}")
    except subprocess.SubprocessError as e:
        print(f"Erreur liée au sous-processus : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    # Exemple d'utilisation
    input_file = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\client.py"  # Modifiez ce chemin
    exe_name = "Client.exe"  # Nom de l'exécutable
    create_exe_with_nuitka(input_file, exe_name)
