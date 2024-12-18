from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
import os

def generate_rsa_keys():
    """Generate RSA public and private keys and save them to files."""
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_key)

    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_key)

    print("RSA keys generated and saved to 'private_key.pem' and 'public_key.pem'")

def encrypt_key(aes_key):
    """Encrypt the AES key using the RSA public key."""
    with open("public_key.pem", "rb") as pub_file:
        public_key = RSA.import_key(pub_file.read())

    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_key = cipher_rsa.encrypt(aes_key)

    with open("aes_key.enc", "wb") as key_file:
        key_file.write(encrypted_key)

    print("AES key encrypted and saved to 'aes_key.enc'")

def encrypt_file(input_file, output_file, key):
    with open(input_file, 'rb') as f:
        plaintext = f.read()

    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    with open(output_file, 'wb') as f:
        f.write(cipher.iv + ciphertext)

    print(f"Encrypted {input_file} to {output_file}")

if __name__ == "__main__":
    # Generate RSA keys if not already done
    if not os.path.exists("private_key.pem") or not os.path.exists("public_key.pem"):
        generate_rsa_keys()

    # Generate a 16-byte AES key
    aes_key = get_random_bytes(16)

    # Encrypt and save the AES key securely
    encrypt_key(aes_key)

    # Encrypt the client script
    input_file = "C:\\Users\\HP\\OneDrive\\Desktop\\GENRAT\\GENRAT\\client.py"
    output_file = "client_encrypted.py.enc"
    encrypt_file(input_file, output_file, aes_key)
