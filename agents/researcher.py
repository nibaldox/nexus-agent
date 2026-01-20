from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv

load_dotenv()

researcher = Agent(
    name="Researcher",
    role="Web Research Specialist",
    model=OpenRouter(id="minimax/minimax-m2.1"),
    tools=[DuckDuckGoTools()],
    description="Your goal is to find accurate and up-to-date information on the web.",
    instructions=[
        "Always cite your sources.",
        "Provide a summary of the key findings.",
        "Use DuckDuckGo to search for recent events and technical details."
    ],
    markdown=True,
)
