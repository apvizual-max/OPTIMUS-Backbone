# Sub-Skill: exec-searxng

* **Description:** Custom local SearXNG metasearch engine deployment guide. Explains the local docker-compose configuration running on port 8081 for privacy-focused web searches.

---

# SearXNG Metasearch Engine
This is the documentation for the local SearXNG metasearch instance deployed on this machine.

## Configuration Details
* **Port:** 8081 (mapped to container port 8080)
* **Base URL:** `http://localhost:8081/`
* **Restart Policy:** `unless-stopped`
* **Configuration Volume:** `./searxng-config:/etc/searxng`
* **DNS Settings:** Google DNS (`8.8.8.8`, `8.8.4.4`)

## How to Manage
Start the service using Docker Compose:
```bash
docker-compose up -d
```
Stop the service:
```bash
docker-compose down
```