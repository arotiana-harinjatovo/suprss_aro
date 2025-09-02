import os
import ast
import yaml

DOCUMENTATION_FILE = "DOCUMENT_TECHNIQUE.md"

# Dossiers à exclure
EXCLUDED_DIRS = {
    "__pycache__", ".env", ".git", "node_modules", "venv", ".idea", ".vscode",
    ".mypy_cache", "dist", "build", "__pypackages__", "coverage", ".pytest_cache",
    ".cache", ".tox", ".eggs", ".venv", "env", "versions"
}
EXCLUDED_FILES_PREFIX = {'.'}

# PARTIE 1 – Structure du projet
def generate_structure(root_dir):
    lines = ["## PARTIE 1 – Structure du projet\n"]
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(tuple(EXCLUDED_FILES_PREFIX))]
        level = root.replace(root_dir, "").count(os.sep)
        indent = "    " * level
        lines.append(f"{indent}- {os.path.basename(root)}/")
        for f in files:
            if f.startswith(tuple(EXCLUDED_FILES_PREFIX)) or f.endswith(".pyc"):
                continue
            lines.append(f"{indent}    - {f}")
    return "\n".join(lines)

# PARTIE 2 – Docstrings
def extract_docstrings_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    docstrings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            name = getattr(node, 'name', 'Module')
            doc = ast.get_docstring(node)
            if doc:
                docstrings.append(f"### {name}\n{doc}\n")
    return docstrings

def generate_docstrings(root_dir):
    lines = ["## PARTIE 2 – Docstrings (modules, classes, fonctions)\n"]
    for root, _, files in os.walk(root_dir):
        if any(excluded in root for excluded in EXCLUDED_DIRS):
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith(tuple(EXCLUDED_FILES_PREFIX)):
                path = os.path.join(root, file)
                lines.append(f"### Fichier: {path}\n")
                lines.extend(extract_docstrings_from_file(path))
    return "\n".join(lines)

# PARTIE 3 – Dépendances Python
def generate_dependencies(requirements_file):
    lines = ["## PARTIE 3 – Dépendances Python\n"]
    if os.path.exists(requirements_file):
        with open(requirements_file, "r") as f:
            for line in f:
                lines.append(f"- {line.strip()}")
    else:
        lines.append("Fichier requirements.txt introuvable.")
    return "\n".join(lines)

# PARTIE 4 – Configuration Docker & Services
def generate_docker_services(compose_file):
    lines = ["## PARTIE 4 – Configuration Docker & Services\n"]
    if os.path.exists(compose_file):
        with open(compose_file, "r") as f:
            compose = yaml.safe_load(f)
        services = compose.get("services", {})
        for name, config in services.items():
            lines.append(f"### {name}")
            image = config.get("image", config.get("build", {}).get("context", "N/A"))
            lines.append(f"- Image: {image}")
            ports = config.get("ports", [])
            lines.append(f"- Ports: {ports}")
            depends = config.get("depends_on", [])
            lines.append(f"- Dépendances: {depends}\n")
    else:
        lines.append("Fichier docker-compose.yml introuvable.")
    return "\n".join(lines)

# Génération du fichier complet
def generate_documentation():
    content = []
    content.append("# DOCUMENT_TECHNIQUE.md\n")
    content.append(generate_structure("."))
    content.append(generate_docstrings("."))
    content.append(generate_dependencies("requirements.txt"))
    content.append(generate_docker_services("docker-compose.yml"))

    with open(DOCUMENTATION_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(content))

    print(f"Le fichier {DOCUMENTATION_FILE} a été généré avec succès.")

# Exécution du script
generate_documentation()
