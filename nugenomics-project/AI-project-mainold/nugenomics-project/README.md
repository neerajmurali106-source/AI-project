🧬 Multi-Agent AI Chat Application (NuGenomics RAG + Wellness Agent)

A web-based multi-agent chat application built using the Google Agent Development Kit (ADK) and Model Context Protocol (MCP).
This project deploys two specialized AI agents — a NuGenomics Customer Support Agent grounded in the official FAQ data using Retrieval-Augmented Generation (RAG) and MCP, and a Genetic Wellness Agent that provides general health and wellness insights powered by large language models (LLMs).

Built for the AI Agent Development Challenge (Grounding & RAG Focus), July 2025.

🚀 Key Features
🧠 Dual-Agent Architecture

NuGenomics Support Agent: Answers customer queries exclusively from the official NuGenomics FAQ dataset using a RAG pipeline built with MCP-based retrieval and grounding. It cites sources and strictly avoids hallucinations.

Genetic Wellness Agent: Responds to general genetic and wellness-related questions using foundational LLM knowledge.

🤖 Google ADK Integration

Utilizes the Google Agent Development Kit (google-adk) for:

Building and structuring intelligent agents (LlmAgent, FunctionTool).

Managing multi-turn conversation state.

Handling tool execution and inter-agent communication.

🧩 Model Context Protocol (MCP) for Grounding

Implements MCP to dynamically inject grounded FAQ content into the agent’s reasoning context.

Ensures answers are always traceable, verifiable, and aligned with the source data (scraped_faqs.json).

Enables modular integration of future knowledge sources (e.g., documents, APIs).

⚙️ Retrieval-Augmented Generation (RAG)

The FAQ knowledge base is indexed, retrieved, and contextually embedded into responses.

Every FAQ-based answer cites its source from the original NuGenomics content.

🧑‍💻 Flask-Based Web Interface

A clean, web-based Flask application provides a unified interface to interact with both agents seamlessly.

🧠 Dynamic Prompt Engineering

Prompts for each agent are dynamically generated at runtime.

The NuGenomics agent’s context window is built from live FAQ retrievals.

The Manager (router) agent uses FAQ question patterns for accurate query routing.

🔁 Stateful Multi-Agent Conversations

Leverages InMemorySessionService from ADK to maintain consistent, isolated conversation history per agent session.

🏗️ Development Process & Role
My Role as Developer and System Architect

I served as the lead architect and developer, responsible for designing, implementing, and integrating the multi-agent architecture with ADK + MCP + Flask.

Key Responsibilities:

System Design: Defined roles for each agent and the overall multi-agent pipeline.

MCP + RAG Integration: Implemented FAQ-based retrieval and grounding using MCP.

Agent Implementation: Created and configured the LlmAgent instances with tool-calling via FunctionTool.

Prompt Engineering: Developed highly structured, dynamic prompts for accurate responses.

Integration & Testing: Connected Flask frontend with ADK backend and validated all routing, retrieval, and grounding logic.

🧠 AI Tools & Assistance

GitHub Copilot: For code scaffolding and function boilerplates.

ChatGPT, Gemini, and Perplexity: For debugging and refining MCP + ADK integration logic.

Codebase-Aware AI Tools: For analyzing multi-module dependencies and optimizing RAG performance.

Setup and Installation
Clone the Repository
bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>


Create and Activate a Virtual Environment
bash
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
Install Dependencies
Create a requirements.txt file with the following content:

flask
flask_cors
python-dotenv
google-generativeai
google-adk
litellm


Then, install the dependencies:

bash
pip install -r requirements.txt
Configure Credentials
Create a file named .env in the root directory.

Add your Google API Key to it:

text
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
How to Run the Application
With the setup complete, run the Flask application from the root directory:

bash
python app.py
Open your browser and navigate to:

text
http://localhost:5000
Your NuGenomics Hybrid AI Assistant is now running!