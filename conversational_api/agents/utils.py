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