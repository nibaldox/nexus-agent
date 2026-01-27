"""
Chart Tools for Agno - Advanced Visualization Toolkit
Creates various types of charts with modern styling
"""
import matplotlib
matplotlib.use('Agg')  # Prevent GUI blocking
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import re
import uuid
from datetime import datetime
import json
import shutil
from agno.tools import Toolkit
from agno.utils.log import log_info

class ChartTools(Toolkit):
    """Advanced chart creation toolkit with multiple chart types and modern styling."""

    def __init__(self, charts_dir: str = os.path.join("workspace", "assets", "charts")):
        super().__init__(name="chart_tools")
        self.charts_dir = charts_dir
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)

        self.register(self.create_interactive_chart)
        self.register(self.create_chart)
        self.register(self.create_scatter_plot)
        self.register(self.create_area_chart)
        self.register(self.create_histogram)
        self.register(self.create_box_plot)

    def _get_session_id(self) -> str:
        return os.getenv("NEXUS_SESSION_ID") or "default"

    def _ensure_dir(self, path: str):
        os.makedirs(path, exist_ok=True)

    def _slugify(self, text: str) -> str:
        if not text:
            return "chart"
        text = text.lower().strip()
        text = re.sub(r"\s+", "_", text)
        text = re.sub(r"[^a-z0-9_-]", "", text)
        text = re.sub(r"_+", "_", text).strip("_")
        return text or "chart"

    def _build_filename(self, title: str, chart_type: str, ext: str) -> str:
        base = self._slugify(title)
        type_slug = self._slugify(chart_type) or "chart"
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_id = str(uuid.uuid4())[:8]
        return f"{base}_{type_slug}_{stamp}_{short_id}.{ext}"

    def _resolve_paths(self, filename: str) -> dict:
        session_id = self._get_session_id()
        base_dir = Path(__file__).resolve().parents[1]
        session_dir = base_dir / "workspace" / "conversations" / session_id / "assets" / "charts"
        public_dir = (base_dir / self.charts_dir).resolve()

        self._ensure_dir(str(session_dir))
        self._ensure_dir(str(public_dir))

        return {
            "session_path": str(session_dir / filename),
            "public_path": str(public_dir / filename),
            "session_dir": str(session_dir),
            "public_dir": str(public_dir)
        }

    def create_interactive_chart(self, type: str, title: str, x_values: list, y_values: list,
                                x_label: str = "", y_label: str = "", width: int = 900, height: int = 420) -> str:
        """
        Creates an INTERACTIVE Chart.js chart embedded in HTML.
        
        RECOMMENDED over create_chart() for better user experience.
        
        :param type: 'line', 'bar', 'pie', 'radar', 'doughnut'
        :param title: Title of the chart
        :param x_values: List of labels for X axis
        :param y_values: List of values for Y axis
        :return: Markdown string with iframe embed
        """
        try:
            if len(x_values) != len(y_values):
                min_len = min(len(x_values), len(y_values))
                x_values = x_values[:min_len]
                y_values = y_values[:min_len]

            chart_type_map = {'line': 'line', 'bar': 'bar', 'pie': 'pie', 'area': 'line', 'doughnut': 'doughnut', 'radar': 'radar'}
            chartjs_type = chart_type_map.get(type.lower(), 'line')
            
            colors = ['rgba(0, 224, 255, 0.8)', 'rgba(217, 70, 239, 0.8)', 'rgba(255, 138, 0, 0.8)', 'rgba(52, 211, 153, 0.8)']
            border_colors = [c.replace('0.8)', '1)') for c in colors]
            background_colors = [c.replace('0.8)', '0.3)') for c in colors]
            
            if chartjs_type in ['pie', 'doughnut']:
                dataset = {"label": y_label or "Values", "data": y_values, "backgroundColor": colors[:len(y_values)], "borderColor": border_colors[:len(y_values)], "borderWidth": 2}
            else:
                dataset = {"label": y_label or "Data", "data": y_values, "backgroundColor": background_colors[0], "borderColor": border_colors[0], "borderWidth": 2.5, "fill": type.lower() == 'area', "tension": 0.3}
            
            chart_config = {
                "type": chartjs_type,
                "data": {"labels": [str(x) for x in x_values], "datasets": [dataset]},
                "options": {
                    "responsive": True, "maintainAspectRatio": False,
                    "plugins": {
                        "title": {"display": True, "text": title, "color": "#e2e8f0", "font": {"size": 18, "weight": "bold"}},
                        "legend": {"labels": {"color": "#e2e8f0"}},
                        "tooltip": {"backgroundColor": "rgba(10, 10, 10, 0.95)", "titleColor": "#00E0FF", "bodyColor": "#e2e8f0", "borderColor": "#6366f1", "borderWidth": 1}
                    },
                    "scales": {
                        "x": {"display": chartjs_type not in ['pie', 'doughnut'], "title": {"display": bool(x_label), "text": x_label, "color": "#e2e8f0"}, "ticks": {"color": "#94a3b8"}, "grid": {"color": "rgba(255, 255, 255, 0.1)"}},
                        "y": {"display": chartjs_type not in ['pie', 'doughnut'], "title": {"display": bool(y_label), "text": y_label, "color": "#e2e8f0"}, "ticks": {"color": "#94a3b8"}, "grid": {"color": "rgba(255, 255, 255, 0.1)"}}
                    }
                }
            }
            
            # Pre-serialize config to JSON to ensure proper escaping
            config_json = json.dumps(chart_config)
            
            download_name = self._build_filename(title, type, "png")
            html_content = f"""<!DOCTYPE html><html><head><script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script><script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script><style>body {{ background: #000000; padding: 20px; font-family: monospace; color: #e2e8f0; }} .chart-container {{ position: relative; width: 100%; max-width: {width}px; height: {height}px; margin: 0 auto; }} .download-btn {{ position: absolute; top: 10px; right: 10px; background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.5); color: #e2e8f0; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 12px; z-index: 1000; }}</style></head><body><button class="download-btn" onclick="downloadChart()">📥 Download PNG</button><div class="chart-container"><canvas id="myChart"></canvas></div><script>const ctx = document.getElementById('myChart'); const config = {config_json}; if (config.type !== 'pie' && config.type !== 'doughnut') {{ config.options.plugins.zoom = {{ zoom: {{ wheel: {{ enabled: true }}, pinch: {{ enabled: true }}, mode: 'xy' }}, pan: {{ enabled: true, mode: 'xy' }} }}; }} const myChart = new Chart(ctx, config); function downloadChart() {{ const canvas = document.getElementById('myChart'); const url = canvas.toDataURL('image/png'); const a = document.createElement('a'); a.href = url; a.download = '{download_name}'; a.click(); }}</script></body></html>"""
            
            filename = self._build_filename(title, type, "html")
            paths = self._resolve_paths(filename)
            with open(paths["session_path"], 'w', encoding='utf-8') as f:
                f.write(html_content)
            # Copy to public assets for UI rendering
            shutil.copyfile(paths["session_path"], paths["public_path"])
            
            log_info(f"Created interactive {type} chart: {title}")
            
            # For the browser: src="assets/charts/{filename}" (because of FastAPI mount)
            # For the agents: path is "workspace/conversations/{session_id}/assets/charts/{filename}"
            return f'''
### 📊 Visualización Interactiva: {title}

<iframe src="assets/charts/{filename}" width="100%" height="{height + 60}" frameborder="0" style="border-radius: 8px; background: #000;"></iframe>

> **Info para Agentes**: El archivo interactivo se guardó en `{paths["session_path"]}`.
> **Publicación UI**: `{paths["public_path"]}`.
> **Características**: Interactivo, Zoom, Pan, Exportar PNG.

**Tipo**: {type.title()} Chart | **Puntos**: {len(y_values)}
'''
        except Exception as e:
            return f"Error creating interactive chart: {str(e)}"

    def create_chart(self, type: str, title: str, x_values: list, y_values: list,
                   x_label: str = "", y_label: str = "", color: str = None) -> str:
        """Generates a STATIC chart and returns a Markdown image link."""
        try:
            if len(x_values) != len(y_values):
                min_len = min(len(x_values), len(y_values))
                x_values = x_values[:min_len]
                y_values = y_values[:min_len]

            plt.figure(figsize=(14, 6))
            plt.style.use('dark_background')
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')

            if color is None:
                color = '#00E0FF' if type.lower() == 'line' else '#D946EF' if type.lower() == 'bar' else '#00E0FF'

            if type.lower() == 'line':
                ax.plot(x_values, y_values, marker='o', color=color, linewidth=2.5, markersize=8)
                ax.fill_between(x_values, y_values, alpha=0.3, color=color)
            elif type.lower() == 'bar':
                bars = ax.bar(x_values, y_values, color=color, edgecolor='white', linewidth=1.5, alpha=0.8)
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}', ha='center', va='bottom', color='white', fontsize=9)
            elif type.lower() == 'pie':
                colors = ['#00E0FF', '#D946EF', '#FF8A00', '#F0F0F0', '#00FF7F', '#9B59B6']
                ax.pie(y_values, labels=x_values, autopct='%1.1f%%', colors=colors, startangle=90, explode=[0.05]*len(y_values))

            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            if type.lower() != 'pie':
                ax.set_xlabel(x_label, color='white', fontsize=12)
                ax.set_ylabel(y_label, color='white', fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.3, color='gray')

            filename = self._build_filename(title, type, "png")
            paths = self._resolve_paths(filename)
            plt.savefig(paths["session_path"], facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()
            shutil.copyfile(paths["session_path"], paths["public_path"])
            log_info(f"Created static {type} chart: {title}")
            return f"\n![{title}](assets/charts/{filename})\n\n> **Ruta local**: `{paths['session_path']}`\n> **Publicación UI**: `{paths['public_path']}`"
        except Exception as e:
            plt.close()
            return f"Error creating chart: {str(e)}"

    def create_scatter_plot(self, title: str, x_values: list, y_values: list,
                         x_label: str = "", y_label: str = "", color: str = '#FF6B6B') -> str:
        """Create a scatter plot with modern styling."""
        try:
            plt.figure(figsize=(14, 6))
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            ax.scatter(x_values, y_values, c=color, s=100, alpha=0.7, edgecolors='white', linewidth=1.5)
            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel(x_label, color='white', fontsize=12)
            ax.set_ylabel(y_label, color='white', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray')
            filename = self._build_filename(title, "scatter", "png")
            paths = self._resolve_paths(filename)
            plt.savefig(paths["session_path"], facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()
            shutil.copyfile(paths["session_path"], paths["public_path"])
            log_info(f"Created scatter plot: {title}")
            return f"\n![{title}](assets/charts/{filename})\n\n> **Ruta local**: `{paths['session_path']}`\n> **Publicación UI**: `{paths['public_path']}`"
        except Exception as e:
            plt.close()
            return f"Error creating scatter plot: {str(e)}"

    def create_area_chart(self, title: str, x_values: list, y_values: list,
                       x_label: str = "", y_label: str = "", color: str = '#00E0FF') -> str:
        """Create an area chart with modern styling."""
        try:
            plt.figure(figsize=(14, 6))
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            ax.plot(x_values, y_values, color=color, linewidth=2.5)
            ax.fill_between(x_values, y_values, alpha=0.4, color=color)
            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel(x_label, color='white', fontsize=12)
            ax.set_ylabel(y_label, color='white', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray')
            filename = self._build_filename(title, "area", "png")
            paths = self._resolve_paths(filename)
            plt.savefig(paths["session_path"], facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()
            shutil.copyfile(paths["session_path"], paths["public_path"])
            log_info(f"Created area chart: {title}")
            return f"\n![{title}](assets/charts/{filename})\n\n> **Ruta local**: `{paths['session_path']}`\n> **Publicación UI**: `{paths['public_path']}`"
        except Exception as e:
            plt.close()
            return f"Error creating area chart: {str(e)}"

    def create_histogram(self, title: str, values: list, bins: int = 10, color: str = '#9B59B6') -> str:
        """Create a histogram with modern styling."""
        try:
            plt.figure(figsize=(14, 6))
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')
            ax.hist(values, bins=bins, color=color, edgecolor='white', linewidth=1.5, alpha=0.8)
            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Value', color='white', fontsize=12)
            ax.set_ylabel('Frequency', color='white', fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray', axis='y')
            filename = self._build_filename(title, "histogram", "png")
            paths = self._resolve_paths(filename)
            plt.savefig(paths["session_path"], facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()
            shutil.copyfile(paths["session_path"], paths["public_path"])
            log_info(f"Created histogram: {title}")
            return f"\n![{title}](assets/charts/{filename})\n\n> **Ruta local**: `{paths['session_path']}`\n> **Publicación UI**: `{paths['public_path']}`"
        except Exception as e:
            plt.close()
            return f"Error creating histogram: {str(e)}"

    def create_box_plot(self, title: str, data: list, labels: list = None, color: str = '#FF8A00') -> str:
        """Create a box plot with modern styling."""
        try:
            plt.figure(figsize=(14, 6))
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
            ax.set_title(title, color='white', fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, linestyle='--', alpha=0.3, color='gray', axis='y')
            filename = self._build_filename(title, "boxplot", "png")
            paths = self._resolve_paths(filename)
            plt.savefig(paths["session_path"], facecolor='#1e1e1e', dpi=150, bbox_inches='tight')
            plt.close()
            shutil.copyfile(paths["session_path"], paths["public_path"])
            log_info(f"Created box plot: {title}")
            return f"\n![{title}](assets/charts/{filename})\n\n> **Ruta local**: `{paths['session_path']}`\n> **Publicación UI**: `{paths['public_path']}`"
        except Exception as e:
            plt.close()
            return f"Error creating box plot: {str(e)}"
