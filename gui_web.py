#!/usr/bin/env python
"""
Web-based GUI demo using built-in http.server
No external dependencies needed!
"""
import sys
sys.path.insert(0, 'src')

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from config import get_settings
from core import DocumentProcessor, BaselineRetriever, DualRAGEvaluator
from core.resonance_client import MockResonanceDBClient

# Initialize components
print('Initializing application components...')
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

HTML_CONTENT = '''<!DOCTYPE html>
<html>
<head>
    <title>Dual-RAG-Evaluator GUI</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            padding: 20px;
        }
        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 12px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
            color: white; 
            padding: 40px 20px; 
            text-align: center; 
        }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 30px; }
        .panel { }
        .panel h2 { 
            color: #2c3e50; 
            margin-bottom: 15px; 
            font-size: 18px; 
            border-bottom: 3px solid #667eea; 
            padding-bottom: 10px; 
        }
        textarea, input { 
            width: 100%; 
            padding: 12px; 
            margin: 8px 0; 
            border: 2px solid #e0e0e0; 
            border-radius: 6px; 
            font-family: "Courier New", monospace; 
            font-size: 13px;
            transition: border-color 0.3s;
        }
        textarea:focus, input:focus { 
            outline: none;
            border-color: #667eea;
        }
        textarea { resize: vertical; min-height: 100px; }
        input[type="text"] { height: 40px; }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 600; 
            margin-top: 10px;
            font-size: 14px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(102, 126, 234, 0.4);
        }
        button:active { transform: translateY(0); }
        .document-item { 
            background: #f8f9fa; 
            padding: 12px; 
            margin: 8px 0; 
            border-left: 4px solid #667eea; 
            border-radius: 4px;
            font-size: 13px;
            line-height: 1.4;
        }
        .result { 
            background: linear-gradient(135deg, #d5f4e6 0%, #e8f8f5 100%); 
            padding: 15px; 
            margin-top: 10px; 
            border-radius: 6px; 
            border-left: 4px solid #27ae60;
            font-size: 13px;
            line-height: 1.6;
        }
        .loading { color: #667eea; font-weight: bold; }
        .error { 
            background: #fadbd8; 
            padding: 12px; 
            color: #c0392b; 
            border-radius: 6px; 
            margin-top: 10px; 
            border-left: 4px solid #c0392b;
        }
        .status-box {
            background: linear-gradient(135deg, #e8f8f5 0%, #d5f4e6 100%);
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #27ae60;
            font-size: 13px;
            line-height: 1.6;
        }
        .pipeline {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 20px;
        }
        .pipeline-step {
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 6px;
            border: 2px solid #27ae60;
        }
        .pipeline-step-icon { 
            font-weight: bold; 
            color: #27ae60; 
            font-size: 24px; 
            margin-bottom: 8px;
        }
        .pipeline-step-label { 
            font-size: 12px; 
            color: #2c3e50; 
            font-weight: 600;
        }
        .full-width { grid-column: 1 / -1; }
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .stat { 
            padding: 10px; 
            background: #f8f9fa; 
            border-radius: 4px;
            font-size: 12px;
        }
        .stat-label { color: #7f8c8d; font-weight: 600; }
        .stat-value { color: #2c3e50; font-weight: 700; margin-top: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dual-RAG-Evaluator</h1>
            <p>Interactive Retrieval-Augmented Generation Evaluation System</p>
        </div>
        
        <div class="content">
            <div class="panel">
                <h2>Documents & Configuration</h2>
                <div class="status-box" id="statusBox">
                    <strong>System Status:</strong> Online<br>
                    <strong>App:</strong> Dual-RAG-Evaluator v1.0.0<br>
                    <strong>Model:</strong> all-MiniLM-L6-v2<br>
                    <strong>Config Options:</strong> 40
                </div>
                
                <h3 style="font-size: 13px; color: #2c3e50; margin: 15px 0 10px 0; font-weight: 600;">Loaded Documents</h3>
                <div id="documentList"></div>
            </div>
            
            <div class="panel">
                <h2>Query Processor</h2>
                <label style="display: block; font-weight: 600; color: #2c3e50; margin-bottom: 5px; font-size: 13px;">Enter a query:</label>
                <textarea id="queryInput" placeholder="Example: What is machine learning?"></textarea>
                <button onclick="processQuery()" style="width: 100%;">Process Query</button>
                <div id="results" style="margin-top: 15px; min-height: 100px;">
                    <p style="color: #95a5a6; font-size: 13px;">Results will appear here after processing...</p>
                </div>
            </div>
        </div>
        
        <div style="padding: 30px; border-top: 1px solid #ecf0f1;">
            <h2 style="color: #2c3e50; margin-bottom: 15px; font-size: 18px; border-bottom: 3px solid #667eea; padding-bottom: 10px;">Processing Pipeline</h2>
            <div class="pipeline">
                <div class="pipeline-step">
                    <div class="pipeline-step-icon">✓</div>
                    <div class="pipeline-step-label">Document Processing</div>
                </div>
                <div class="pipeline-step">
                    <div class="pipeline-step-icon">✓</div>
                    <div class="pipeline-step-label">Embedding Generation</div>
                </div>
                <div class="pipeline-step">
                    <div class="pipeline-step-icon">✓</div>
                    <div class="pipeline-step-label">Semantic Retrieval</div>
                </div>
                <div class="pipeline-step">
                    <div class="pipeline-step-icon">✓</div>
                    <div class="pipeline-step-label">Dual-Model Evaluation</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function loadDocuments() {
            let html = '';
            const docs = %DOCS_JSON%;
            docs.forEach((doc, idx) => {
                html += `<div class="document-item">
                    <strong>[Document ${idx+1}]</strong><br>
                    ${doc}
                </div>`;
            });
            document.getElementById('documentList').innerHTML = html;
        }
        
        function processQuery() {
            const query = document.getElementById('queryInput').value;
            if (!query.trim()) {
                document.getElementById('results').innerHTML = '<div class="error">Please enter a query</div>';
                return;
            }
            
            document.getElementById('results').innerHTML = '<p class="loading">Processing query...</p>';
            
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/process', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    const html = `<div class="result">
                        <strong>Query:</strong> ${data.query}<br>
                        <strong>Embedding Dimension:</strong> ${data.embedding_dim}<br>
                        <strong>Processing Time:</strong> ${data.processing_time}ms<br>
                        <strong>Status:</strong> <span style="color: #27ae60; font-weight: bold;">✓ SUCCESS</span>
                        <div class="stats">
                            <div class="stat">
                                <div class="stat-label">Model Used</div>
                                <div class="stat-value">all-MiniLM-L6-v2</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Vector Dimension</div>
                                <div class="stat-value">${data.embedding_dim}</div>
                            </div>
                        </div>
                    </div>`;
                    document.getElementById('results').innerHTML = html;
                } else {
                    document.getElementById('results').innerHTML = '<div class="error">Error processing query</div>';
                }
            };
            
            xhr.onerror = function() {
                document.getElementById('results').innerHTML = '<div class="error">Network error</div>';
            };
            
            xhr.send(JSON.stringify({query: query}));
        }
        
        // Load documents on page load
        window.onload = loadDocuments;
    </script>
</body>
</html>'''

class GUIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            html = HTML_CONTENT.replace('%DOCS_JSON%', json.dumps(sample_documents))
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/process':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            start = time.time()
            query = data.get('query', '')
            embedded_query = doc_processor.embed_chunks([query])[0]
            processing_time = int((time.time() - start) * 1000)
            
            response = {
                'query': query,
                'embedding_dim': len(embedded_query),
                'processing_time': processing_time,
                'status': 'success'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress unnecessary logs

if __name__ == '__main__':
    print('=' * 70)
    print(' ' * 10 + 'DUAL-RAG-EVALUATOR GUI - WEB INTERFACE')
    print('=' * 70)
    print()
    print('Embedding model loaded: %s' % settings.EMBEDDING_MODEL)
    print('Sample documents: %d' % len(sample_documents))
    print('Config options: %d' % len(settings.to_dict()))
    print()
    print('Starting web server on http://localhost:8080')
    print()
    print('IMPORTANT:')
    print('  1. Open http://localhost:8080 in your web browser')
    print('  2. You will see the GUI interface with:')
    print('     - Document list panel')
    print('     - Query processor panel')
    print('     - Processing pipeline visualization')
    print()
    print('  3. Try entering a query like:')
    print('     "What is machine learning?"')
    print()
    print('Press Ctrl+C to stop the server')
    print('=' * 70)
    print()
    
    server = HTTPServer(('localhost', 8080), GUIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\nServer stopped.')
        server.server_close()
