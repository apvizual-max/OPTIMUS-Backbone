FROM hermes-mcp-base:latest

LABEL optimus.bridge="minimax-antigravity-bridge"
LABEL optimus.target="antigravity"
LABEL optimus.role="council+delegate+memory-reader"
LABEL optimus.author="mavis"

WORKDIR /app
COPY shared/ /app/shared/
COPY minimax-antigravity-bridge/ /app/bridge/
COPY minimax-antigravity-bridge/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV BRIDGE_PORT=8802 \
    PYTHONUNBUFFERED=1

EXPOSE 8802
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8802/health',timeout=4).status==200 else 1)"

CMD ["python", "/app/bridge/minimax_antigravity_bridge.py"]
