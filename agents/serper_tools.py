"""
Serper.dev Search Tools for Agno
Custom toolkit for searching the web using Serper.dev API
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Any
from agno.tools import Toolkit
from agno.utils.log import log_info, logger
import requests


class SerperTools(Toolkit):
    """Search the web using Serper.dev API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_search: bool = True,
        enable_news: bool = False,
        **kwargs,
    ):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            logger.warning("No Serper API key provided")

        tools: List[Any] = []
        if enable_search:
            tools.append(self.search_web)
        if enable_news:
            tools.append(self.search_news)

        super().__init__(name="serper_tools", tools=tools, **kwargs)

    def search_web(self, query: str, num_results: int = 10) -> str:
        """
        Search the web using Serper.dev API.

        Args:
            query (str): The search query.
            num_results (int): Number of results to return (default: 10).

        Returns:
            str: Formatted search results with titles, links, and snippets.
        """
        try:
            if not self.api_key:
                return "Please provide a SERPER_API_KEY"
            if not query:
                return "Please provide a query to search for"

            log_info(f"Searching Serper for: {query}")

            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": num_results
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            results = response.json()

            # Format results for better readability
            if not results.get("organic"):
                return f"No results found for: {query}"

            formatted_results = []
            for i, item in enumerate(results.get("organic", [])[:num_results], 1):
                formatted_results.append({
                    "position": i + 1,
                    "title": item.get("title", "N/A"),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "N/A")
                })

            # Add knowledge graph if available
            kg = results.get("knowledgeGraph", {})
            if kg:
                formatted_results.append({
                    "type": "knowledge_graph",
                    "title": kg.get("title", ""),
                    "description": kg.get("description", ""),
                    "type": kg.get("type", "")
                })

            # Add related questions if available
            for q in results.get("peopleAlsoAsk", [])[:3]:
                formatted_results.append({
                    "type": "related_question",
                    "question": q.get("question", "")
                })

            return json.dumps(formatted_results, indent=2, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            return f"Error searching Serper: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def search_news(self, query: str, num_results: int = 10) -> str:
        """
        Search for news using Serper.dev API.

        Args:
            query (str): The search query.
            num_results (int): Number of results to return (default: 10).

        Returns:
            str: Formatted news results with titles, links, and snippets.
        """
        try:
            if not self.api_key:
                return "Please provide a SERPER_API_KEY"
            if not query:
                return "Please provide a query to search for"

            log_info(f"Searching Serper News for: {query}")

            url = "https://google.serper.dev/news"
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": num_results
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            results = response.json()

            # Format results for better readability
            if not results.get("news"):
                return f"No news found for: {query}"

            formatted_results = []
            for i, item in enumerate(results.get("news", [])[:num_results], 1):
                formatted_results.append({
                    "position": i,
                    "title": item.get("title", "N/A"),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "N/A"),
                    "date": item.get("date", ""),
                    "source": item.get("source", "")
                })

            return json.dumps(formatted_results, indent=2, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            return f"Error searching Serper News: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def get_current_date(self) -> str:
        """
        Get the current date and time.

        Returns:
            str: Current date and time information.
        """
        try:
            now = datetime.now()
            return f"Current date and time: {now.strftime('%A, %B %d, %Y at %I:%M %p')} (UTC: {now.utcnow().strftime('%Y-%m-%d %H:%M:%S')})"
        except Exception as e:
            return f"Error getting current date: {str(e)}"
