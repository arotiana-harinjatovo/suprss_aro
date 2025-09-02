import markdown

with open("PARTIE_1_STRUCTURE.md", "r", encoding="utf-8") as f:
    contenu_md = f.read()

html = markdown.markdown(contenu_md)

with open("structure.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Fichier HTML généré : structure.html")
