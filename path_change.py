import os
import re

# 📂 Dossier à parcourir
folder_path = r"C:\Users\rakot\Documents\4PROJ_Ete\project\front"

# Extensions de fichiers à traiter
extensions = ['.js', '.jsx', '.tsx']

# 🎯 Regex axios déjà avec API_URL mais en quotes
axios_api_pattern = re.compile(r"axios\.(get|post|put|delete)\(['\"]\$\{API_URL\}(/[^'\"]*)['\"]\)")

# 🎯 Regex axios sans API_URL (ex: axios.get('/users'))
axios_plain_pattern = re.compile(r"axios\.(get|post|put|delete)\(['\"](/[^'\"]*)['\"]\)")

# 🎯 Regex fetch déjà avec API_URL
fetch_api_pattern = re.compile(r"fetch\(['\"]\$\{API_URL\}(/[^'\"]*)['\"]\)")

# 🎯 Regex fetch sans API_URL
fetch_plain_pattern = re.compile(r"fetch\(['\"](/[^'\"]*)['\"]\)")

# 🔄 Remplacements
def replace_axios_api(match):
    method, endpoint = match.groups()
    return f"axios.{method}(`${{API_URL}}{endpoint}`)"

def replace_axios_plain(match):
    method, endpoint = match.groups()
    return f"axios.{method}(`${{API_URL}}{endpoint}`)"

def replace_fetch_api(match):
    endpoint = match.group(1)
    return f"fetch(`${{API_URL}}{endpoint}`)"

def replace_fetch_plain(match):
    endpoint = match.group(1)
    return f"fetch(`${{API_URL}}{endpoint}`)"

# 🚀 Parcours des fichiers
for root, _, files in os.walk(folder_path):
    for file in files:
        if any(file.endswith(ext) for ext in extensions):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            new_content = axios_api_pattern.sub(replace_axios_api, new_content)
            new_content = axios_plain_pattern.sub(replace_axios_plain, new_content)
            new_content = fetch_api_pattern.sub(replace_fetch_api, new_content)
            new_content = fetch_plain_pattern.sub(replace_fetch_plain, new_content)

            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Modifié : {file_path}")

print("🔁 Conversion axios + fetch terminée.")
