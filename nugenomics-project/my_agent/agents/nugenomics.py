import asyncio
import requests
import json
from bs4 import BeautifulSoup
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, ToolContext, AgentTool
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from typing import List, Dict, Any
import difflib
import time

BASE_LINKS = [
    "https://www.nugenomics.in/faqs/"
]

FAQ_DATA: List[Dict[str, str]] = [] 


def fetch_and_process_faqs(url: str) -> List[Dict[str, str]]:
    """
    Fetches the page and simulates RAG indexing by creating chunks 
    with distinct 'source' metadata.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        qa_pairs = []

        for item in soup.find_all(["div", "section"]):
            q_div = item.find(["h2", "h3", "div"], class_=lambda x: x and "title" in x.lower())
            a_div = item.find(["div", "p"], class_=lambda x: x and ("content" in x.lower() or "text" in x.lower()))
            if q_div and a_div:
                question = q_div.get_text(strip=True)
                answer = a_div.get_text(strip=True)
                if question and answer:
                    chunk_id = f"FAQ Section {len(qa_pairs) + 1}"
                    qa_pairs.append({"source": chunk_id, "content": f"Question: {question}\nAnswer: {answer}"})

        if not qa_pairs:
            for item in soup.find_all("div", class_="elementor-accordion-item"):
                q_div = item.find("div", class_="elementor-tab-title")
                a_div = item.find("div", class_="elementor-tab-content")
                if q_div and a_div:
                    question = q_div.get_text(strip=True)
                    answer = a_div.get_text(strip=True)
                    chunk_id = f"FAQ Section {len(qa_pairs) + 1}"
                    qa_pairs.append({
                        "source": chunk_id,
                        "content": f"Question: {question}\nAnswer: {answer}"
                    })

        if not qa_pairs:
            text = soup.get_text(separator="\n", strip=True)[:30000]
            qa_pairs.append({"source": f"Raw Content ({url})", "content": text})

        print(f"✅ Extracted {len(qa_pairs)} entries from {url}")
        return qa_pairs

    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return [{"source": "Error", "content": f"Could not load content from {url}: {e}"}]


for link in BASE_LINKS:
    FAQ_DATA.extend(fetch_and_process_faqs(link))
FAQ_DATA.append({
    "source": "Manual Additions",
    "content": (
        "Question: Who is the program for?\n"
        "Answer: The program is for individuals who want to understand their genetics to improve "
        "their health, nutrition, and fitness through DNA-based insights."
    )
})

FAQ_DATA.append({
    "source": "Company Overview",
    "content": (
        "Question: What is Nugenomics?\n"
        "Answer: Nugenomics is a health and wellness company that uses DNA-based insights "
        "to create personalized nutrition, fitness, and lifestyle plans for individuals."
    )
})

print("\n🔍 Sample extracted FAQ entries:\n")
for i, item in enumerate(FAQ_DATA[:5]):
    print(f"{i+1}. {item['content'][:300]}\n")


def enhance_query(query: str) -> List[str]:
    """Adds known synonyms/keywords for better simulated 'semantic' search."""
    normalized_query = query.lower()
    search_terms = [normalized_query]

    if "report" in normalized_query or "generated" in normalized_query:
        search_terms.extend(["DNA", "combine", "analyze", "develop plan", "counselling"])

    if any(x in normalized_query for x in ["contact", "reach", "talk", "support"]):
        search_terms.extend(["email", "call", "info@nugenomics.in", "+91"])

    return list(set(search_terms))


def search_faq_text(query: str) -> str:
    """Improved version with synonym mapping and better fuzzy matching."""
    results = []
    query = query.lower()

    keyword_map = {
        "report": ["dna", "result", "test", "blood", "kit", "analysis"],
        "receive": ["get", "deliver", "result", "when", "timeline", "how long"],
        "sample": ["saliva", "collection", "kit", "send", "lab"],
        "contact": ["support", "help", "email", "phone", "call"],
        "fail": ["error", "quality", "retake", "issue"],
    }

def search_faq_text(query: str) -> str:
    """Wrapper that queries the centralized FAQ service (MCP-style cache) and formats results."""
    try:
        from ..faq_service import query_faq as _query_faq
    except Exception:
        # fallback to local import path
        from my_agent.faq_service import query_faq as _query_faq

    data = _query_faq(query)
    results = data.get('results', [])
    if not results:
        return ("The information about your query could not be found directly in our FAQ. "
                "Please contact NuGenomics support at info@nugenomics.in for help.")
    formatted = []
    for r in results:
        a = r.get('answer', '').strip()
        q = r.get('question', '').strip()
        url = r.get('url', 'https://www.nugenomics.in/faqs/')
        formatted.append(f"Question: {q}\nAnswer: {a}\nSource: {url}")
    return "\n\n".join(formatted)




STRICT_INSTRUCTION = (
    "You are a helpful and strictly grounded FAQ assistant for Nugenomics. "
    "Your ONLY source of information is the 'search_faq_text' tool. "
    "You must always call this tool first to find relevant information "
    "before answering. If the tool finds no relevant data, respond that "
    "the information is not available in the FAQ or company website."
)

search_tool = FunctionTool(search_faq_text)



nugenagent = LlmAgent(
    model="gemini-2.5-flash",
    name="nugenomics_rag_agent",
    description="An agent for grounded Nugenomics FAQs with citations.",
    instruction=STRICT_INSTRUCTION,
    tools=[search_tool],
)


async def ask_agent(question: str, retries: int = 3):
    """Ask the agent a question with automatic retry if the model is overloaded."""
    for attempt in range(1, retries + 1):
        try:
            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name=nugenagent.name,
                user_id="user_test",
                session_id="session_1"
            )

            runner = Runner(agent=nugenagent, session_service=session_service)

            async for event in runner.run(session=session, message=question):
                if event.is_final_response():
                    return event.message.text

        except Exception as e:
            if "503" in str(e) and attempt < retries:
                print(f"⚠️ Model overloaded. Retrying in {2 * attempt} seconds...")
                time.sleep(2 * attempt)
                continue
            else:
                return f"❌ Error: {e}"

    return "❌ Failed after multiple attempts."


if __name__ == "__main__":
    async def main():
        test_questions = [
            "How is my DNA report generated?",
            "When will I receive my DNA test results?",
            "How do I collect my saliva sample?",
            "What is Nugenomics?",
            "What happens if my sample fails quality check?",
            "How can I contact customer support?"
        ]

        for q in test_questions:
            print(f"\n🧠 Question: {q}")
            ans = await ask_agent(q)
            print(f"\n🤖 Answer:\n{ans}")
            print("\n" + "=" * 60 + "\n")

    asyncio.run(main())


nugen_agent = AgentTool(agent=nugenagent)