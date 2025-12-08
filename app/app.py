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

@app.route('/processes')
def processes():
    """Show process tree and supervisord information"""
    import subprocess

    try:
        # Get current process info
        current_pid = os.getpid()
        current_ppid = os.getppid()

        # Get process tree
        ps_output = subprocess.check_output(['ps', 'auxf'], text=True)

        # Get supervisorctl status if available
        supervisor_status = None
        try:
            supervisor_status = subprocess.check_output(
                ['supervisorctl', '-c', '/etc/supervisor/conf.d/supervisord.conf', 'status'],
                text=True,
                stderr=subprocess.STDOUT
            )
        except Exception as e:
            supervisor_status = f"Error getting supervisor status: {str(e)}"

        # Get PID 1 info
        pid1_info = None
        try:
            pid1_info = subprocess.check_output(['ps', '-p', '1', '-o', 'pid,ppid,cmd'], text=True)
        except Exception as e:
            pid1_info = f"Error: {str(e)}"

        return jsonify({
            'current_process': {
                'pid': current_pid,
                'ppid': current_ppid,
                'description': 'This Flask app process'
            },
            'pid_1_info': pid1_info,
            'supervisor_status': supervisor_status,
            'full_process_tree': ps_output
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'current_process': {
                'pid': os.getpid(),
                'ppid': os.getppid()
            }
        }), 500

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
