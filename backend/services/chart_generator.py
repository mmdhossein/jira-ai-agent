import io
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Essential for headless environments
from matplotlib.figure import Figure
from typing import Dict, Any, List

class ChartGenerator:
    """Service for generating charts using the Thread-Safe Object-Oriented API."""
    
    async def generate_chart(self, chart_plan: Dict[str, Any], data: Dict[str, Any]) -> bytes:
        gen_type = chart_plan.get("gen_type")
        # Dispatch to specific methods
        print("Before methods")

        methods = {
            "bar": self._generate_bar_chart,
            "line": self._generate_line_chart,
            "pie": self._generate_pie_chart,
            "scatter": self._generate_scatter_chart,
            "heatmap": self._generate_heatmap,
            "histogram": self._generate_histogram
        }
        print("Before generator")
        generator = methods.get(gen_type, self._generate_bar_chart)
        print(f"DEBUG: Selected function: {generator}")
        result = await  generator(chart_plan, data)

        return result

    def _fig_to_bytes(self, fig: Figure) -> bytes:
        """Helper to convert Figure to bytes and clean up memory."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        image_bytes = buf.getvalue()
        buf.close()
        # Explicitly clear the figure to free memory
        fig.clf() 
        return image_bytes

    async def _generate_bar_chart(self, plan: Dict[str, Any], data: Dict[str, Any]) -> bytes:
        print("BAR : ", data)
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        x_data, y_data = data.get("x", []), data.get("y", [])
        
        if isinstance(y_data[0], list) if y_data else False:
            x_pos = np.arange(len(x_data))
            width = 0.8 / len(y_data)
            for i, series in enumerate(y_data):
                offset = width * i - (width * len(y_data) / 2) + width / 2
                label = data.get("series_labels", [])[i] if i < len(data.get("series_labels", [])) else f"Series {i+1}"
                ax.bar(x_pos + offset, series, width, label=label)
            ax.legend()
        else:
            ax.bar(x_data, y_data, color=plan.get("colors", ["#3498db"])[0])
        
        ax.set_title(plan.get("title", "Chart"))
        if len(x_data) > 10: ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        return self._fig_to_bytes(fig)

    async def _generate_line_chart(self, plan: Dict[str, Any], data: Dict[str, Any]) -> bytes:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        x_data, y_data = data.get("x", []), data.get("y", [])
        
        if isinstance(y_data[0], list) if y_data else False:
            for i, series in enumerate(y_data):
                label = data.get("series_labels", [])[i] if i < len(data.get("series_labels", [])) else f"Series {i+1}"
                ax.plot(x_data, series, marker='o', label=label)
            ax.legend()
        else:
            ax.plot(x_data, y_data, marker='o', color='#3498db')
        
        ax.set_title(plan.get("title", "Chart"))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return self._fig_to_bytes(fig)

    async def _generate_pie_chart(self, plan: Dict[str, Any], data: Dict[str, Any]) -> bytes:
        fig = Figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        ax.pie(data.get("values", []), labels=data.get("labels", []), autopct='%1.1f%%', startangle=90)
        ax.set_title(plan.get("title", "Chart"))
        fig.tight_layout()
        return self._fig_to_bytes(fig)

    async def _generate_scatter_chart(self, plan: Dict[str, Any], data: Dict[str, Any]) -> bytes:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.scatter(data.get("x", []), data.get("y", []), s=data.get("sizes", 50), alpha=0.6)
        ax.set_title(plan.get("title", "Chart"))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return self._fig_to_bytes(fig)

    async def _generate_heatmap(self, plan: Dict[str, Any], data: Dict[str, Any]) -> bytes:
        fig = Figure(figsize=(10, 8))
        ax = fig.add_subplot(111)
        im = ax.imshow(np.array(data.get("matrix", [])), cmap='YlOrRd', aspect='auto')
        fig.colorbar(im, ax=ax)
        ax.set_title(plan.get("title", "Heatmap"))
        fig.tight_layout()
        return self._fig_to_bytes(fig)

    async def _generate_histogram(self, plan: Dict[str, Any], data: Dict[str, Any]) -> bytes:
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.hist(data.get("values", []), bins=plan.get("bins", 20), color='#3498db', alpha=0.7)
        ax.set_title(plan.get("title", "Histogram"))
        fig.tight_layout()
        return self._fig_to_bytes(fig)
