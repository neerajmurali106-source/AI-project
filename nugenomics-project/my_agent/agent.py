from google.adk.agents import LlmAgent
from .agents import nugen_agent 
from .agents import well_agent 

router_agent = LlmAgent(
    name="nugenomics_hybrid_agent",
    model="gemini-2.5-flash",
    description=(
        "A unified Nugenomics assistant that intelligently routes queries "
        "to the correct sub-agent. It combines company-specific support (nugen_agent) "
        "and general genetic wellness guidance (well_agent)."
    ),
    instruction=(
        "You are the main Nugenomics Hybrid Router Agent.\n"
        "→ If the question is related to Nugenomics, reports, counselling, DNA tests, "
        "rescheduling, or anything about company processes, route it to the 'nugen_agent'.\n"
        "→ If the question is about genetics, DNA, health, or wellness, route it to the 'wellagent'.\n"
        "→ If the question is unrelated to these topics, respond with: "
        "'I can only answer questions about genetics, wellness, or Nugenomics company topics.'\n\n"
        "When you respond, clearly specify which sub-agent handled the question and then show the result. "
        "Start your response from a new line after introducing the agent."
    ),
    tools=[nugen_agent, well_agent],
)


root_agent = router_agent

import asyncio
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, session_service=session_service, app_name="NuGenomicsApp")

async def ask_agent(question: str) -> str:
    """Run a query through the root_agent and return the response text."""
    try:
        result = await runner.run_once(
            user_message=question,
            user_id="web_user"
        )
        return result.output_text
    except Exception as e:
        return f"Error from agent: {e}"
