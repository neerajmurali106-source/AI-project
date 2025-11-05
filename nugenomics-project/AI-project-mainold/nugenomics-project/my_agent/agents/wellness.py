from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import asyncio

# ✅ Define the agent (not wrapped in AgentTool)
well_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="genetic_wellness_agent",
    description="An agent that provides general information about genetic wellness.",
    instruction=(
        "You are a Genetic Wellness Information Agent. "
        "You provide accurate, science-based, and easy-to-understand answers "
        "to general questions about genetic wellness, DNA testing, and personalized health. "
        "If the question is unrelated to genetics, politely say that you can only answer "
        "questions about genetics and wellness."
    ),
)

# ✅ (Optional testing section — safe to remove in production)
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=well_agent.name,
        user_id="user_test",
        session_id="session_1"
    )
    runner = Runner(agent=well_agent, session_service=session_service)

    question = "How can my genes affect my sleep pattern?"
    async for event in runner.run_async(session=session, message=question):
        if event.is_final_response():
            print("🤖", event.message.text)

if __name__ == "__main__":
    asyncio.run(main())
