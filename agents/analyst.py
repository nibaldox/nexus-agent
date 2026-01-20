from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.yfinance import YFinanceTools
from agents.chart_tools import ChartTools
from dotenv import load_dotenv

load_dotenv()

analyst = Agent(
    name="Analyst",
    role="Financial Data Analyst",
    model=OpenRouter(id="minimax/minimax-m2.1", max_tokens=8192),
    tools=[YFinanceTools(), ChartTools()],
    description="Your goal is to analyze financial markets and provide data-driven insights.",
    instructions=[
        "Use YFinance to get real-time stock prices, company info, AND commodities/currencies.",
        "Pro Tip: If asked for commodities, try standard futures tickers (e.g., Copper usually 'HG=F', Gold 'GC=F', Oil 'CL=F').",
        "Do not refuse to answer if it's not a standard stock. Try to find the closest financial instrument.",
        "Provide data in tables when possible.",
        "If the user asks for a chart or visualization, use ChartTools to generate it.",
        "Always define specific data points for x_values and y_values when creating a chart."
    ],
    markdown=True,
)
