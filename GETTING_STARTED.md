# Getting Started with Supervisord App Platform Template

This guide will help you get your Supervisord-managed application running on DigitalOcean App Platform.

## What You Get

This template provides a complete, production-ready setup for running multi-process applications:

- **Supervisord Process Manager**: Manages multiple processes in a single container
- **Example Flask Application**: A working web app with health checks
- **OpenTelemetry Collector**: Observability sidecar for traces, metrics, and logs

## Deployment Methods

### Method 1: Deploy to DigitalOcean Button (Quickest)

This is the fastest way to see the template in action!

1. Click the "Deploy to DO" button in the README
2. Review the configuration
3. Click "Create App"

The button will:
- Deploy the app directly from the template repository
- Use the `.do/deploy.template.yaml` configuration
- Create a running instance on DigitalOcean App Platform

**Important**: This deploys from the template repo, not your own fork. To customize:
1. Fork the repository to your GitHub account
2. Update the app settings in App Platform to point to your fork
3. Customize `app/app.py` and `config/supervisord.conf`
4. Push changes to your fork to trigger deployments

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
   - Modify `config/supervisord.conf` to add additional processes if needed

3. **Update App Spec**
   ```bash
   # Edit .do/app.yaml and replace AppPlatform-Templates
   sed -i '' 's/AppPlatform-Templates/your-username/g' .do/app.yaml
   ```

4. **Deploy via doctl**
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

## Configuration Files Explained

### `.do/app.yaml`
Main App Platform specification file. Defines the service configuration, GitHub repo, environment variables, and instance size.

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

### 2. Understand the Configuration

The template runs two processes managed by supervisord:
- **app**: Your main Flask application (or replace with your own)
- **otel-collector**: OpenTelemetry Collector for observability

Both processes are configured in `config/supervisord.conf`:
- `priority`: Lower numbers start first (otel-collector=5, app=10)
- `autostart`: Processes start when supervisord starts
- `autorestart`: Processes restart automatically if they crash
- `stdout_logfile=/dev/fd/1`: Logs are sent to stdout for App Platform

### 3. Configure OpenTelemetry (Optional)

The OpenTelemetry Collector is enabled by default. To send data to your own collector:

Set the endpoint in `.do/app.yaml`:
```yaml
- key: OTEL_EXPORTER_OTLP_ENDPOINT
  value: https://your-collector.example.com:4318
  scope: RUN_TIME
```

Use port `4318` for HTTP or `4317` for gRPC. See [OTEL_PRODUCTION.md](OTEL_PRODUCTION.md) for backend-specific examples.

To disable OTEL, remove the `[program:otel-collector]` section from `config/supervisord.conf`.

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
