"""
Main Window for Dual-RAG-Evaluator

PyQt5-based GUI for comparing ChromaDB vs ResonanceDB RAG systems.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QGroupBox,
    QTabWidget,
    QSplitter,
    QMessageBox,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from src.config import get_settings
from src.utils import (
    DocumentHandler,
    ResultExporter,
    get_app_logger,
    get_ui_logger,
)
# Lazy import of core modules - import on-demand to avoid torch DLL loading at startup
# from src.core import DocumentProcessor, BaselineRetriever, DualRAGEvaluator

logger = get_ui_logger()

# Lazy import function
def _get_core_modules():
    """Import core modules on-demand to defer torch DLL loading."""
    from src.core import DocumentProcessor, BaselineRetriever, DualRAGEvaluator
    return DocumentProcessor, BaselineRetriever, DualRAGEvaluator


class RAGComparisonThread(QThread):
    """Worker thread for RAG comparison to prevent UI freezing."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self,
        document_path: str,
        query: str,
        doc_processor: "DocumentProcessor",
        retriever: "BaselineRetriever",
        evaluator: "DualRAGEvaluator",
    ):
        super().__init__()
        self.document_path = document_path
        self.query = query
        self.doc_processor = doc_processor
        self.retriever = retriever
        self.evaluator = evaluator

    def run(self):
        """Execute RAG comparison in background thread."""
        try:
            self.progress.emit("Loading document...")
            # Load and process document
            # (implementation would use the working modules from src/core/)

            self.progress.emit("Running comparison...")
            # Run comparison

            results = {"chromadb": {}, "resonancedb": {}}
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(f"Error during comparison: {str(e)}")
            logger.error(f"Thread error: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window for Dual-RAG-Evaluator."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.settings = get_settings()
        self.doc_handler = DocumentHandler(max_size_mb=self.settings.MAX_FILE_SIZE_MB)
        self.exporter = ResultExporter(self.settings.RESULTS_DIRECTORY)

        # Core components (will be initialized)
        self.doc_processor = None
        self.retriever = None
        self.evaluator = None

        # Current results
        self.current_results = None
        self.comparison_thread = None

        # Setup UI
        self.initUI()
        self.setWindowTitle(f"{self.settings.APP_NAME} v{self.settings.APP_VERSION}")
        self.setGeometry(100, 100, self.settings.WINDOW_WIDTH, self.settings.WINDOW_HEIGHT)

        logger.info("Main window initialized")

    def initUI(self):
        """Initialize user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Title
        title = QLabel(f"{self.settings.APP_NAME}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # Create tabs
        tabs = QTabWidget()

        # Tab 1: Document & Query
        tab1 = self.create_input_tab()
        tabs.addTab(tab1, "Input & Query")

        # Tab 2: Results
        tab2 = self.create_results_tab()
        tabs.addTab(tab2, "Comparison Results")

        # Tab 3: Configuration
        tab3 = self.create_config_tab()
        tabs.addTab(tab3, "Configuration")

        # Tab 4: About
        tab4 = self.create_about_tab()
        tabs.addTab(tab4, "About")

        main_layout.addWidget(tabs)

        central_widget.setLayout(main_layout)

    def create_input_tab(self) -> QWidget:
        """Create input/query tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Document selection
        doc_group = QGroupBox("Document Upload")
        doc_layout = QHBoxLayout()

        self.doc_path_label = QLineEdit()
        self.doc_path_label.setReadOnly(True)
        self.doc_path_label.setPlaceholderText("No document selected")

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_document)

        doc_layout.addWidget(QLabel("Document:"))
        doc_layout.addWidget(self.doc_path_label)
        doc_layout.addWidget(self.browse_btn)
        doc_group.setLayout(doc_layout)

        layout.addWidget(doc_group)

        # Query input
        query_group = QGroupBox("Enter Query")
        query_layout = QVBoxLayout()

        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter your search query here...")
        self.query_input.setMaximumHeight(80)

        query_layout.addWidget(self.query_input)
        query_group.setLayout(query_layout)

        layout.addWidget(query_group)

        # Options
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()

        self.negation_check = QCheckBox("Detect Negation")
        self.negation_check.setChecked(self.settings.NEGATION_ENABLED)

        self.top_k_spin = QSpinBox()
        self.top_k_spin.setValue(self.settings.TOP_K)
        self.top_k_spin.setRange(1, 20)

        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setValue(self.settings.SIMILARITY_THRESHOLD)
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.1)

        options_layout.addWidget(QLabel("Top-K:"))
        options_layout.addWidget(self.top_k_spin)
        options_layout.addWidget(QLabel("Threshold:"))
        options_layout.addWidget(self.threshold_spin)
        options_layout.addWidget(self.negation_check)
        options_layout.addStretch()

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Run comparison button
        self.run_btn = QPushButton("Run Comparison")
        self.run_btn.setStyleSheet("background-color: #1f4788; color: white; padding: 10px;")
        self.run_btn.clicked.connect(self.run_comparison)
        self.run_btn.setMinimumHeight(40)

        layout.addWidget(self.run_btn)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_results_tab(self) -> QWidget:
        """Create results display tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Results will appear here...")

        layout.addWidget(QLabel("Comparison Results"))
        layout.addWidget(self.results_display)

        # Action buttons
        button_layout = QHBoxLayout()

        export_pdf_btn = QPushButton("Export as PDF")
        export_pdf_btn.clicked.connect(lambda: self.export_results("pdf"))

        export_csv_btn = QPushButton("Export as CSV")
        export_csv_btn.clicked.connect(lambda: self.export_results("csv"))

        export_json_btn = QPushButton("Export as JSON")
        export_json_btn.clicked.connect(lambda: self.export_results("json"))

        export_html_btn = QPushButton("Export as HTML")
        export_html_btn.clicked.connect(lambda: self.export_results("html"))

        copy_btn = QPushButton("Copy Results")
        copy_btn.clicked.connect(lambda: self.results_display.selectAll())

        button_layout.addWidget(export_pdf_btn)
        button_layout.addWidget(export_csv_btn)
        button_layout.addWidget(export_json_btn)
        button_layout.addWidget(export_html_btn)
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        widget.setLayout(layout)
        return widget

    def create_config_tab(self) -> QWidget:
        """Create configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("RAG Configuration"))

        # Chunk settings
        chunk_group = QGroupBox("Document Processing")
        chunk_layout = QHBoxLayout()

        chunk_layout.addWidget(QLabel("Chunk Size:"))
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setValue(self.settings.CHUNK_SIZE)
        chunk_layout.addWidget(self.chunk_size_spin)

        chunk_layout.addWidget(QLabel("Overlap:"))
        self.overlap_spin = QSpinBox()
        self.overlap_spin.setValue(self.settings.CHUNK_OVERLAP)
        chunk_layout.addWidget(self.overlap_spin)

        chunk_group.setLayout(chunk_layout)
        layout.addWidget(chunk_group)

        # Embedding settings
        embed_group = QGroupBox("Embedding Settings")
        embed_layout = QHBoxLayout()

        embed_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
            "distiluse-base-multilingual-cased-v2",
        ])
        self.model_combo.setCurrentText(self.settings.EMBEDDING_MODEL)
        embed_layout.addWidget(self.model_combo)

        embed_group.setLayout(embed_layout)
        layout.addWidget(embed_group)

        # Feature toggles
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout()

        self.cache_check = QCheckBox("Enable Caching")
        self.cache_check.setChecked(self.settings.CACHE_ENABLED)
        features_layout.addWidget(self.cache_check)

        self.metrics_check = QCheckBox("Enable Metrics")
        self.metrics_check.setChecked(self.settings.METRICS_ENABLED)
        features_layout.addWidget(self.metrics_check)

        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_about_tab(self) -> QWidget:
        """Create about/info tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setText(
            f"""
<h2>{self.settings.APP_NAME}</h2>
<p><b>Version:</b> {self.settings.APP_VERSION}</p>

<h3>Description</h3>
<p>Dual-RAG-Evaluator compares ChromaDB and ResonanceDB vector databases
for RAG (Retrieval-Augmented Generation) applications, with special focus
on semantic negation handling.</p>

<h3>Key Features</h3>
<ul>
  <li>Side-by-side RAG comparison</li>
  <li>Negation detection and analysis</li>
  <li>Multi-format export (PDF, CSV, JSON, HTML)</li>
  <li>Real-time metrics collection</li>
  <li>Query caching and history</li>
</ul>

<h3>Documentation</h3>
<p>For detailed documentation, visit the project repository on GitHub.</p>

<h3>License</h3>
<p>MIT License - See LICENSE file for details</p>
        """
        )

        layout.addWidget(about_text)
        widget.setLayout(layout)
        return widget

    def browse_document(self):
        """Browse and select document file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Document",
            "",
            "Documents (*.pdf *.docx *.txt *.md);;All Files (*)",
        )

        if file_path:
            is_valid, error = self.doc_handler.validate_file(file_path)
            if is_valid:
                self.doc_path_label.setText(file_path)
                logger.info(f"Document selected: {file_path}")
            else:
                QMessageBox.warning(self, "Invalid File", error)
                logger.warning(f"Invalid document: {error}")

    def run_comparison(self):
        """Run RAG comparison."""
        doc_path = self.doc_path_label.text()
        query = self.query_input.toPlainText()

        if not doc_path or doc_path == "No document selected":
            QMessageBox.warning(self, "Missing Document", "Please select a document first.")
            return

        if not query.strip():
            QMessageBox.warning(self, "Missing Query", "Please enter a query.")
            return

        # Lazy load core modules on first use
        if self.doc_processor is None:
            try:
                self.results_display.append("[Status] Initializing AI models (first run)...")
                QApplication.processEvents()
                
                DocumentProcessor, BaselineRetriever, DualRAGEvaluator = _get_core_modules()
                self.doc_processor = DocumentProcessor()
                self.retriever = BaselineRetriever()
                self.evaluator = DualRAGEvaluator(
                    self.retriever,
                    self.retriever.resonance_client if hasattr(self.retriever, 'resonance_client') else None,
                    self.doc_processor.model if hasattr(self.doc_processor, 'model') else None
                )
                self.results_display.append("[Status] Models loaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load AI models: {str(e)}")
                logger.error(f"Model loading error: {str(e)}")
                return

        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)

        # Start comparison in background thread
        self.comparison_thread = RAGComparisonThread(
            doc_path, query, self.doc_processor, self.retriever, self.evaluator
        )
        self.comparison_thread.progress.connect(self.update_progress)
        self.comparison_thread.finished.connect(self.on_comparison_finished)
        self.comparison_thread.error.connect(self.on_comparison_error)
        self.comparison_thread.start()

    def update_progress(self, message: str):
        """Update progress message."""
        self.results_display.append(f"[Progress] {message}")

    def on_comparison_finished(self, results: dict):
        """Handle comparison completion."""
        self.current_results = results
        self.results_display.setText(f"Results:\n{results}")
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        logger.info("Comparison completed successfully")

    def on_comparison_error(self, error: str):
        """Handle comparison error."""
        QMessageBox.critical(self, "Comparison Error", error)
        self.run_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        logger.error(f"Comparison error: {error}")

    def export_results(self, format_type: str):
        """Export results in specified format."""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "Run a comparison first.")
            return

        try:
            if format_type == "pdf":
                success, filepath = self.exporter.export_pdf(self.current_results)
            elif format_type == "csv":
                # Convert results to list format for CSV
                results_list = [self.current_results]
                success, filepath = self.exporter.export_csv(results_list)
            elif format_type == "json":
                success, filepath = self.exporter.export_json(self.current_results)
            elif format_type == "html":
                success, filepath = self.exporter.export_html(self.current_results)
            else:
                success, filepath = False, "Unknown format"

            if success:
                QMessageBox.information(
                    self, "Export Successful", f"Results exported to:\n{filepath}"
                )
                logger.info(f"Exported {format_type.upper()}: {filepath}")
            else:
                QMessageBox.warning(self, "Export Failed", filepath)
                logger.error(f"Export failed: {filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            logger.error(f"Export error: {str(e)}")


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
