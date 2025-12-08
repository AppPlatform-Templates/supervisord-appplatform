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
    from flask import request

    try:
        # Get current process info
        current_pid = os.getpid()
        current_ppid = os.getppid()

        # Get process tree
        ps_output = subprocess.check_output(['ps', 'auxf'], text=True)

        # Get supervisorctl status
        supervisor_status = None
        supervisor_processes = []
        try:
            supervisor_status = subprocess.check_output(
                ['supervisorctl', '-c', '/etc/supervisor/conf.d/supervisord.conf', 'status'],
                text=True,
                stderr=subprocess.STDOUT
            )
            # Parse supervisor status into structured data
            for line in supervisor_status.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        supervisor_processes.append({
                            'name': parts[0],
                            'status': parts[1],
                            'details': ' '.join(parts[2:]) if len(parts) > 2 else ''
                        })
        except Exception as e:
            supervisor_status = f"Error: {str(e)}"

        # Get PID 1 info
        pid1_cmd = None
        try:
            pid1_info = subprocess.check_output(['ps', '-p', '1', '-o', 'cmd'], text=True)
            pid1_cmd = pid1_info.strip().split('\n')[1] if '\n' in pid1_info else pid1_info
        except Exception as e:
            pid1_cmd = f"Error: {str(e)}"

        # Check if HTML format is requested
        if request.args.get('format') == 'html' or 'text/html' in request.headers.get('Accept', ''):
            return render_process_html(current_pid, current_ppid, pid1_cmd, supervisor_processes, ps_output)

        return jsonify({
            'status': 'ok',
            'architecture': {
                'description': 'Multi-process container managed by supervisord',
                'pid_1': {
                    'process': 'supervisord',
                    'command': pid1_cmd,
                    'role': 'Process supervisor and PID 1'
                },
                'managed_processes': supervisor_processes
            },
            'current_request': {
                'handler_pid': current_pid,
                'parent_pid': current_ppid,
                'process_name': 'Flask application'
            },
            'raw_data': {
                'supervisor_status': supervisor_status,
                'process_tree': ps_output
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'current_process': {
                'pid': os.getpid(),
                'ppid': os.getppid()
            }
        }), 500

def render_process_html(current_pid, current_ppid, pid1_cmd, supervisor_processes, ps_output):
    """Render a nice HTML view of the process information"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supervisord Process Monitor</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 40px auto;
                padding: 0 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #0080FF;
                margin-top: 0;
            }
            h2 {
                color: #333;
                border-bottom: 2px solid #0080FF;
                padding-bottom: 10px;
                margin-top: 30px;
            }
            .status-box {
                background: #f8f9fa;
                border-left: 4px solid #0080FF;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            .process-item {
                background: #fff;
                border: 1px solid #e0e0e0;
                padding: 12px;
                margin: 10px 0;
                border-radius: 4px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .status-running {
                color: #28a745;
                font-weight: bold;
            }
            .status-stopped {
                color: #dc3545;
                font-weight: bold;
            }
            .pid-badge {
                background: #0080FF;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            pre {
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 20px;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 13px;
            }
            .metric {
                display: inline-block;
                margin-right: 20px;
            }
            .metric-label {
                color: #666;
                font-size: 14px;
            }
            .metric-value {
                color: #333;
                font-size: 20px;
                font-weight: bold;
            }
            .architecture-diagram {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 4px;
                font-family: monospace;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Supervisord Process Monitor</h1>

            <div class="status-box">
                <strong>Multi-Process Architecture Active</strong><br>
                Supervisord is managing multiple processes in a single container
            </div>

            <h2>📊 Architecture Overview</h2>
            <div class="architecture-diagram">
┌─────────────────────────────────────────────┐
│  Container (DigitalOcean App Platform)      │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ PID 1: supervisord                     │ │
│  │ Role: Process supervisor & init        │ │
│  └─────────────────┬───────────────────── │ │
│                    │                        │
│         ┏━━━━━━━━━━┻━━━━━━━━━━┓            │
│         ▼                      ▼            │
│  ┌─────────────┐      ┌──────────────┐    │
│  │ PID %d      │      │ Other        │    │
│  │ Flask App   │      │ Processes    │    │
│  │ Port 8080   │      │ (workers)    │    │
│  └─────────────┘      └──────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
            </div>

            <h2>🎯 PID 1 (Init Process)</h2>
            <div class="process-item">
                <div>
                    <strong>supervisord</strong><br>
                    <code style="color: #666;">%s</code>
                </div>
                <span class="pid-badge">PID 1</span>
            </div>

            <h2>⚙️ Managed Processes</h2>
    """ % (current_pid, pid1_cmd)

    for proc in supervisor_processes:
        status_class = 'status-running' if proc['status'] == 'RUNNING' else 'status-stopped'
        html += f"""
            <div class="process-item">
                <div>
                    <strong>{proc['name']}</strong><br>
                    <span class="{status_class}">{proc['status']}</span> - {proc['details']}
                </div>
            </div>
        """

    html += f"""
            <h2>📍 Current Request Handler</h2>
            <div class="status-box">
                <div class="metric">
                    <div class="metric-label">Process ID</div>
                    <div class="metric-value">{current_pid}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Parent PID</div>
                    <div class="metric-value">{current_ppid}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Process</div>
                    <div class="metric-value">Flask App</div>
                </div>
            </div>

            <h2>🌳 Full Process Tree</h2>
            <pre>{ps_output}</pre>

            <p style="text-align: center; color: #666; margin-top: 40px;">
                <small>Add <code>?format=json</code> to get JSON output</small>
            </p>
        </div>
    </body>
    </html>
    """

    from flask import Response
    return Response(html, mimetype='text/html')

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
