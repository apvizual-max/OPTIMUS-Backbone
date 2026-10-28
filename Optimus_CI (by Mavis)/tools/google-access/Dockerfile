FROM node:22-slim

# Google_Access - one MCP server, one permanent Google credential.
# The credential NEVER enters an image layer: it lives in the mounted volume
# at /data and is read at runtime.

WORKDIR /app
COPY server.mjs /app/server.mjs

ENV GA_DATA_DIR=/data \
    GA_SECRETS_DIR=/secrets \
    GA_PORT=8766 \
    GA_HOST=0.0.0.0

EXPOSE 8766

# The health probe derives its port from GA_PORT, never from a literal.
# Measured defect 2026-10-27: the probe hardcoded 8765 while the container
# ran with GA_PORT=8766 (host port 8765 was already taken by another
# host-native process - measured: python, service "hc-backend"), so the
# container reported "unhealthy" for 9 consecutive intervals while the
# service itself answered HTTP 200 with grant=live. A literal port in the
# health probe is a second source of truth about the same thing.
HEALTHCHECK --interval=60s --timeout=10s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.GA_PORT||8766)+'/health').then(r=>r.json()).then(j=>process.exit(j.grant==='live'?0:1)).catch(()=>process.exit(1))"

CMD ["node", "/app/server.mjs"]
