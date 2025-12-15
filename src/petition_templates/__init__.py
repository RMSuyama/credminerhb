
# Petition Templates Package
from .template_engine import render_template_text

def get_all_petition_types():
    return [
        {"name": "Procuração Ad Judicia", "content": "Template Content...", "description": "Modelo Padrão"},
        {"name": "Substabelecimento", "content": "Template Content...", "description": "Com reservas de poderes"}
    ]
