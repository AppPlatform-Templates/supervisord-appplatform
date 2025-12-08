# Deployment Guide

Step-by-step guide to deploy your Supervisord application on DigitalOcean App Platform.

## Prerequisites

Before you begin, ensure you have:

1. **DigitalOcean Account**: [Sign up here](https://cloud.digitalocean.com/registrations/new)
2. **doctl CLI**: [Installation guide](https://docs.digitalocean.com/reference/doctl/how-to/install/)
3. **GitHub Account**: For source code repository
4. **Git**: Installed on your local machine

## Step 1: Authenticate doctl

```bash
# Authenticate with DigitalOcean
doctl auth init

# Verify authentication
doctl account get
```

## Step 2: Fork or Clone the Repository

### Option A: Fork the Repository (Recommended)

1. Go to the repository on GitHub
2. Click the "Fork" button in the top-right corner
3. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/supervisord-appplatform.git
   cd supervisord-appplatform
   ```

### Option B: Use as Template

1. Click "Use this template" on GitHub
2. Create a new repository
3. Clone your new repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/your-repo-name.git
   cd your-repo-name
   ```

## Step 3: Customize the Application

### Update App Specification

Edit the `.do/examples/starter.yaml` file to point to your repository:

```bash
# Replace AppPlatform-Templates with your actual username
sed -i '' 's/AppPlatform-Templates/your-username/g' .do/examples/starter.yaml
```

Or manually edit the file:

```yaml
services:
  - name: supervisord-service
    github:
      repo: your-username/supervisord-appplatform  # Update this line
      branch: main
      deploy_on_push: true
```

### (Optional) Customize Your Application

Replace the example Flask app with your own:

1. **Replace `app/app.py`** with your application code
2. **Update `app/requirements.txt`** with your dependencies
3. **Modify `config/supervisord.conf`** to define your processes

Example: Adding a background worker

```ini
# Uncomment in supervisord.conf
[program:worker]
command=python worker.py
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/app/worker.err.log
stdout_logfile=/var/log/app/worker.out.log
priority=15
```

## Step 4: Push to GitHub

Commit and push your changes:

```bash
git add .
git commit -m "Customize supervisord template for my app"
git push origin main
```

## Step 5: Deploy to App Platform

### Quick Deploy (Starter Configuration)

```bash
doctl apps create --spec .do/examples/starter.yaml
```

### Deploy with OpenTelemetry

If you want to enable OpenTelemetry:

1. Update `.do/examples/with-otel.yaml` with your GitHub repo
2. Configure your OTEL endpoint
3. Deploy:
   ```bash
   doctl apps create --spec .do/examples/with-otel.yaml
   ```

### Custom Deployment

Use the main spec file:

```bash
# Update .do/app.yaml with your configuration
doctl apps create --spec .do/app.yaml
```

## Step 6: Monitor Deployment

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

## Step 7: Verify Multi-Process Setup

### Check Health Endpoint

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

### View Process Information

```bash
curl https://your-app-url.ondigitalocean.app/info
```

This will show environment variables and process manager info.

## Step 8: Configure GitHub Auto-Deploy

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

## Updating Your App

### Update via CLI

```bash
# Update app configuration
doctl apps update <APP_ID> --spec .do/app.yaml

# Trigger manual deployment
doctl apps create-deployment <APP_ID>
```

### Update via Console

1. Go to [DigitalOcean Control Panel](https://cloud.digitalocean.com/apps)
2. Select your app
3. Click "Settings" > "App Spec"
4. Edit the YAML configuration
5. Click "Save" to redeploy

## Environment Variables

### Add Environment Variables

```bash
# Using doctl
doctl apps update <APP_ID> --spec .do/app.yaml
```

Or via the console:
1. Navigate to your app
2. Go to "Settings" > "Environment Variables"
3. Add/edit variables
4. Click "Save" (triggers redeployment)

### Common Environment Variables

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

## Managing Processes

### Access Console

1. Go to your app in the DigitalOcean console
2. Click "Console" tab
3. Run supervisorctl commands:

```bash
# View all processes
supervisorctl status

# Restart a process
supervisorctl restart app

# Stop a process
supervisorctl stop worker

# Start a process
supervisorctl start worker

# View logs
tail -f /var/log/app/app.out.log
```

## Scaling

### Vertical Scaling (More Resources)

Update instance size in your spec:

```yaml
instance_size_slug: apps-s-2vcpu-4gb  # Upgrade to 2 vCPU, 4GB RAM
```

Then update:
```bash
doctl apps update <APP_ID> --spec .do/app.yaml
```

### Horizontal Scaling (More Instances)

**Note**: Supervisord manages processes within a single container. For horizontal scaling across multiple containers, consider splitting services in your App Platform spec.

## Troubleshooting

### Deployment Fails

1. Check build logs:
   ```bash
   doctl apps logs <APP_ID> --type build
   ```

2. Check deployment logs:
   ```bash
   doctl apps logs <APP_ID> --type deploy
   ```

3. Common issues:
   - Invalid GitHub repository path
   - Missing dependencies in requirements.txt
   - Port mismatch (ensure app listens on PORT environment variable)

### Health Check Fails

1. Ensure your app exposes `/health` endpoint
2. Check that app listens on `0.0.0.0`, not `localhost`
3. Verify port matches `http_port` in spec (default: 8080)
4. Increase `initial_delay_seconds` if app takes longer to start

### Process Won't Start

1. Access console and check supervisord status:
   ```bash
   supervisorctl status
   ```

2. View process logs:
   ```bash
   supervisorctl tail app stderr
   supervisorctl tail app stdout
   ```

3. Check supervisord configuration:
   ```bash
   cat /etc/supervisor/conf.d/supervisord.conf
   ```

## Cost Optimization

### Development/Testing

Use the smallest instance:
```yaml
instance_size_slug: apps-s-1vcpu-1gb  # ~$12/month
```

### Production

Choose based on your needs:
- **Basic**: `apps-s-1vcpu-1gb` - ~$12/month
- **Standard**: `apps-s-1vcpu-2gb` - ~$18/month
- **Performance**: `apps-s-2vcpu-4gb` - ~$36/month

### Suspend Development Apps

Suspend apps when not in use:
```bash
# Suspend app
doctl apps update <APP_ID> --spec .do/app.yaml  # Set replicas to 0

# Resume app
doctl apps create-deployment <APP_ID>
```

## Next Steps

- **Add Monitoring**: Set up alerts for health check failures
- **Configure Logging**: Forward logs to external service
- **Set up Custom Domain**: Add your own domain in App Platform settings
- **Enable SSL**: Free SSL certificates included with App Platform
- **Add Database**: Connect to DigitalOcean Managed Databases if needed

## Resources

- [App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [doctl Reference](https://docs.digitalocean.com/reference/doctl/)
- [Supervisord Documentation](http://supervisord.org/)
- [App Spec Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **DigitalOcean Community**: [community.digitalocean.com](https://www.digitalocean.com/community)
- **Support**: [DigitalOcean Support](https://www.digitalocean.com/support/)

---

Happy deploying!
