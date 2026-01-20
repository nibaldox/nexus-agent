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

load_dotenv()

manager = Team(
    name="Nexus Manager",
    members=[researcher, analyst, librarian],
    model=OpenRouter(id="minimax/minimax-m2.1"),
    description="You are Nexus Lead, the coordinator of an advanced research team. You have access to a Researcher, an Analyst, and a Librarian.",
    instructions=[
        "Your main job is to understand the user's request and delegate it to the right specialist.",
        "🔎 **Researcher**: For web search and general internet queries.",
        "📊 **Analyst**: For financial data, stock prices, and market analysis.",
        "📚 **Librarian**: For retrieving information from local PDF documents.",
        "If a request requires multiple steps (e.g., 'Check Apple stock and find recent news'), break it down and use multiple agents.",
        "Synthesize the final answer from the team's outputs.",
        f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    ],
    db=SqliteDb(db_file="agent.db", session_table="nexus_team_sessions"),
    add_history_to_context=True,
    markdown=True,
    show_members_responses=True, # Show what sub-agents say (useful for stream)
)
