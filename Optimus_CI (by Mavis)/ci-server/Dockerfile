# Mavis-Optimus-CI - serverul de Continuous Integration al proiectului Optimus CI.
#
# CE ESTE: containerul care tine toata data git locala a proiectului, o
# sincronizeaza cu GitHub si impinge doar cu acordul lui Popy.
#
# DE CE EXISTA: mai multi agenti lucreaza simultan pe acelasi repo (Mavis Cloud,
# Jules prin CD, Antigravity). Daca fiecare face push cand vrea, istoricul se
# rupe si apare conflictul pe care nimeni nu-l stie. Aici exista O poarta:
#   1. GitHub trebuie sa fie CURAT si UNITAR (o ramura main, zero PR-uri).
#   2. Altfel motorul NU face nimic si raporteaza de ce.
#   3. Local, totul e autonom: fetch, integrare, commit, mereu pe main.
#   4. Push-ul cere acordul lui Popy (marker PUSH-ACORD) si nimic altceva.
#
# PORTELE (scriptele .ps1 ale proiectului) ruleaza aici cu PowerShell 7, ca
# poarta sa fie aceeasi in host si in container - nu doua implementari.

FROM node:22-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates curl tzdata procps less \
    && rm -rf /var/lib/apt/lists/*

# PowerShell 7: portile proiectului sunt scripturi .ps1.
RUN curl -fsSL https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -o /tmp/pmp.deb \
    && dpkg -i /tmp/pmp.deb && rm -f /tmp/pmp.deb \
    && apt-get update && apt-get install -y --no-install-recommends powershell \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/pwsh /usr/local/bin/powershell

WORKDIR /opt/optimus-ci
COPY engine/ /opt/optimus-ci/engine/
COPY hooks/ /opt/optimus-ci/hooks/
COPY gate/ /opt/optimus-ci/gate/
COPY gitconfig /etc/gitconfig
RUN chmod 0755 /opt/optimus-ci/engine/entrypoint.sh

ENV CI_PROJECT_DIR=/workspace/project \
    CI_GITDATA_DIR=/workspace/gitdata \
    CI_SECRETS_DIR=/secrets \
    CI_GA_DATA_DIR=/ga-data \
    CI_GATE_DIR=/workspace/gate \
    CI_EVIDENCE_DIR=/workspace/gitdata/evidence \
    CI_API_PORT=8790 \
    CI_GH_OWNER=apvizual-max \
    MAVIS_SECRET_SCANNER=/workspace/project/scripts/scan-staged-secrets.ps1 \
    MAVIS_PUSH_GATE=/workspace/gate/pre-push \
    MAVIS_GITDIR=/workspace/gitdata/repo \
    NODE_ENV=production

EXPOSE 8790

HEALTHCHECK --interval=30s --timeout=8s --start-period=15s --retries=3 \
    CMD node /opt/optimus-ci/engine/cli.mjs ping > /dev/null || exit 1

ENTRYPOINT ["/opt/optimus-ci/engine/entrypoint.sh"]
CMD ["node", "/opt/optimus-ci/engine/cli.mjs", "serve"]
