"""
Chart Tools for Agno - Advanced Visualization Toolkit
Creates various types of charts with modern styling
"""
import matplotlib
matplotlib.use('Agg')  # Prevent GUI blocking
import matplotlib.pyplot as plt
import numpy as np
import os
import uuid
from agno.tools import Toolkit
from agno.utils.log import log_info

class ChartTools(Toolkit):
    """Advanced chart creation toolkit with multiple chart types and modern styling."""

    def __init__(self, charts_dir: str = "frontend/assets/charts"):
        super().__init__(name="chart_tools")
        self.charts_dir = charts_dir
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)

        self.register(self.create_chart)
        self.register(self.create_scatter_plot)
        self.register(self.create_area_chart)
        self.register(self.create_histogram)
        self.register(self.create_box_plot)

    def create_chart(self, type: str, title: str, x_values: list, y_values: list,
                   x_label: str = "", y_label: str = "", color: str = None) -> str:
        """
        Generates a chart (line, bar, or pie) and returns a Markdown image link.

        :param type: 'line', 'bar', or 'pie'
        :param title: Title of the chart
        :param x_values: List of labels/values for X axis
        :param y_values: List of values for Y axis
        :param x_label: Label for X axis
        :param y_label: Label for Y axis
        :param color: Custom color for the chart
        :return: Markdown string displaying the chart
        """
        try:
            # Data Validation: Ensure lengths match
            if len(x_values) != len(y_values):
                min_len = min(len(x_values), len(y_values))
                x_values = x_values[:min_len]
                y_values = y_values[:min_len]

            plt.figure(figsize=(12, 7))

            # Modern dark theme
            plt.style.use('dark_background')
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')

            # Color palette
            if color is None:
                if type.lower() == 'line':
                    color = '#00E0FF'
                elif type.lower() == 'bar':
                    color = '#D946EF'
                elif type.lower() == 'pie':
                    color = '#00E0FF'
            else:
                color = color

            if type.lower() == 'line':
                ax.plot(x_values, y_values, marker='o', color=color, linewidth=2.5, markersize=8)
                ax.fill_between(x_values, y_values, alpha=0.3, color=color)
            elif type.lower() == 'bar':
                bars = ax.bar(x_values, y_values, color=color, edgecolor='white', linewidth=1.5, alpha=0.8)
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}', ha='center', va='bottom', color='white', fontsize=9)
            elif type.lower() == 'pie':
                colors = ['#00E0FF', '#D946EF', '#FF8A00', '#F0F0F0', '#00FF7F', '#9B59B6']
                wedges, texts, autotexts = ax.pie(y_values, labels=x_values, autopct='%1.1f%%',
                                              colors=colors, startangle=90, explode=[0.05]*len(y_values))
                for text in texts + autotexts:
                    text.set_color('white')
                    text.set_fontsize(10)

            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            if type.lower() != 'pie':
                ax.set_xlabel(x_label, color='white', fontsize=12)
                ax.set_ylabel(y_label, color='white', fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.3, color='gray')
                ax.tick_params(colors='white', labelsize=10)

            # Save
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()

            log_info(f"Created {type} chart: {title}")
            return f"\n![{title}](assets/charts/{filename})\n"

        except Exception as e:
            plt.close()
            return f"Error creating chart: {str(e)}"

    def create_scatter_plot(self, title: str, x_values: list, y_values: list,
                         x_label: str = "", y_label: str = "", color: str = '#FF6B6B') -> str:
        """Create a scatter plot with modern styling."""
        try:
            plt.figure(figsize=(12, 7))
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')

            scatter = ax.scatter(x_values, y_values, c=color, s=100, alpha=0.7, edgecolors='white', linewidth=1.5)
            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel(x_label, color='white', fontsize=12)
            ax.set_ylabel(y_label, color='white', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray')
            ax.tick_params(colors='white', labelsize=10)

            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()

            log_info(f"Created scatter plot: {title}")
            return f"\n![{title}](assets/charts/{filename})\n"

        except Exception as e:
            plt.close()
            return f"Error creating scatter plot: {str(e)}"

    def create_area_chart(self, title: str, x_values: list, y_values: list,
                       x_label: str = "", y_label: str = "", color: str = '#00E0FF') -> str:
        """Create an area chart with modern styling."""
        try:
            plt.figure(figsize=(12, 7))
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')

            ax.plot(x_values, y_values, color=color, linewidth=2.5)
            ax.fill_between(x_values, y_values, alpha=0.4, color=color)
            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel(x_label, color='white', fontsize=12)
            ax.set_ylabel(y_label, color='white', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray')
            ax.tick_params(colors='white', labelsize=10)

            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()

            log_info(f"Created area chart: {title}")
            return f"\n![{title}](assets/charts/{filename})\n"

        except Exception as e:
            plt.close()
            return f"Error creating area chart: {str(e)}"

    def create_histogram(self, title: str, values: list, bins: int = 10, color: str = '#9B59B6') -> str:
        """Create a histogram with modern styling."""
        try:
            plt.figure(figsize=(12, 7))
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')

            n, bins, patches = ax.hist(values, bins=bins, color=color, edgecolor='white', linewidth=1.5, alpha=0.8)
            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Value', color='white', fontsize=12)
            ax.set_ylabel('Frequency', color='white', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray', axis='y')
            ax.tick_params(colors='white', labelsize=10)

            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()

            log_info(f"Created histogram: {title}")
            return f"\n![{title}](assets/charts/{filename})\n"

        except Exception as e:
            plt.close()
            return f"Error creating histogram: {str(e)}"

    def create_box_plot(self, title: str, data: list, labels: list = None, color: str = '#FF8A00') -> str:
        """Create a box plot with modern styling."""
        try:
            plt.figure(figsize=(12, 7))
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')

            bp = ax.boxplot(data, patch_artist=True, labels=labels, widths=0.6)
            for patch in bp['boxes']:
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            for patch in bp['medians']:
                patch.set_color('white')
                patch.set_linewidth(2)
            for patch in bp['whiskers']:
                patch.set_color(color)
                patch.set_linewidth(1.5)

            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray', axis='y')
            ax.tick_params(colors='white', labelsize=10)

            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(self.charts_dir, filename)
            plt.savefig(filepath, facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()

            log_info(f"Created box plot: {title}")
            return f"\n![{title}](assets/charts/{filename})\n"

        except Exception as e:
            plt.close()
            return f"Error creating box plot: {str(e)}"
