import os
import subprocess

def obfuscate_script(input_file, output_dir="obfuscated_scripts", pyarmor_path="C:\\Users\\HP\\AppData\\Roaming\\Python\\Python312\\Scripts\\pyarmor.exe"):
    """
    Automates the obfuscation of a Python script using PyArmor.
    
    Parameters:
        input_file (str): Path to the Python script to obfuscate.
        output_dir (str): Directory where the obfuscated script will be saved.
        pyarmor_path (str): Path to the PyArmor executable (if not in PATH).
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"The input file '{input_file}' does not exist.")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"[*] Obfuscating '{input_file}'...")

    # Construct the PyArmor command
    cmd = f"{pyarmor_path} gen --output {output_dir} {input_file}"

    try:
        # Run the command
        subprocess.run(cmd, shell=True, check=True)
        print(f"[+] Obfuscation completed. Obfuscated file saved in '{output_dir}'.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error during obfuscation: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    script_to_obfuscate = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\packed_client.py"  # Replace with the path to your Python script
    obfuscation_output_dir = "obfuscated_scripts"

    try:
        obfuscate_script(script_to_obfuscate, obfuscation_output_dir)
    except Exception as e:
        print(f"[!] An error occurred: {e}")
