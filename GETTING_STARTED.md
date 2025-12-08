# Getting Started with Supervisord App Platform Template

This guide will help you get your Supervisord-managed application running on DigitalOcean App Platform.

## What You Get

This template provides a complete, production-ready setup for running multi-process applications:

- **Supervisord Process Manager**: Manages multiple processes in a single container
- **Example Flask Application**: A working web app with health checks
- **Example Background Worker**: Demonstrates running background tasks
- **OpenTelemetry Support**: Optional observability agent integration
- **Multiple Deployment Configurations**: Starter, with-workers, and with-OTEL options

## Deployment Methods

### Method 1: Deploy to DigitalOcean Button (Recommended)

This is the easiest way to get started!

1. Click the "Deploy to DO" button in the README
2. Authorize GitHub access (if needed)
3. Review the configuration
4. Click "Deploy"

The button will:
- Automatically fork the repository to your GitHub account
- Use the `.do/deploy.template.yaml` configuration
- Deploy your app to DigitalOcean App Platform

**Important**: After deployment, you should:
- Replace the example Flask app with your actual application
- Update `config/supervisord.conf` with your processes
- Push changes to trigger auto-deployment

### Method 2: Manual Fork and Deploy

For more control over the setup:

1. **Fork the Repository**
   ```bash
   # Go to GitHub and fork: https://github.com/AppPlatform-Templates/supervisord-appplatform
   # Then clone your fork:
   git clone https://github.com/your-username/supervisord-appplatform.git
   cd supervisord-appplatform
   ```

2. **Customize the Application**
   - Replace `app/app.py` with your application
   - Update `app/requirements.txt` with your dependencies
   - Modify `config/supervisord.conf` for your processes

3. **Update App Spec**
   ```bash
   # Edit .do/examples/starter.yaml and replace AppPlatform-Templates
   sed -i '' 's/AppPlatform-Templates/your-username/g' .do/examples/starter.yaml
   ```

4. **Deploy via doctl**
   ```bash
   doctl apps create --spec .do/examples/starter.yaml
   ```

## Configuration Files Explained

### `.do/deploy.template.yaml`
Used by the "Deploy to DigitalOcean" button. Contains placeholder values that get filled in during deployment.

### `.do/app.yaml`
Main App Platform specification file. Use this for production deployments.

### `.do/examples/starter.yaml`
Basic configuration - single instance with minimal processes (~$12/month).

### `.do/examples/with-otel.yaml`
Includes OpenTelemetry agent for observability (~$18/month).

### `.do/examples/with-workers.yaml`
Enables background worker processes (~$18/month).

## Customizing Your Application

### 1. Replace the Example App

The template includes a simple Flask application. To use your own:

**For Python applications:**
- Replace `app/app.py` with your code
- Update `app/requirements.txt`
- Keep the `/health` endpoint for health checks

**For other languages:**
- Update `Dockerfile` with your runtime (Node.js, Go, etc.)
- Update `config/supervisord.conf` with appropriate commands
- Ensure your app listens on port specified by `PORT` env var

### 2. Configure Your Processes

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

[program:background-worker]
command=python worker.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/app/worker.err.log
stdout_logfile=/var/log/app/worker.out.log
priority=20
```

**Key settings:**
- `priority`: Lower numbers start first
- `autostart`: Start when supervisord starts
- `autorestart`: Restart if process dies
- `command`: Command to run your process

### 3. Enable Optional Features

**OpenTelemetry Agent:**

1. Uncomment OTEL dependencies in `app/requirements.txt`
2. Set environment variables in your App Spec:
   ```yaml
   - key: OTEL_ENABLED
     value: "true"
   - key: OTEL_EXPORTER_OTLP_ENDPOINT
     value: https://your-collector.example.com
   ```

**Background Workers:**

1. Uncomment the `[program:worker]` section in `config/supervisord.conf`
2. Optionally set environment variable to conditionally enable:
   ```yaml
   - key: WORKER_ENABLED
     value: "true"
   ```

## After Deployment

### Access Your Application

```bash
# Get your app URL
doctl apps get <APP_ID> --format LiveURL

# Or visit the DigitalOcean Console
# https://cloud.digitalocean.com/apps
```

### Test the Endpoints

```bash
# Health check
curl https://your-app.ondigitalocean.app/health

# App info
curl https://your-app.ondigitalocean.app/info
```

### View Logs

**Via Console:**
1. Go to your app in DigitalOcean Console
2. Click "Runtime Logs" tab
3. View real-time logs from all processes

**Via doctl:**
```bash
doctl apps logs <APP_ID> --type run --follow
```

### Manage Processes

Access the console to interact with supervisord:

1. Go to your app in DigitalOcean Console
2. Click "Console" tab
3. Run commands:
   ```bash
   # Check status of all processes
   supervisorctl status

   # Restart a process
   supervisorctl restart app

   # View logs
   tail -f /var/log/app/app.out.log
   ```

## Common Scenarios

### Running a Python App with Celery Worker

1. **Update requirements.txt:**
   ```
   Flask==3.0.0
   celery==5.3.4
   redis==5.0.1
   ```

2. **Update supervisord.conf:**
   ```ini
   [program:flask-app]
   command=python app.py
   autostart=true
   autorestart=true

   [program:celery-worker]
   command=celery -A app.celery worker --loglevel=info
   autostart=true
   autorestart=true
   ```

### Running a Node.js App with Background Jobs

1. **Update Dockerfile:**
   ```dockerfile
   FROM node:18-slim

   RUN apt-get update && apt-get install -y supervisor curl && rm -rf /var/lib/apt/lists/*

   WORKDIR /app
   COPY package*.json ./
   COPY . .
   RUN npm install

   COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

   EXPOSE 8080
   CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
   ```

2. **Update supervisord.conf:**
   ```ini
   [program:node-app]
   command=node server.js
   autostart=true
   autorestart=true

   [program:job-processor]
   command=node worker.js
   autostart=true
   autorestart=true
   ```

## Troubleshooting

### Deploy Button Issues

**Problem**: Deploy button gives an error

**Solution**:
- Ensure the repository is public
- Check that `.do/deploy.template.yaml` exists and is valid
- Try forking manually and deploying via doctl

### Health Check Failures

**Problem**: App deploys but health checks fail

**Solution**:
- Ensure `/health` endpoint exists and returns 200
- Check app listens on `0.0.0.0`, not `localhost`
- Verify port matches `http_port` in spec (8080)
- Increase `initial_delay_seconds` if app needs more time

### Process Won't Start

**Problem**: Supervisord starts but your process doesn't

**Solution**:
1. Check supervisord logs:
   ```bash
   supervisorctl tail app stderr
   ```
2. Verify command in supervisord.conf is correct
3. Check file permissions
4. Ensure dependencies are installed

### Auto-Deploy Not Working

**Problem**: Pushing to GitHub doesn't trigger deployment

**Solution**:
- Check `deploy_on_push: true` in App Spec
- Verify GitHub integration in App Platform console
- Check build logs for errors

## Next Steps

1. **Customize Your App**: Replace the example with your actual application
2. **Add Monitoring**: Set up alerts in DigitalOcean Console
3. **Configure Domain**: Add custom domain in App Platform settings
4. **Scale Resources**: Adjust instance size based on your needs
5. **Add Database**: Connect DigitalOcean Managed Database if needed

## Resources

- [Full Documentation](./README.md)
- [Deployment Guide](./DEPLOY.md)
- [Supervisord Documentation](http://supervisord.org/)
- [App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [App Spec Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)

## Need Help?

- **GitHub Issues**: Report bugs or request features
- **DigitalOcean Community**: [community.digitalocean.com](https://www.digitalocean.com/community)
- **Support**: [DigitalOcean Support](https://www.digitalocean.com/support/)

---

Happy building!
