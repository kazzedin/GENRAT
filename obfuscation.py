import random
import string
import re

# Fonction pour générer des noms de variables aléatoires
def random_name(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Fonction pour obfusquer les chaînes de texte
def obfuscate_string(s):
    return ''.join([f'chr({ord(c)})+' for c in s])[:-1]

# Fonction pour obfusquer une ligne de code
def obfuscate_line(line):
    # Remplacer les noms de variables et fonctions par des noms aléatoires
    line = re.sub(r'\bdef (\w+)\b', lambda m: f'def {random_name()}', line)  # Obfuscation des fonctions
    line = re.sub(r'\b(\w+)\b', lambda m: random_name() if not m.group(1) in ['def', 'class', 'return', 'import'] else m.group(1), line)  # Obfuscation des variables
    # Obfuscation des chaînes de texte
    line = re.sub(r'"([^"]*)"', lambda m: f'"{obfuscate_string(m.group(1))}"', line)
    return line

# Fonction pour obfusquer le fichier Python
def obfuscate_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    obfuscated_lines = []
    for line in lines:
        obfuscated_lines.append(obfuscate_line(line))

    with open(output_file, 'w') as f:
        f.writelines(obfuscated_lines)

# Exemple d'utilisation
if __name__ == "__main__":
    input_file = 'client.py'  # Nom de votre fichier à obfusquer
    output_file = 'client_obfuscated.py'  # Nom du fichier obfusqué généré
    obfuscate_file(input_file, output_file)
    print(f"Le fichier obfusqué a été sauvegardé sous {output_file}")
