from agno.agent import Agent
from agno.team import Team
from agno.models.openrouter import OpenRouter
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
from datetime import datetime

# Import Specialists
from agents.researcher import researcher
from agents.analyst import analyst
from agents.librarian import librarian
from agents.visualizer import visualizer

load_dotenv()

manager = Team(
    name="Nexus Manager",
    members=[researcher, analyst, librarian, visualizer],
    model=OpenRouter(id="nvidia/nemotron-3-nano-30b-a3b:free", max_tokens=200000),
    description="You are Nexus Lead, coordinator of an advanced research team. You have access to a Researcher, an Analyst, a Librarian, and a Visualizer.",
    instructions=[
        "You are the Nexus Lead. Your only goal is to ANSWER the user's request using your team.",
        "Rule #1: Never say 'I can't do this' or forward a refusal. If one agent fails, try another.",
        "Rule #2: Be smart about routing.",
        "   - Financial/Market data -> Analyst. (If Analyst fails, use Researcher).",
        "   - General info/News -> Researcher.",
        "   - Internal documents -> Librarian.",
        "   - Charts and visualizations -> Visualizer.",
        "   - File operations -> Visualizer.",
        "Rule #3: If the Analyst says they can't find a commodity or asset, IMMEDIATELY ask the Researcher to find the price/data on the web.",
        "Do not ask the user for permission to switch agents. Just do it.",
        "Synthesize the final answer to be direct and helpful."
    ],
    db=SqliteDb(db_file="agent.db", session_table="nexus_team_sessions"),
    add_history_to_context=True,
    markdown=True,
    show_members_responses=True, # Show what sub-agents say (useful for stream)
)
