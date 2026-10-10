# =============================================================================
#  mavis-sentinel-hub
#  Local deployment image for the SENTINEL Command Center.
#  Built by Mavis for SENTINEL_PRIME.
#
#  The image is deliberately tiny and deliberately empty of application data.
#  It contains the web plane and nothing else. The dashboard, the corpus and
#  every measured value live on the Windows host, because the things it
#  measures are Windows facts. Baking a copy of the app in here would create
#  a second source of truth that silently diverges from the one that is
#  actually measured - and a dashboard that reports numbers nobody measured is
#  worse than no dashboard.
#
#  This is the same shape a public deployment takes. When the system goes
#  public, the change is a TLS block, a real hostname and an image tag - not
#  a different application.
# =============================================================================
FROM nginx:alpine

LABEL org.opencontainers.image.title="mavis-sentinel-hub" \
      org.opencontainers.image.description="Local deployment front for the SENTINEL Command Center" \
      org.opencontainers.image.authors="Mavis (MiniMax Code agent) for Popy" \
      org.opencontainers.image.licenses="UNLICENSED" \
      sentinel.role="deployment-front" \
      sentinel.public="false"

# The routing table is baked in, so the container is self-contained: it cannot
# be half-configured by a file that happens to be missing on the host.
#
# NOTE, because it cost one build: do NOT follow this with
# `RUN rm -f /etc/nginx/conf.d/default.conf`. It reads like tidying up the
# stock file, but COPY has already OVERWRITTEN the stock file at this exact
# path, so the rm deletes THIS project's config and leaves nginx with no
# server block at all - which starts cleanly and then 404s everything, a
# silent failure that looks like a routing bug in the host. nginx:alpine's
# entrypoint does not rewrite default.conf when one is present, so there is
# nothing to clean up.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Liveness of the GATEWAY, not of the app behind it. The orchestrator asks
# /readyz separately for that, because a health check that only ever asks the
# app cannot tell a dead gateway from a dead app.
HEALTHCHECK --interval=20s --timeout=4s --start-period=8s --retries=3 \
    CMD wget -qO- http://127.0.0.1/healthz >/dev/null 2>&1 || exit 1

EXPOSE 80
