import requests
from bs4 import BeautifulSoup

def retrieve_policy_document_content(url: str):
    """Fetch and clean webpage text for company policy or FAQ pages."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:15000]
    except Exception as e:
        return f"Error fetching or processing the link: {e}"
