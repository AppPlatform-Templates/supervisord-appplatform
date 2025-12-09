# Supervisord on DigitalOcean App Platform

A production-ready template for running multi-process applications on DigitalOcean App Platform using [Supervisord](http://supervisord.org/). This template demonstrates how to manage multiple processes within a single container, perfect for running your application alongside monitoring agents or auxiliary services.

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/AppPlatform-Templates/supervisord-appplatform/tree/main)

## What is Supervisord?

Supervisord is a process control system that allows you to monitor and control multiple processes on UNIX-like systems. Unlike traditional init systems, it's designed for application-level process management, making it ideal for containerized environments where you need to run multiple related processes together.

## Features

- **Multi-Process Management**: Run your main application alongside monitoring agents or auxiliary services
- **Easy Configuration**: Simple INI-style configuration for defining processes
- **Centralized Logging**: All process logs available through App Platform
- **Health Checks**: Built-in health check endpoint for App Platform
- **Example Application**: Includes a Flask web application as a working example
- **OpenTelemetry Ready**: Includes OpenTelemetry Collector for observability out of the box

## Use Cases

- **Web Service + Monitoring**: Run your application with OpenTelemetry Collector or other monitoring sidecars
- **Multi-Process Applications**: Applications that need multiple related processes in one container
- **Sidecar Pattern**: Run auxiliary processes alongside your main application (logging agents, proxies, etc.)

## Quick Start

### Option 1: One-Click Deploy (Fastest)

Click the "Deploy to DigitalOcean" button above to:
- Deploy the template directly to App Platform
- Get your app running in minutes with zero configuration
- No CLI tools required!

**Note**: The one-click deploy uses the template repository. To customize the code:
1. Fork this repository to your GitHub account
2. Update your app settings in App Platform to point to your fork
3. Customize the code and push changes

### Option 2: Fork and Customize (Recommended)

For full control over your deployment:

#### Prerequisites
- [DigitalOcean Account](https://cloud.digitalocean.com/registrations/new)
- [doctl CLI](https://docs.digitalocean.com/reference/doctl/how-to/install/) installed and authenticated
- GitHub account

#### Steps

**Step 1: Authenticate doctl**

```bash
# Authenticate with DigitalOcean
doctl auth init

# Verify authentication
doctl account get
```

**Step 2: Fork the repository**

**Why fork?** You need your own repository to customize the code and enable auto-deployment.

1. Go to [https://github.com/AppPlatform-Templates/supervisord-appplatform](https://github.com/AppPlatform-Templates/supervisord-appplatform)
2. Click the "Fork" button in the top-right corner
3. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/supervisord-appplatform.git
   cd supervisord-appplatform
   ```

**Step 3: Update app specification**

Edit `.do/app.yaml` to point to your forked repository:

```bash
# Replace AppPlatform-Templates with your GitHub username
sed -i '' 's/AppPlatform-Templates/YOUR_USERNAME/g' .do/app.yaml
```

Or manually edit the file:

```yaml
services:
  - name: supervisord-service
    github:
      repo: YOUR_USERNAME/supervisord-appplatform  # Your fork
      branch: main
      deploy_on_push: true
```

**Step 4: (Optional) Customize your application**

Replace the example Flask app with your own:

1. **Replace `app/app.py`** with your application code
2. **Update `app/requirements.txt`** with your dependencies

**Step 5: Push to GitHub**

Commit and push your changes:

```bash
git add .
git commit -m "Customize supervisord template for my app"
git push origin main
```

**Step 6: Deploy to App Platform**

Deploy using the app specification file:

```bash
doctl apps create --spec .do/app.yaml
```

This will deploy your application with:
- **Flask web service** running on port 8080
- **OpenTelemetry Collector** running as a sidecar for observability
- Both processes managed by supervisord

### Option 3: Quick CLI Deploy (No Fork)

To quickly test the template without forking:

```bash
git clone https://github.com/AppPlatform-Templates/supervisord-appplatform.git
cd supervisord-appplatform
doctl apps create --spec .do/app.yaml
```

**To customize later**: Fork the repository, update the app in App Platform settings to point to your fork, then customize and push changes.

## What's Included

**Running Processes**:
1. **Flask Web App** - Your application on port 8080 with OpenTelemetry instrumentation
2. **OTEL Collector** - OpenTelemetry sidecar for observability
3. Both managed by **Supervisord** (process manager)

**Endpoints**:
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
│  │  │ :8080  │    │          │   │  │
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
│   ├── supervisord.conf         # Supervisord configuration
│   └── otel-collector-config.yaml  # OpenTelemetry Collector config
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Local development setup
├── Makefile                     # Development commands
├── OTEL_PRODUCTION.md          # Production OTEL configuration guide
└── README.md                    # This file
```

## Customizing for Your Application

### 1. Replace the Example App

Replace `app/app.py` with your own application. Make sure to:
- Keep the `/health` endpoint for App Platform health checks
- Listen on the port specified by the `PORT` environment variable (default: 8080)
- Update `app/requirements.txt` with your dependencies

**Example for Python applications:**
```python
import os
from flask import Flask

app = Flask(__name__)
port = int(os.getenv("PORT", 8080))

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

@app.route('/')
def index():
    return "My Custom App"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
```

### 2. Update Dockerfile for Different Languages

If you're using a different language or runtime, update the `Dockerfile`:

**Example: Node.js application**
```dockerfile
FROM node:18-slim

RUN apt-get update && apt-get install -y supervisor curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/ /app/
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN npm install

EXPOSE 8080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

### 3. Configure Supervisord Processes

The template includes two processes configured in `config/supervisord.conf`:
- **app**: Your main Flask application (modify `app/app.py` and `start.sh`)
- **otel-collector**: OpenTelemetry Collector for observability

**Key configuration options in supervisord.conf**:
```ini
[program:app]
command=/app/start.sh              # Command to run your process
autostart=true                     # Start process when supervisord starts
autorestart=true                   # Restart process if it exits
priority=10                        # Lower numbers start first
stdout_logfile=/dev/fd/1          # Send logs to stdout for App Platform
stderr_logfile=/dev/fd/2          # Send errors to stderr
```

**To add a new process:**
```ini
[program:myworker]
command=python /app/worker.py
autostart=true
autorestart=true
priority=15
stdout_logfile=/dev/fd/1
stderr_logfile=/dev/fd/2
```

### 4. Configure OpenTelemetry (Optional)

**By default**, traces/logs/metrics are exported to console logs (visible in App Platform Runtime Logs). No configuration needed!

**To send to production backends** (Grafana Cloud, Datadog, Honeycomb, etc.), see [OTEL_PRODUCTION.md](OTEL_PRODUCTION.md) for step-by-step configuration examples.

**To disable OTEL**, remove the `[program:otel-collector]` section from `config/supervisord.conf`.

## Monitoring Deployment

### View Deployment Status

```bash
# List all apps
doctl apps list

# Get app details (replace APP_ID with your actual app ID)
doctl apps get <APP_ID>

# View deployment logs
doctl apps logs <APP_ID> --type deploy
```

### Access Your Application

Once deployed, App Platform will provide a URL:

```bash
doctl apps get <APP_ID> --format LiveURL
```

Visit this URL to see your application running!

### Verify Multi-Process Setup

**Check health endpoint:**
```bash
curl https://your-app-url.ondigitalocean.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "supervisord-app"
}
```

**View process information:**
```bash
curl https://your-app-url.ondigitalocean.app/info
```

This will show environment variables and process manager info.

## Managing Your Application

### Configure GitHub Auto-Deploy

App Platform automatically deploys when you push to your repository:

1. Make changes to your code
2. Commit and push:
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```
3. App Platform will automatically build and deploy

To disable auto-deploy, update your spec:
```yaml
github:
  repo: your-username/supervisord-appplatform
  branch: main
  deploy_on_push: false  # Change to false
```

Then update the app:
```bash
doctl apps update <APP_ID> --spec .do/app.yaml
```

### Update Your App

**Update via CLI:**
```bash
# Update app configuration
doctl apps update <APP_ID> --spec .do/app.yaml

# Trigger manual deployment
doctl apps create-deployment <APP_ID>
```

**Update via Console:**
1. Go to [DigitalOcean Control Panel](https://cloud.digitalocean.com/apps)
2. Select your app
3. Click "Settings" > "App Spec"
4. Edit the YAML configuration
5. Click "Save" to redeploy

### Environment Variables

**Add environment variables via CLI:**
Update `.do/app.yaml`:
```yaml
envs:
  - key: APP_ENV
    value: production
    scope: RUN_TIME

  - key: CUSTOM_VAR
    value: your-value
    scope: RUN_TIME

  # For secrets
  - key: API_KEY
    value: your-secret-key
    scope: RUN_TIME
    type: SECRET
```

Then update the app:
```bash
doctl apps update <APP_ID> --spec .do/app.yaml
```

**Or via the console:**
1. Navigate to your app
2. Go to "Settings" > "Environment Variables"
3. Add/edit variables
4. Click "Save" (triggers redeployment)

**Common environment variables:**

| Variable | Description | Default   |
|----------|-------------|-----------|
| `PORT` | Application port | `8080` |
| `OTEL_SERVICE_NAME` | Service name for tracing | `supervisord-app` |

Add custom environment variables as needed for your application.

### Managing Processes

**Access console:**
1. Go to your app in the DigitalOcean console
2. Click "Console" tab
3. Run supervisorctl commands:

```bash
# View all processes
supervisorctl status

# Restart the main app
supervisorctl restart app

# Restart the OTEL collector
supervisorctl restart otel-collector

# View logs
supervisorctl tail app stdout
supervisorctl tail otel-collector stdout
```

**View logs via doctl:**
```bash
# View runtime logs
doctl apps logs <APP_ID> --type run --follow

# View build logs
doctl apps logs <APP_ID> --type build

# View deployment logs
doctl apps logs <APP_ID> --type deploy
```

### Scaling

**Vertical Scaling (More Resources):**

Update instance size in your spec:
```yaml
instance_size_slug: apps-s-2vcpu-4gb  # Upgrade to 2 vCPU, 4GB RAM
```

Then update:
```bash
doctl apps update <APP_ID> --spec .do/app.yaml
```

**Horizontal Scaling (More Instances):**

**Note**: Supervisord manages processes within a single container. For horizontal scaling across multiple containers, consider splitting services in your App Platform spec.

## OpenTelemetry Instrumentation

The template includes OpenTelemetry instrumentation out of the box, demonstrating how to run monitoring agents alongside your application.

### Testing OTEL Locally

The Flask app is automatically instrumented and generates traces for all HTTP requests:

```bash
# Start locally with docker-compose
docker-compose up

# View automatic traces from any endpoint
curl http://127.0.0.1:8080/health
docker-compose logs | grep -i trace

# Test custom span creation
curl http://127.0.0.1:8080/test-trace
docker-compose logs | grep "custom-operation"
```

Every request generates trace spans with trace IDs, span IDs, and attributes. The `/test-trace` endpoint demonstrates how to create custom spans in your own code. By default, traces are exported to console for easy debugging.

### Sending Data to Production Backends

**By default**, traces/logs/metrics are exported to console logs (visible in App Platform Runtime Logs). No configuration needed!

**To send to production backends** (Grafana Cloud, Datadog, Honeycomb, etc.), see [OTEL_PRODUCTION.md](OTEL_PRODUCTION.md) for step-by-step configuration examples.

The OTEL Collector process runs alongside your app as a sidecar, demonstrating supervisord's multi-process management capabilities.

## Troubleshooting

### Deployment Fails

1. **Check build logs:**
   ```bash
   doctl apps logs <APP_ID> --type build
   ```

2. **Check deployment logs:**
   ```bash
   doctl apps logs <APP_ID> --type deploy
   ```

3. **Common issues:**
   - Invalid GitHub repository path in `.do/app.yaml`
   - Missing dependencies in `requirements.txt`
   - Port mismatch (ensure app listens on `PORT` environment variable)
   - Ensure your app listens on `0.0.0.0`, not `localhost`

### Health Check Fails

1. Ensure your app exposes `/health` endpoint that returns 200 status
2. Check that app listens on `0.0.0.0`, not `localhost`
3. Verify port matches `http_port` in spec (default: 8080)
4. Increase `initial_delay_seconds` in health check config if app takes longer to start

**Example health check in `.do/app.yaml`:**
```yaml
health_check:
  http_path: /health
  initial_delay_seconds: 40
  period_seconds: 10
  timeout_seconds: 5
  success_threshold: 1
  failure_threshold: 3
```

### Process Won't Start

1. **Access console and check supervisord status:**
   ```bash
   supervisorctl status
   ```

2. **View process logs:**
   ```bash
   supervisorctl tail app stderr
   supervisorctl tail app stdout
   ```

3. **Check supervisord configuration:**
   ```bash
   cat /etc/supervisor/conf.d/supervisord.conf
   ```

4. **Common issues:**
   - Incorrect command in supervisord.conf
   - Missing file permissions
   - Dependencies not installed
   - Process exits immediately (check `startsecs` setting)

### Processes Restart Frequently

Check `startsecs` in supervisord.conf - the process must stay running this long to be considered successfully started.

```ini
[program:app]
startsecs=10  # Process must run for 10 seconds to be considered started
```

### Auto-Deploy Not Working

**Problem**: Pushing to GitHub doesn't trigger deployment

**Solution:**
- Check `deploy_on_push: true` in `.do/app.yaml`
- Verify GitHub integration in App Platform console
- Check build logs for errors
- Ensure you're pushing to the correct branch specified in the spec

## Production Considerations

### Security

- **Never commit secrets** to the repository
- Use App Platform environment variables with `type: SECRET` for sensitive data
- Keep dependencies updated regularly
- Use specific version tags in Dockerfile instead of `latest`
- Review and restrict file permissions in your container

### Monitoring

- Use App Platform's built-in metrics for container health
- Configure logging forwarding to centralized logging systems
- Set up alerts for container restarts and health check failures
- Monitor resource usage (CPU, memory) and scale accordingly

### Performance

- Use specific version tags for all dependencies
- Optimize Docker image size by removing unnecessary packages
- Consider using multi-stage builds for smaller images
- Configure appropriate resource limits in app spec

## Local Development

### Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Makefile

```bash
# Build the container
make build

# Run the container
make up

# View logs
make logs

# Stop and remove containers
make down
```

## Next Steps

- **Add Monitoring**: Set up alerts for health check failures in App Platform
- **Configure Logging**: Forward logs to external service (Datadog, Loggly, etc.)
- **Set up Custom Domain**: Add your own domain in App Platform settings
- **Enable SSL**: Free SSL certificates included with App Platform
- **Add Database**: Connect to DigitalOcean Managed Databases if needed
- **CI/CD Integration**: Set up automated testing before deployment

## Resources

- [Supervisord Documentation](http://supervisord.org/)
- [DigitalOcean App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [App Spec Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)
- [App Platform Pricing](https://www.digitalocean.com/pricing/app-platform)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/AppPlatform-Templates/supervisord-appplatform/issues)
- **DigitalOcean Community**: [community.digitalocean.com](https://www.digitalocean.com/community)
- **Support**: [DigitalOcean Support](https://www.digitalocean.com/support/)

---

Happy deploying!
