from fastmcp import FastMCP
from difflib import SequenceMatcher
import requests
from bs4 import BeautifulSoup
import re

# Initialize MCP server
mcp = FastMCP("NuGenomics FAQ MCP Server")

FAQ_URL = "https://www.nugenomics.in/faqs/"
_cached_faqs = []


def get_all_faqs_local():
    """
    Scrape FAQs from the NuGenomics FAQ page (Elementor accordion layout).
    Returns a list of {'question': ..., 'answer': ...} dictionaries.
    """
    global _cached_faqs

    # Return from cache if already loaded
    if _cached_faqs:
        return _cached_faqs

    try:
        response = requests.get(FAQ_URL, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching FAQ page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    faqs = []
    # The current NuGenomics FAQ page uses Elementor accordion layout
    faq_blocks = soup.select("div.elementor-accordion-item")

    for block in faq_blocks:
        question_el = block.select_one(".elementor-tab-title")
        answer_el = block.select_one(".elementor-tab-content")

        if question_el and answer_el:
            q = question_el.get_text(strip=True)
            a = answer_el.get_text(strip=True)
            if q and a:
                faqs.append({"question": q, "answer": a})

    _cached_faqs = faqs
    print(f"✅ Loaded {len(faqs)} FAQs from site.")
    return faqs



def compute_similarity(a: str, b: str) -> float:
    """Combines character and word overlap similarity."""
    a_clean = re.sub(r'[^a-z0-9 ]', '', a.lower())
    b_clean = re.sub(r'[^a-z0-9 ]', '', b.lower())

    # Sequence-based similarity
    seq_ratio = SequenceMatcher(None, a_clean, b_clean).ratio()

    # Word overlap similarity
    set_a = set(a_clean.split())
    set_b = set(b_clean.split())
    word_overlap = len(set_a & set_b) / max(len(set_a | set_b), 1)

    return (0.6 * seq_ratio) + (0.4 * word_overlap)



@mcp.resource("faq://{query}")
async def search_faq(query: str):
    """
    Searches the FAQ list using fuzzy string + word overlap matching.
    Returns the most relevant question and answer if similarity > 0.35.
    """
    faqs = get_all_faqs_local()
    if not faqs:
        return []

    best_match = None
    best_ratio = 0.0

    # Loop through each FAQ and find the best match
    for faq in faqs:
        ratio = compute_similarity(query, faq["question"])
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = faq

    # Return only if a good enough match was found
    if best_ratio > 0.35 and best_match:
        return [{
            "question": best_match["question"],
            "answer": best_match["answer"],
            "match_score": round(best_ratio, 2)
        }]
    else:
        return []


if __name__ == "__main__":
    print("🚀 NuGenomics FAQ MCP Server running...")
    print(f"🔗 FAQ Source: {FAQ_URL}")
    print("🧠 Resource available: faq://{query}")
    mcp.run(transport="stdio")
