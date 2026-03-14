# Configuration file for the Sphinx documentation builder.
# This file only contains a selection of the most common options.

import os
import sys
from pathlib import Path

# Project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Project information
project = "Dual-RAG-Evaluator"
copyright = "2024, Srini235"
author = "Srini235"
release = "1.0.0"

# Add extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
]

# Autodoc settings
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autosummary_generate = True

# Napoleon settings for Google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

# Theme configuration
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "both",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "#1f4788",
}

# HTML output options
html_static_path = ["_static"]
html_css_files = []
htmlhelp_basename = "Dual-RAG-Evaluatordoc"

# LaTeX output
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "",
    "fncychap": "\\usepackage{fncychap}",
    "printindex": "\\footnotesize",
}

latex_documents = [
    (
        "index",
        "DualRAGEvaluator.tex",
        "Dual-RAG-Evaluator Documentation",
        "Srini235",
        "manual",
    ),
]

# Man page output
man_pages = [
    (
        "index",
        "dual-rag-evaluator",
        "Dual-RAG-Evaluator Documentation",
        ["Srini235"],
        1,
    ),
]

# Texinfo output
texinfo_documents = [
    (
        "index",
        "DualRAGEvaluator",
        "Dual-RAG-Evaluator Documentation",
        "Srini235",
        "DualRAGEvaluator",
        "Compare ChromaDB vs ResonanceDB with negation support.",
        "Miscellaneous",
    ),
]

# General settings
master_doc = "index"
language = "en"
exclude_patterns = ["_build"]
pygments_style = "sphinx"
todo_include_todos = True

# Warnings
suppress_warnings = ["app.add_config_value"]
