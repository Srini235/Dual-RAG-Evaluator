"""
Export Utilities

Provides functionality to export results in multiple formats: PDF, CSV, JSON, HTML.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import csv

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


class ResultExporter:
    """Export comparison results in multiple formats."""

    def __init__(self, output_directory: str = "./results"):
        """
        Initialize exporter.

        Args:
            output_directory: Directory for exporting results.
        """
        self.output_dir = Path(output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ResultExporter initialized with output dir: {output_directory}")

    def export_json(
        self, results: Dict[str, Any], filename: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Export results as JSON.

        Args:
            results: Results dictionary to export.
            filename: Output filename (auto-generated if not provided).

        Returns:
            Tuple of (success, filepath)
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results_{timestamp}.json"

            filepath = self.output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported JSON to: {filepath}")
            return True, str(filepath)
        except Exception as e:
            error_msg = f"Error exporting JSON: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def export_csv(
        self, results: List[Dict[str, Any]], filename: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Export results as CSV.

        Args:
            results: List of result dictionaries to export.
            filename: Output filename (auto-generated if not provided).

        Returns:
            Tuple of (success, filepath)
        """
        try:
            if not results:
                return False, "No results to export"

            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results_{timestamp}.csv"

            filepath = self.output_dir / filename

            # Get all keys from all results
            keys = set()
            for result in results:
                keys.update(result.keys())
            keys = sorted(list(keys))

            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)

            logger.info(f"Exported CSV to: {filepath}")
            return True, str(filepath)
        except Exception as e:
            error_msg = f"Error exporting CSV: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def export_pdf(
        self, results: Dict[str, Any], filename: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Export results as PDF report.

        Args:
            results: Results dictionary to export.
            filename: Output filename (auto-generated if not provided).

        Returns:
            Tuple of (success, filepath)
        """
        if not REPORTLAB_AVAILABLE:
            msg = "reportlab not installed. Install with: pip install reportlab"
            logger.warning(msg)
            return False, None
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results_{timestamp}.pdf"

            filepath = self.output_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(str(filepath), pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f4788"),
                spaceAfter=30,
                alignment=1,  # Center alignment
            )
            story.append(Paragraph("Dual-RAG Comparison Results", title_style))
            story.append(Spacer(1, 0.2 * inch))

            # Metadata
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"<b>Generated:</b> {timestamp}", styles["Normal"]))
            story.append(Spacer(1, 0.3 * inch))

            # Results table
            table_data = [
                ["Metric", "ChromaDB", "ResonanceDB"],
            ]

            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            table_data.append([str(sub_key), str(sub_value), ""])
                    else:
                        table_data.append([str(key), str(value), ""])

            table = Table(table_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4788")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ]
                )
            )
            story.append(table)

            # Build PDF
            doc.build(story)
            logger.info(f"Exported PDF to: {filepath}")
            return True, str(filepath)
        except Exception as e:
            error_msg = f"Error exporting PDF: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def export_html(
        self, results: Dict[str, Any], filename: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Export results as HTML report.

        Args:
            results: Results dictionary to export.
            filename: Output filename (auto-generated if not provided).

        Returns:
            Tuple of (success, filepath)
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results_{timestamp}.html"

            filepath = self.output_dir / filename

            html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dual-RAG Comparison Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #1f4788; text-align: center; }
        .metadata { font-size: 0.9em; color: #666; margin: 20px 0; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background-color: #1f4788;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f0f0f0;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.85em;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Dual-RAG Comparison Results</h1>
        <div class="metadata">
            <strong>Generated:</strong> {timestamp}
        </div>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>ChromaDB</th>
                    <th>ResonanceDB</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <div class="footer">
            <p>Report generated by Dual-RAG-Evaluator v1.0.0</p>
        </div>
    </div>
</body>
</html>
"""

            rows = ""
            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            rows += f"<tr><td>{sub_key}</td><td>{sub_value}</td><td></td></tr>\n"
                    else:
                        rows += f"<tr><td>{key}</td><td>{value}</td><td></td></tr>\n"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            html_content = html_content.format(timestamp=timestamp, rows=rows)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Exported HTML to: {filepath}")
            return True, str(filepath)
        except Exception as e:
            error_msg = f"Error exporting HTML: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
