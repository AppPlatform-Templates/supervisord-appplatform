# OpenTelemetry Production Configuration

## TL;DR

**Your current setup works in production as-is!** 

- Flask app → `localhost:4318` → OTEL Collector → logs to console
- Both run in the same container, so `localhost` works fine
- Deploy directly to App Platform - no changes needed

Only configure the sections below if you want to send telemetry to an external observability platform (Datadog, Grafana, etc.).

---

## Current Setup (Works in Production)

```
Container:
  Flask App (port 8080) → localhost:4318 → OTEL Collector → console logs
```

This is perfect for getting started. Traces, metrics, and logs appear in your container logs.

---

## Send to External Platform (Optional)

If you want traces/metrics in Datadog, Grafana, etc., follow these 2 steps:

### Step 1: Add Environment Variables

In App Platform, add these env vars:

```bash
OTEL_COLLECTOR_ENDPOINT=https://your-backend.com:4317
OTEL_COLLECTOR_INSECURE=false
```

### Step 2: Update Collector Config

Edit `config/otel-collector-config.yaml`, change exporters from `[logging]` to `[logging, otlp]`:

```yaml
service:
  pipelines:
    traces:
      exporters: [logging, otlp]  # was: [logging]
    metrics:
      exporters: [logging, otlp]  # was: [logging]
    logs:
      exporters: [logging, otlp]  # was: [logging]
```

That's it! Rebuild and deploy.

---

## Popular Backends

**Grafana Cloud:**
```bash
OTEL_COLLECTOR_ENDPOINT=https://otlp-gateway-prod-us-central-0.grafana.net:4317
OTEL_COLLECTOR_INSECURE=false
```
Add auth in collector config: `authorization: "Basic ${env:OTEL_API_KEY}"`

**Datadog:**
```bash
OTEL_COLLECTOR_ENDPOINT=https://http-intake.logs.datadoghq.com:443
OTEL_COLLECTOR_INSECURE=false
```

**Honeycomb:**
```bash
OTEL_COLLECTOR_ENDPOINT=https://api.honeycomb.io:443
OTEL_COLLECTOR_INSECURE=false
```
Add header in collector config: `x-honeycomb-team: "${env:OTEL_API_KEY}"`

**Jaeger (self-hosted):**
```bash
OTEL_COLLECTOR_ENDPOINT=http://jaeger-collector:4317
OTEL_COLLECTOR_INSECURE=true
```
