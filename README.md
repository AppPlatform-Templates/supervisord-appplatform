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

- **Application + Background Worker**: Run a web server with a background job processor
- **Multi-Service Applications**: Combine related services that need to share the same filesystem
- **Observability**: Run monitoring agents (OpenTelemetry, StatsD, etc.) alongside your application
- **Legacy Applications**: Modernize applications that need multiple processes without redesigning architecture

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

2. **Update the App Spec**: Edit `.do/app.yaml` or use one of the examples in `.do/examples/`:
   ```bash
   # Replace AppPlatform-Templates with your actual GitHub username
   sed -i '' 's/AppPlatform-Templates/your-username/g' .do/examples/starter.yaml
   ```

3. **Deploy to App Platform**:
   ```bash
   doctl apps create --spec .do/examples/starter.yaml
   ```

Your app will be deployed and accessible at the URL provided by App Platform!

## Deployment Options

### Starter (Basic Multi-Process)
**Cost**: ~$12/month
**Instance**: 1 vCPU, 1GB RAM
**Processes**: Main app + optional background processes

```bash
doctl apps create --spec .do/examples/starter.yaml
```

### With OpenTelemetry
**Cost**: ~$12-18/month
**Instance**: 1 vCPU, 2GB RAM
**Processes**: Main app + OpenTelemetry agent

```bash
doctl apps create --spec .do/examples/with-otel.yaml
```

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
│  │  │  App   │    │  Worker/ │ │ │
│  │  │ (Flask)│    │   OTEL   │ │ │
│  │  │:8080   │    │  Agent   │ │ │
│  │  └────────┘    └──────────┘ │ │
│  │                               │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Project Structure

```
supervisord-appplatform/
├── .do/
│   ├── app.yaml                 # Main App Platform spec
│   └── examples/
│       ├── starter.yaml         # Basic deployment
│       └── with-otel.yaml       # With OpenTelemetry
├── app/
│   ├── app.py                   # Example Flask application
│   └── requirements.txt         # Python dependencies
├── config/
│   └── supervisord.conf         # Supervisord configuration
├── Dockerfile                   # Container definition
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

## Adding OpenTelemetry Instrumentation

1. **Uncomment OpenTelemetry dependencies** in `app/requirements.txt`:
   ```
   opentelemetry-distro==0.45b0
   opentelemetry-exporter-otlp==1.24.0
   opentelemetry-instrumentation-flask==0.45b0
   ```

2. **Enable in App Platform**:
   ```yaml
   - key: OTEL_ENABLED
     value: "true"
   - key: OTEL_EXPORTER_OTLP_ENDPOINT
     value: https://your-otel-collector.example.com
   ```

3. **Deploy** and your application will automatically be instrumented!

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
- [Example Applications](./examples/)

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
