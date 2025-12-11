import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all emojis
content = content.replace('icon="🚧"', '')
content = content.replace('"🚨 Zona de Perigo - Excluir Devedor"', '"Zona de Perigo - Excluir Devedor"')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Emojis removidos!")
