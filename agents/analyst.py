from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

load_dotenv()

analyst = Agent(
    name="Analyst",
    role="Financial Data Analyst",
    model=OpenRouter(id="minimax/minimax-m2.1"),
    tools=[YFinanceTools()],
    description="Your goal is to analyze financial markets and provide data-driven insights.",
    instructions=[
        "Use YFinance to get real-time stock prices and company info.",
        "Do not hallucinate prices.",
        "Provide data in tables when possible."
    ],
    markdown=True,
)
