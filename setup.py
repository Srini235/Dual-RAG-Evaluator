"""
Setup configuration for Dual-RAG-Evaluator

Enables pip installation with: pip install .
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dual-rag-evaluator',
    version='1.0.0',
    author='Srini235',
    author_email='contact@example.com',
    description='Dual RAG Evaluator - Compare ChromaDB vs ResonanceDB semantics with negation support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Srini235/Dual-RAG-Evaluator',
    project_urls={
        'Bug Tracker': 'https://github.com/Srini235/Dual-RAG-Evaluator/issues',
        'Documentation': 'https://github.com/Srini235/Dual-RAG-Evaluator/wiki',
        'Source Code': 'https://github.com/Srini235/Dual-RAG-Evaluator',
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Office/Business',
    ],
    python_requires='>=3.10',
    install_requires=[
        # Core ML dependencies
        'numpy>=1.24.0',
        'sentence-transformers>=2.2.0',
        'chromadb>=0.4.0',
        'torch>=2.0.0',
        
        # GUI framework
        'PyQt5>=5.15.0',
        'PyQt5-sip>=12.13.0',
        
        # RAG and orchestration
        'langchain>=0.0.300',
        'requests>=2.31.0',
        
        # Data processing and analysis
        'pandas>=2.0.0',
        'scikit-learn>=1.3.0',
        
        # Export and visualization
        'matplotlib>=3.7.0',
        'reportlab>=4.0.0',
        
        # Logging
        'loguru>=0.7.0',
        
        # Document processing
        'PyPDF2>=3.0.0',
        'python-docx>=0.8.11',
        'markdown>=3.4.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0',
            'isort>=5.12.0',
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.3.0',
            'sphinx-autodoc-typehints>=1.24.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'dual-rag=core.main:main',
        ],
        'gui_scripts': [
            'dual-rag-gui=ui.main_window:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        'RAG',
        'Vector Database',
        'ChromaDB',
        'ResonanceDB',
        'Semantic Search',
        'NLP',
        'Information Retrieval',
        'Machine Learning',
        'Healthcare',
    ],
)
