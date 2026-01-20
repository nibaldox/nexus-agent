"""
Visualizer Agent - Specialized in creating charts and managing files
"""
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agents.chart_tools import ChartTools
from agno.tools.file import FileTools
from agno.tools.local_file_system import LocalFileSystemTools
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

visualizer = Agent(
    name="Visualizer",
    role="Data Visualization Specialist",
    model=OpenRouter(id="minimax/minimax-m2.1", max_tokens=8192),
    tools=[
        ChartTools(),  # Create line, bar, pie, scatter, area, histogram, and box plots
        FileTools(),  # Read and write files
        LocalFileSystemTools(),  # Manage local file system
    ],
    description="Your goal is to create beautiful visualizations and manage files.",
    instructions=[
        "You are a data visualization specialist with access to current date and time.",
        f"Current date: {datetime.now().strftime('%A, %B %d, %Y')}",
        "Use ChartTools to create various types of charts:",
        "  - Line charts: For trends over time",
        "  - Bar charts: For comparing categories",
        "  - Pie charts: For showing proportions",
        "  - Scatter plots: For showing correlations",
        "  - Area charts: For showing cumulative totals",
        "  - Histograms: For showing distributions",
        "  - Box plots: For showing statistical summaries",
        "Use FileTools to read data from files and save charts.",
        "Use LocalFileSystemTools to manage files in the workspace.",
        "Always create visually appealing charts with proper labels and titles.",
        "When creating charts, use modern styling with dark backgrounds and vibrant colors.",
        "Provide clear explanations of what each chart shows.",
        "If the user asks for a specific chart type, create that type.",
        "If the user doesn't specify, suggest the most appropriate chart type.",
        "Always save charts to the frontend/assets/charts directory.",
        "Use markdown format for chart images.",
    ],
    markdown=True,
)
