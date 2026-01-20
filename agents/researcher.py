from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.websearch import WebSearchTools
from agno.tools.website import WebsiteTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.exa import ExaTools
from agno.tools.arxiv import ArxivTools
from agno.tools.newspaper import NewspaperTools
from agents.serper_tools import SerperTools

import os
from dotenv import load_dotenv
load_dotenv()

researcher = Agent(
    name="Researcher",
    role="Web Research Specialist",
    model=OpenRouter(id="nvidia/nemotron-3-nano-30b-a3b:free", max_tokens=8192),
    tools=[
        DuckDuckGoTools(),
        WebSearchTools(backend="auto"),  # Auto-selects best available backend (Google, Bing, Brave, etc.)
        WebsiteTools(),  # Scrape and read website content
        HackerNewsTools(),  # Search Hacker News for tech news
        ExaTools(api_key=os.getenv("EXA_API_KEY")),  # AI-powered search with categories
        ArxivTools(),  # Search scientific papers
        NewspaperTools(),  # Extract articles from news websites
        SerperTools(api_key=os.getenv("SERPER_API_KEY")),  # Google search via Serper.dev
    ],
    description="Your goal is to find accurate and up-to-date information on the web.",
    instructions=[
        "You are the universal information finder with access to multiple search engines and specialized databases.",
        "Primary: Use DuckDuckGo for fast, private searches.",
        "Secondary: Use WebSearchTools with auto backend for broader search (Google, Bing, Brave, Yandex, Yahoo).",
        "For Google search with rich results: Use SerperTools (via Serper.dev).",
        "For detailed website content: Use WebsiteTools to scrape and read full pages.",
        "For tech/startup news: Use HackerNewsTools.",
        "For AI-powered search with categories (news, research, company, etc.): Use ExaTools.",
        "For scientific papers and academic research: Use ArxivTools.",
        "For news articles from specific websites: Use NewspaperTools.",
        "If the Analyst or others fail to find data (like specific commodity prices or obscure facts), YOU find it.",
        "Always cite your sources and be concise."
    ],
    markdown=True,
)
