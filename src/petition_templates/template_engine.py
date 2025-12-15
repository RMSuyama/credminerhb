
import re

def render_template_text(template_content: str, context: dict) -> str:
    """
    Renders a text template by replacing {{key}} placeholders with values from the context dictionary.
    
    Args:
        template_content (str): The text with placeholders.
        context (dict): Dictionary where keys match the placeholder names.
        
    Returns:
        str: The rendered text.
    """
    if not template_content:
        return ""
        
    def replace_match(match):
        key = match.group(1).strip()
        # Return value from context or keep the placeholder if missing
        return str(context.get(key, f"{{{{{key}}}}}"))
        
    return re.sub(r'\{\{(.*?)\}\}', replace_match, template_content)
