"""
Example Flask Application managed by Supervisord
This is a simple demo app to showcase multi-process management
"""

from flask import Flask, jsonify
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Hello from Supervisord-managed app!',
        'status': 'running',
        'processes': 'managed by supervisord'
    })

@app.route('/health')
def health():
    """Health check endpoint for App Platform"""
    return jsonify({
        'status': 'healthy',
        'service': 'supervisord-app'
    }), 200

@app.route('/info')
def info():
    """Show environment and process information"""
    return jsonify({
        'environment': {
            'APP_ENV': os.getenv('APP_ENV', 'development'),
            'PORT': os.getenv('PORT', '8080'),
            'OTEL_ENABLED': os.getenv('OTEL_ENABLED', 'false')
        },
        'process_manager': 'supervisord',
        'python_version': sys.version
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"OpenTelemetry enabled: {os.getenv('OTEL_ENABLED', 'false')}")

    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('APP_ENV') == 'development'
    )
