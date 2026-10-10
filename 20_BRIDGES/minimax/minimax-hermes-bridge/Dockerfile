FROM hermes-mcp-base:latest

LABEL optimus.bridge="minimax-hermes-bridge"
LABEL optimus.target="hermes"
LABEL optimus.role="doctor+delegate+centralize"
LABEL optimus.author="mavis"

WORKDIR /app
COPY shared/ /app/shared/
COPY minimax-hermes-bridge/ /app/bridge/
COPY minimax-hermes-bridge/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

ENV BRIDGE_PORT=8801 \
    PYTHONUNBUFFERED=1

EXPOSE 8801
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8801/health',timeout=4).status==200 else 1)"

CMD ["python", "/app/bridge/minimax_hermes_bridge.py"]
