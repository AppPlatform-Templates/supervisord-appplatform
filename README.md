# Supervisord on DigitalOcean App Platform

A production-ready template for running multi-process applications on DigitalOcean App Platform using [Supervisord](http://supervisord.org/). This template demonstrates how to manage multiple processes within a single container, perfect for running your application alongside monitoring agents or auxiliary services.

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/AppPlatform-Templates/supervisord-appplatform/tree/main)

## What is Supervisord?

Supervisord is a process control system that allows you to monitor and control multiple processes on UNIX-like systems. Unlike traditional init systems, it's designed for application-level process management, making it ideal for containerized environments where you need to run multiple related processes together.

## Features

- **Multi-Process Management**: Run your main application alongside monitoring agents or auxiliary services
- **Process Monitoring**: Automatic restart of failed processes
- **Easy Configuration**: Simple INI-style configuration for defining processes
- **Logging**: Centralized logging for all managed processes
- **Health Checks**: Built-in health check endpoint for App Platform
- **Example Application**: Includes a Flask web application as a working example
- **OpenTelemetry Ready**: Includes OpenTelemetry Collector for observability out of the box

## Use Cases

- **Web Service + Monitoring**: Run your application with OpenTelemetry Collector or other monitoring sidecars
- **Multi-Process Applications**: Applications that need multiple related processes in one container
- **Sidecar Pattern**: Run auxiliary processes alongside your main application (logging agents, proxies, etc.)

## Quick Start

### Option 1: One-Click Deploy (Easiest)

Click the "Deploy to DigitalOcean" button above to:
- Deploy the template directly to App Platform
- Get your app running in minutes with zero configuration

No CLI tools required!

**Note**: The one-click deploy uses the template repository. To customize the code, fork this repository and update your app settings in App Platform to point to your fork.

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
- ✅ OpenTelemetry Collector (sidecar)
- ✅ Both managed by supervisord

Visit the app URL to see the live process dashboard!

## What's Included

**Cost**: ~$12/month (1 vCPU, 1GB RAM)

**Running Processes**:
1. **Flask Web App** - Your application on port 8080 with OpenTelemetry instrumentation
2. **OTEL Collector** - OpenTelemetry sidecar for observability
3. Both managed by **Supervisord** (process manager)

**Features**:
- Process dashboard at `/` showing all running processes
- Health check endpoint at `/health`
- Test trace endpoint at `/test-trace` to verify OTEL instrumentation
- Automatic trace generation for all HTTP requests

The template demonstrates multi-process architecture with your web service and OpenTelemetry Collector running side by side.

## Architecture

```
┌─────────────────────────────────────┐
│   DigitalOcean App Platform         │
│                                     │
│  ┌───────────────────────────────┐  │
│  │    Container (Port 8080)      │  │
│  │                               │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │   Supervisord (PID 1)   │  │  │
│  │  └──────────┬──────────────┘  │  │
│  │             │                 │  │
│  │    ┌────────┴────────┐        │  │
│  │    │                 │        │  │
│  │  ┌─▼──────┐    ┌────▼─────┐   │  │
│  │  │ Flask  │    │   OTEL   │   │  │
│  │  │  Web   │    │  Agent   │   │  │
│  │  │  App   │    │ (Sidecar)│   │  │
│  │  │:8080   │    │          │   │  │
│  │  └────────┘    └──────────┘   │  │
│  │                               │  │
│  └───────────────────────────────┘  │
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

### 2. Understand the Configuration

The template includes two processes configured in `config/supervisord.conf`:
- **app**: Your main Flask application (modify `app/app.py` and `start.sh`)
- **otel-collector**: OpenTelemetry Collector for observability

**Key configuration options in supervisord.conf**:
- `command`: The command to run your process
- `autostart`: Start process when supervisord starts
- `autorestart`: Restart process if it exits
- `priority`: Lower numbers start first (otel-collector=5, app=10)
- `stdout_logfile=/dev/fd/1`: Send logs to stdout for App Platform

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

| Variable | Description | Default   |
|----------|-------------|-----------|
| `PORT` | Application port | `8080` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL collector endpoint (optional) | Console output |
| `OTEL_SERVICE_NAME` | Service name for tracing | `supervisord-app` |

Add custom environment variables as needed for your application.

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
curl http://127.0.0.1:8080/health
docker-compose logs | grep -i trace

# Test custom span creation
curl http://127.0.0.1:8080/test-trace
docker-compose logs | grep "custom-operation"
```

Every request generates trace spans with trace IDs, span IDs, and attributes. The `/test-trace` endpoint demonstrates how to create custom spans in your own code. By default, traces are exported to console for easy debugging.

### Sending Logs/Traces/Metrics to a Collector

To send logs/traces/metrics to your OTEL collector in production:

1. **Update the OTEL endpoint** in `.do/app.yaml`:
   ```yaml
   - key: OTEL_EXPORTER_OTLP_ENDPOINT
     value: https://your-otel-collector.example.com:4318
   ```

2. **Deploy** and your application will automatically send logs/traces/metrics to your collector!

**Note**: Use port `4318` for HTTP or `4317` for gRPC. See [OTEL_PRODUCTION.md](OTEL_PRODUCTION.md) for specific examples (Datadog, Grafana Cloud, Honeycomb, etc.).

The OTEL Collector process runs alongside your app as a sidecar, demonstrating supervisord's multi-process management capabilities.

## Production Considerations

### Resource Sizing

- **Basic (1vCPU/1GB)**: App + OTEL Collector (recommended starting point)
- **Standard (1vCPU/2GB)**: For higher traffic or resource-intensive applications
- **Professional (2vCPU/4GB+)**: For high-traffic production applications

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

