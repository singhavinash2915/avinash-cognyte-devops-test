#!/usr/bin/env python3
"""
Simple HTTP Server for Frontend Static Files
Production-grade static file serving for development/testing
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path
import argparse
import webbrowser
from datetime import datetime

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS support"""
    
    def end_headers(self):
        """Add CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def guess_type(self, path):
        """Override MIME type guessing for better support"""
        result = super().guess_type(path)
        
        # Handle case where super().guess_type returns just mimetype
        if isinstance(result, tuple):
            mimetype, encoding = result
        else:
            mimetype, encoding = result, None
        
        # Handle common frontend file types
        if path.endswith('.js'):
            return 'application/javascript', encoding
        elif path.endswith('.css'):
            return 'text/css', encoding
        elif path.endswith('.html'):
            return 'text/html', encoding
        elif path.endswith('.json'):
            return 'application/json', encoding
        elif path.endswith('.ico'):
            return 'image/x-icon', encoding
        
        return mimetype, encoding

def main():
    """Main server function"""
    parser = argparse.ArgumentParser(description='Currency Converter Frontend Server')
    parser.add_argument('--port', '-p', type=int, default=5000, 
                       help='Port to serve on (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--open', '-o', action='store_true',
                       help='Open browser automatically')
    parser.add_argument('--directory', '-d', type=str, default='.',
                       help='Directory to serve (default: current directory)')
    
    args = parser.parse_args()
    
    # Change to the specified directory
    if args.directory != '.':
        try:
            os.chdir(args.directory)
        except OSError as e:
            print(f"Error: Cannot change to directory '{args.directory}': {e}")
            sys.exit(1)
    
    # Verify index.html exists
    if not Path('index.html').exists():
        print("Warning: index.html not found in current directory")
        print(f"Current directory: {os.getcwd()}")
        print("Available files:")
        for file in os.listdir('.'):
            if os.path.isfile(file):
                print(f"  - {file}")
    
    # Create server
    try:
        with socketserver.TCPServer((args.host, args.port), CORSHTTPRequestHandler) as httpd:
            print(f"\n🚀 Currency Converter Frontend Server")
            print(f"📂 Serving directory: {os.getcwd()}")
            print(f"🌐 Server running at: http://{args.host}:{args.port}")
            print(f"📱 Local access: http://localhost:{args.port}")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n{'='*50}")
            print("Press Ctrl+C to stop the server")
            print(f"{'='*50}\n")
            
            # Open browser if requested
            if args.open:
                webbrowser.open(f'http://localhost:{args.port}')
                print(f"🌐 Opened http://localhost:{args.port} in default browser")
            
            # Start serving
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {args.port} is already in use")
            print(f"Try using a different port: python server.py --port {args.port + 1}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Server stopped by user")
        print(f"👋 Goodbye!")

if __name__ == '__main__':
    main()