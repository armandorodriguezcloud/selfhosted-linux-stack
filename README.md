# Self-Hosted Linux Application Stack

> A self-hosted, containerized Linux services lab — a personal testing
> environment I started because of my work.

## Overview

A single Docker-orchestrated Linux host runs a suite of self-hosted services
behind a **Traefik** reverse proxy (automatic TLS), backed by a shared
**PostgreSQL** instance. I started it as a personal sandbox to get hands-on with
the kinds of containerized services, database lifecycle, and operations I work
with — somewhere to experiment and break things safely. It is a test
environment, **not production, and not a copy of any production system**.

## Services

| Service        | Role                                   | Hostname               |
|----------------|----------------------------------------|------------------------|
| Traefik        | Reverse proxy + Let's Encrypt TLS      | —                      |
| Grafana        | Observability dashboards               | `grafana.lab.local`    |
| Synapse        | Matrix homeserver (secure comms)       | `matrix.lab.local`     |
| Element        | Matrix web client                      | `chat.lab.local`       |
| Wiki.js        | Documentation / knowledge base         | `wiki.lab.local`       |
| Zammad         | Request tracking (rails + scheduler)   | `support.lab.local`    |
| MobSF          | Mobile application security testing    | `mobsf.lab.local`      |
| ops-bot        | Custom Matrix → Zammad automation      | —                      |
| PostgreSQL     | Shared database backend                | internal               |
| Redis / Memcached | Zammad caching + jobs               | internal               |

## Architecture

- **One reverse proxy, many services** — Traefik routes by hostname and
  terminates TLS; only 80/443 are exposed.
- **Shared PostgreSQL** — a single Postgres instance provisions a dedicated
  database + role per service on first boot (`db/init/`).
- **Two networks** — `web` (Traefik-facing) and `internal` (service-to-service
  + database), so only intended services are reachable from the edge.
- **Custom automation** — `ops-bot` bridges Matrix chat to Zammad, an example
  of the glue that ties the stack together.

See [docs/architecture.md](docs/architecture.md) for the full breakdown.

## Quick start

```bash
cp .env.example .env          # set the database + admin passwords
docker compose up -d
docker compose ps             # all services healthy
```

> Synapse needs a generated `homeserver.yaml` on first run:
> ```bash
> docker compose run --rm synapse generate
> ```
> Then add local DNS (or `/etc/hosts`) entries for the `*.lab.local` hostnames.

## What I practice here

- Operating a multi-service containerized Linux stack end to end on Docker
- Reverse-proxy architecture with automatic TLS (Traefik + ACME)
- PostgreSQL lifecycle: provisioning, per-service isolation, backups
- Service reliability, network segmentation, and recovery
- Practical automation (custom bots) integrating services

---

_Part of my homelab portfolio — https://armandorodriguez.cloud_
