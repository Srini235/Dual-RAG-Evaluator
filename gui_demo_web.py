#!/usr/bin/env python
"""
Web-based GUI demo of Dual-RAG-Evaluator
Run: python gui_demo_web.py
Then open: http://localhost:5000
"""
import sys
sys.path.insert(0, 'src')

from flask import Flask, render_template_string, request, jsonify
import json
from config import get_settings
from core import DocumentProcessor, BaselineRetriever, DualRAGEvaluator
from core.resonance_client import MockResonanceDBClient

app = Flask(__name__)

# Initialize components
settings = get_settings()
doc_processor = DocumentProcessor()
retriever = BaselineRetriever()
resonance_client = MockResonanceDBClient()
evaluator = DualRAGEvaluator(retriever, resonance_client, doc_processor.model)

# Sample documents
sample_documents = [
    'Machine learning is a subset of artificial intelligence that enables systems to learn from data.',
    'Neural networks are computing systems inspired by biological neural networks in animal brains.',
    'Deep learning uses multiple layers of neural networks to process complex patterns in data.'
]

# HTML Template for GUI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dual-RAG-Evaluator GUI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Segoe UI, Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 28px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .container { max-width: 1200px; margin: 20px auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 0 20px; }
        .panel { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 20px; }
        .panel h2 { color: #2c3e50; margin-bottom: 15px; font-size: 18px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        textarea, input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #bdc3c7; border-radius: 4px; font-family: monospace; font-size: 12px; }
        textarea { resize: vertical; min-height: 120px; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { background: #2980b9; }
        .document-item { background: #ecf0f1; padding: 10px; margin: 5px 0; border-left: 3px solid #3498db; border-radius: 3px; }
        .result { background: #d5f4e6; padding: 15px; margin-top: 10px; border-radius: 4px; border-left: 3px solid #27ae60; }
        .loading { color: #e67e22; font-weight: bold; }
        .error { background: #fadbd8; padding: 10px; color: #c0392b; border-radius: 4px; margin-top: 10px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 15px; border-bottom: 2px solid #ecf0f1; }
        .tab { padding: 10px 15px; cursor: pointer; border: none; background: none; font-size: 14px; font-weight: 500; color: #7f8c8d; }
        .tab.active { color: #3498db; border-bottom: 3px solid #3498db; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .status { background: #e8f8f5; padding: 10px; border-radius: 4px; color: #27ae60; margin-bottom: 10px; }
        .grid-full { grid-column: 1 / -1; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Dual-RAG-Evaluator</h1>
        <p>Web-based GUI Demo - Interactive Retrieval-Augmented Generation Evaluation Tool</p>
    </div>
    
    <div class="container">
        <!-- Left Panel: Input -->
        <div class="panel">
            <h2>Input & Configuration</h2>
            
            <div class="tabs">
                <button class="tab active" onclick="switchTab(event, 'documents')">Documents</button>
                <button class="tab" onclick="switchTab(event, 'query')">Query</button>
                <button class="tab" onclick="switchTab(event, 'settings')">Settings</button>
            </div>
            
            <div id="documents" class="tab-content active">
                <h3 style="font-size: 14px; color: #2c3e50; margin: 10px 0;">Sample Documents</h3>
                <div id="documentList"></div>
                <button onclick="addDocument()">+ Add Document</button>
            </div>
            
            <div id="query" class="tab-content">
                <label>Enter Query:</label>
                <textarea id="queryInput" placeholder="e.g., What is machine learning?"></textarea>
                <button onclick="processQuery()">Process Query</button>
            </div>
            
            <div id="settings" class="tab-content">
                <div class="status">
                    App: <strong id="appName"></strong><br>
                    Version: <strong id="appVersion"></strong><br>
                    Model: <strong id="modelName"></strong><br>
                    Config Options: <strong id="configCount"></strong>
                </div>
            </div>
        </div>
        
        <!-- Right Panel: Output -->
        <div class="panel">
            <h2>Results & Output</h2>
            <div id="results" style="min-height: 200px;">
                <p style="color: #7f8c8d;">Results will appear here...</p>
            </div>
        </div>
        
        <!-- Full Width Panel: Processing Status -->
        <div class="panel grid-full">
            <h2>Processing Pipeline</h2>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
                <div style="text-align: center; padding: 15px; background: #ecf0f1; border-radius: 4px;">
                    <div style="font-weight: bold; color: #27ae60; font-size: 20px;">✓</div>
                    <div style="font-size: 12px; color: #2c3e50; margin-top: 5px;">Document Processing</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #ecf0f1; border-radius: 4px;">
                    <div style="font-weight: bold; color: #27ae60; font-size: 20px;">✓</div>
                    <div style="font-size: 12px; color: #2c3e50; margin-top: 5px;">Embedding Generation</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #ecf0f1; border-radius: 4px;">
                    <div style="font-weight: bold; color: #27ae60; font-size: 20px;">✓</div>
                    <div style="font-size: 12px; color: #2c3e50; margin-top: 5px;">Semantic Retrieval</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #ecf0f1; border-radius: 4px;">
                    <div style="font-weight: bold; color: #27ae60; font-size: 20px;">✓</div>
                    <div style="font-size: 12px; color: #2c3e50; margin-top: 5px;">Dual-Model Evaluation</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(evt, tabName) {
            var i, tabcontent, tabbuttons;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].classList.remove("active");
            }
            tabbuttons = document.getElementsByClassName("tab");
            for (i = 0; i < tabbuttons.length; i++) {
                tabbuttons[i].classList.remove("active");
            }
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
        
        function loadDocuments() {
            fetch('/api/documents')
                .then(r => r.json())
                .then(docs => {
                    let html = '';
                    docs.forEach((doc, idx) => {
                        html += `<div class="document-item">
                            <strong>[Doc ${idx+1}]</strong> ${doc.substring(0, 80)}...
                        </div>`;
                    });
                    document.getElementById('documentList').innerHTML = html;
                });
        }
        
        function loadSettings() {
            fetch('/api/settings')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('appName').textContent = data.app_name;
                    document.getElementById('appVersion').textContent = data.app_version;
                    document.getElementById('modelName').textContent = data.model;
                    document.getElementById('configCount').textContent = data.config_options;
                });
        }
        
        function processQuery() {
            let query = document.getElementById('queryInput').value;
            if (!query.trim()) {
                alert('Please enter a query');
                return;
            }
            
            document.getElementById('results').innerHTML = '<p class="loading">Processing query...</p>';
            
            fetch('/api/process', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            })
            .then(r => r.json())
            .then(data => {
                let html = `<div class="result">
                    <strong>Query:</strong> ${data.query}<br>
                    <strong>Processing Time:</strong> ${data.processing_time}ms<br>
                    <strong>Embedding Dimension:</strong> ${data.embedding_dim}<br>
                    <strong>Status:</strong> <span style="color: #27ae60;">✓ SUCCESS</span>
                </div>`;
                document.getElementById('results').innerHTML = html;
            })
            .catch(err => {
                document.getElementById('results').innerHTML = `<div class="error">Error: ${err.message}</div>`;
            });
        }
        
        function addDocument() {
            alert('Add document feature would allow you to upload or paste new documents for processing');
        }
        
        // Load on page load
        window.onload = function() {
            loadSettings();
            loadDocuments();
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/documents')
def api_documents():
    return jsonify(sample_documents)

@app.route('/api/settings')
def api_settings():
    settings_dict = settings.to_dict()
    return jsonify({
        'app_name': settings.APP_NAME,
        'app_version': settings.APP_VERSION,
        'model': settings.EMBEDDING_MODEL,
        'config_options': len(settings_dict),
        'debug': settings.DEBUG
    })

@app.route('/api/process', methods=['POST'])
def api_process():
    import time
    start = time.time()
    
    data = request.json
    query = data.get('query', '')
    
    # Process query
    embedded_query = doc_processor.embed_chunks([query])[0]
    processing_time = int((time.time() - start) * 1000)
    
    return jsonify({
        'query': query,
        'embedding_dim': len(embedded_query),
        'processing_time': processing_time,
        'status': 'success'
    })

if __name__ == '__main__':
    print('=' * 60)
    print('DUAL-RAG-EVALUATOR GUI - WEB-BASED DEMO')
    print('=' * 60)
    print('\nStarting Flask server...')
    print('\nEmbedding model loaded: %s (dim=%d)' % (settings.EMBEDDING_MODEL, 384))
    print('Sample documents loaded: %d' % len(sample_documents))
    print('\nOpen your browser and go to: http://localhost:5000')
    print('\nPress Ctrl+C to stop the server')
    print('=' * 60 + '\n')
    
    try:
        app.run(debug=False, host='localhost', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print('\n\nServer stopped.')
