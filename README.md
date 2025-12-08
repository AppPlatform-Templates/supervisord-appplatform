# Supervisord on DigitalOcean App Platform

A production-ready template for running multi-process applications on DigitalOcean App Platform using [Supervisord](http://supervisord.org/). This template demonstrates how to manage multiple processes within a single container, perfect for applications that need background workers, monitoring agents, or auxiliary services.

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/AppPlatform-Templates/supervisord-appplatform/tree/main)

## What is Supervisord?

Supervisord is a process control system that allows you to monitor and control multiple processes on UNIX-like systems. Unlike traditional init systems, it's designed for application-level process management, making it ideal for containerized environments where you need to run multiple related processes together.

## Features

- **Multi-Process Management**: Run your main application alongside background workers, monitoring agents, or other auxiliary processes
- **Process Monitoring**: Automatic restart of failed processes
- **Easy Configuration**: Simple INI-style configuration for defining processes
- **Logging**: Centralized logging for all managed processes
- **Health Checks**: Built-in health check endpoint for App Platform
- **Example Application**: Includes a Flask web application as a working example
- **OpenTelemetry Ready**: Optional configuration for running OpenTelemetry agent alongside your app

## Use Cases

- **Web Service + Monitoring Agent**: Run your application with OpenTelemetry, StatsD, or other monitoring agents
- **Web Service + Sidecar Processes**: Add auxiliary processes that need to run alongside your main application
- **Multi-Process Applications**: Applications that need multiple related processes on the same host
- **Agent-Based Architecture**: Run your app with agents for observability, security scanning, or data collection

## Quick Start

### Option 1: One-Click Deploy (Easiest)

Click the "Deploy to DigitalOcean" button above to automatically:
- Fork this repository to your GitHub account
- Deploy to App Platform with starter configuration
- Get your app running in minutes

No CLI tools required!

### Option 2: Manual Deploy via CLI

#### Prerequisites

- [DigitalOcean Account](https://cloud.digitalocean.com/registrations/new)
- [doctl CLI](https://docs.digitalocean.com/reference/doctl/how-to/install/) installed and authenticated
- GitHub account (for source deployment)

#### Deploy in 3 Steps

1. **Fork this repository** to your GitHub account

2. **Update the App Spec**: Edit `.do/app.yaml`:
   ```bash
   # Replace AppPlatform-Templates with your GitHub username
   sed -i '' 's/AppPlatform-Templates/your-username/g' .do/app.yaml
   ```

3. **Deploy to App Platform**:
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

Your app will be deployed with **2 processes running**:
- ✅ Flask web service (port 8080)
- ✅ OpenTelemetry agent (sidecar)
- ✅ Both managed by supervisord (PID 1)

Visit the app URL to see the live process dashboard!

## What's Included

**Cost**: ~$12/month (1 vCPU, 1GB RAM)

**Running Processes**:
1. **Supervisord** (PID 1) - Process supervisor managing everything
2. **Flask Web App** - Your application on port 8080 with OpenTelemetry instrumentation
3. **OTEL Agent** - OpenTelemetry sidecar for observability

**Features**:
- Process dashboard at `/` showing all running processes
- Health check endpoint at `/health`
- Test trace endpoint at `/test-trace` to verify OTEL instrumentation
- Automatic trace generation for all HTTP requests

The template demonstrates multi-process architecture - perfect for adding monitoring agents, security scanners, or any sidecar processes alongside your web service!

## Architecture

```
┌─────────────────────────────────────┐
│   DigitalOcean App Platform         │
│                                     │
│  ┌───────────────────────────────┐ │
│  │    Container (Port 8080)      │ │
│  │                               │ │
│  │  ┌─────────────────────────┐ │ │
│  │  │   Supervisord (PID 1)   │ │ │
│  │  └──────────┬──────────────┘ │ │
│  │             │                 │ │
│  │    ┌────────┴────────┐       │ │
│  │    │                 │       │ │
│  │  ┌─▼──────┐    ┌────▼─────┐ │ │
│  │  │ Flask  │    │   OTEL   │ │ │
│  │  │  Web   │    │  Agent   │ │ │
│  │  │  App   │    │ (Sidecar)│ │ │
│  │  │:8080   │    │          │ │ │
│  │  └────────┘    └──────────┘ │ │
│  │                               │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Project Structure

```
supervisord-appplatform/
├── .do/
│   ├── app.yaml                 # App Platform deployment spec
│   └── deploy.template.yaml     # Deploy button template
├── app/
│   ├── app.py                   # Example Flask application
│   ├── requirements.txt         # Python dependencies (includes OTEL)
│   └── start.sh                 # Application startup script
├── config/
│   └── supervisord.conf         # Supervisord configuration
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Local development setup
├── Makefile                     # Development commands
├── README.md                    # This file
└── .gitignore
```

## Customizing for Your Application

### 1. Replace the Example App

Replace `app/app.py` with your own application. Make sure to:
- Keep the `/health` endpoint for App Platform health checks
- Listen on the port specified by the `PORT` environment variable (default: 8080)
- Update `app/requirements.txt` with your dependencies

### 2. Configure Processes

Edit `config/supervisord.conf` to define your processes:

```ini
[program:my-app]
command=python my_app.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/app/my-app.err.log
stdout_logfile=/var/log/app/my-app.out.log
priority=10

[program:my-worker]
command=python worker.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/app/worker.err.log
stdout_logfile=/var/log/app/worker.out.log
priority=15
```

**Key configuration options**:
- `command`: The command to run your process
- `autostart`: Start process when supervisord starts
- `autorestart`: Restart process if it exits
- `priority`: Lower numbers start first
- `startsecs`: Process must stay running this long to be considered started
- `stopwaitsecs`: Time to wait for graceful shutdown before SIGKILL

### 3. Update Dockerfile

If you're using a different language or runtime, update the `Dockerfile`:

```dockerfile
# Example: Node.js application
FROM node:18-slim

RUN apt-get update && apt-get install -y supervisor curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ /app/
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN npm install

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

## Environment Variables

Configure these in your `.do/app.yaml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Application environment | `production` |
| `PORT` | Application port | `8080` |
| `OTEL_ENABLED` | Enable OpenTelemetry agent | `false` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL collector endpoint | - |
| `OTEL_SERVICE_NAME` | Service name for tracing | `supervisord-app` |

## Managing Processes

### View Running Processes

SSH into your container (via App Platform console) and run:

```bash
supervisorctl status
```

### Restart a Process

```bash
supervisorctl restart app
```

### View Logs

```bash
# View supervisord logs
tail -f /var/log/supervisor/supervisord.log

# View app logs
tail -f /var/log/app/app.out.log
tail -f /var/log/app/app.err.log
```

## OpenTelemetry Instrumentation

The template includes OpenTelemetry instrumentation out of the box, demonstrating how to run monitoring agents alongside your application.

### Testing OTEL Locally

The Flask app is automatically instrumented and generates traces for all HTTP requests:

```bash
# View automatic traces from any endpoint
curl http://localhost:8080/health
docker-compose logs | grep -i trace

# Test custom span creation
curl http://localhost:8080/test-trace
docker-compose logs | grep "custom-operation"
```

Every request generates trace spans with trace IDs, span IDs, and attributes. The `/test-trace` endpoint demonstrates how to create custom spans in your own code. By default, traces are exported to console for easy debugging.

### Sending Traces to a Collector

To send traces to your OTEL collector in production:

1. **Update the OTEL endpoint** in `.do/app.yaml`:
   ```yaml
   - key: OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
     value: https://your-otel-collector.example.com
   ```

2. **Deploy** and your application will automatically send traces to your collector!

The OTEL agent process runs alongside your app as a sidecar, demonstrating supervisord's multi-process management capabilities.

## Production Considerations

### Resource Sizing

- **Basic (1vCPU/1GB)**: Single app + lightweight worker
- **Standard (1vCPU/2GB)**: App + OTEL agent or heavier background processes
- **Professional (2vCPU/4GB+)**: Multiple workers or resource-intensive processes

### Monitoring

- Use App Platform's built-in metrics for container health
- Configure logging forwarding to centralized logging systems
- Set up alerts for container restarts and health check failures

### Security

- Never commit secrets to the repository
- Use App Platform environment variables with `type: SECRET` for sensitive data
- Keep dependencies updated regularly
- Use specific version tags in Dockerfile instead of `latest`

## Common Issues

### Process Fails to Start

Check logs in App Platform console or via supervisorctl:
```bash
supervisorctl tail app stderr
```

### Health Check Failing

Ensure your app:
1. Listens on `0.0.0.0` (not `localhost`)
2. Responds on the `/health` endpoint
3. Starts within `initial_delay_seconds` (default: 40s)

### Processes Restart Frequently

Check `startsecs` in supervisord.conf - the process must stay running this long to be considered successfully started.

## Examples

### Running a Python Worker

Add to `supervisord.conf`:
```ini
[program:worker]
command=celery -A app.tasks worker --loglevel=info
directory=/app
autostart=true
autorestart=true
```

### Running a Cron-like Task

```ini
[program:scheduler]
command=python scheduler.py
directory=/app
autostart=true
autorestart=true
```

## Limitations

- **No Persistent Storage**: App Platform uses ephemeral storage. Use DigitalOcean Spaces for persistent files
- **Single Container**: All processes run in one container and share resources
- **No Horizontal Scaling**: For multi-container scaling, separate services in App Platform
- **Not PID 1 Alternative**: Supervisord is not designed to replace init systems

## Resources

- [Supervisord Documentation](http://supervisord.org/)
- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [App Platform Pricing](https://www.digitalocean.com/pricing/app-platform)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this template for your projects.

## Support

- GitHub Issues: Report bugs or request features
- DigitalOcean Community: [DigitalOcean Community](https://www.digitalocean.com/community)
- Supervisord Docs: [supervisord.org](http://supervisord.org/)

---

Built with ❤️ for DigitalOcean App Platform
