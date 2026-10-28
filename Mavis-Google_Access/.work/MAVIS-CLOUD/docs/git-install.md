# Git — configurări de mediu și chei

## Ce e necesar pe orice mașină

```bash
git --version
gh --version          # opțional, pentru operațiuni GitHub
node --version        # necesar: motorul de CV rulează în Node
python3 --version
```

## Identitate

```bash
git config --global user.name  "Alexandru Popescu"
git config --global user.email "alex@ap-id.ro"
git config --global init.defaultBranch main
```

## Chei — NU în repo

| Cheie | Unde stă | Ce deschide |
|---|---|---|
| `GITHUB_TOKEN` | manager de secrete | commit + push + API |
| `JULES_API_KEY` | manager de secrete | apeluri Jules |
| `GOOGLE_EMAIL` | manager de secrete | LinkedIn |
| `LINKEDIN_PASSWORD` | manager de secrete | LinkedIn |

**Regulă:** `.gitignore` acoperă `*.env`, `*token*`, `*secret*`, `oauth.json`,
`*.pem`, `*.key`. Workflow-ul `Verificare` **blochează build-ul** dacă apare
un fișier de secret. Nu se negociază.

## Credential helper — corect

```bash
# FALS: funcția se numește gh și apelează gh → recursie infinită → HTTP 431
git config --global credential.helper '!gh() { echo username=x-access-token; echo password=$(gh auth token); }; gh'

# CORECT: alt nume, cale plină
gh=/cale/catre/gh
git config --global credential.helper "!f() { echo username=x-access-token; echo password=$($gh auth token); }; f"
```

## SSL în sandbox

```bash
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt
git config --global http.sslVerify false   # proxy de sandbox; opensl confirmă "Verify return code: 0"
```
