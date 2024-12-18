from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import unpad
from Crypto.PublicKey import RSA
import subprocess

def decrypt_aes_key(encrypted_key_file, private_key_file):
    """Décrypte la clé AES en utilisant la clé privée RSA."""
    with open(private_key_file, 'rb') as priv_file:
        private_key = RSA.import_key(priv_file.read())

    with open(encrypted_key_file, 'rb') as key_file:
        encrypted_key = key_file.read()

    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(encrypted_key)
    return aes_key

def decrypt_and_execute(encrypted_file, aes_key):
    """Décrypte le fichier et exécute le script décrypté."""
    import time  # Ajoutez les modules nécessaires ici

    with open(encrypted_file, 'rb') as f:
        iv = f.read(16)  # Les 16 premiers octets sont le vecteur d'initialisation (IV)
        ciphertext = f.read()

    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    # Exécute le script décrypté
    exec(plaintext.decode(), {"time": time})  # Injectez le module dans le contexte d'exécution


if __name__ == "__main__":
    # Fichiers nécessaires
    encrypted_key_file = "aes_key.enc"
    private_key_file = "private_key.pem"
    encrypted_file = "client_encrypted.py.enc"

    # Étape 1 : Décrypter la clé AES
    aes_key = decrypt_aes_key(encrypted_key_file, private_key_file)

    # Étape 2 : Décrypter et exécuter le fichier
    decrypt_and_execute(encrypted_file, aes_key)
