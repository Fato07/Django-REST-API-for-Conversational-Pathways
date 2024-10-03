from bs4 import BeautifulSoup
import logging
import bleach

logger = logging.getLogger(__name__)

def html_to_script(html_input):
    """
    Sanitizes and converts HTML input to plain text script.
    """
    # Sanitize the HTML to allow only certain tags
    allowed_tags = ['p', 'b', 'i', 'u', 'strong', 'em', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']
    cleaned_html = bleach.clean(html_input, tags=allowed_tags, strip=True)
    
    # Convert to plain text
    soup = BeautifulSoup(cleaned_html, 'html.parser')
    text = soup.get_text(separator='\n')  # Preserves line breaks
    return text.strip()

def clean_payload(data):
    """
    Recursively remove keys with None, empty strings, empty lists, or empty dictionaries.
    """
    if isinstance(data, dict):
        return {
            key: clean_payload(value)
            for key, value in data.items()
            if value not in [None, '', [], {}]
        }
    elif isinstance(data, list):
        return [clean_payload(item) for item in data if item not in [None, '', {}, []]]
    else:
        return data