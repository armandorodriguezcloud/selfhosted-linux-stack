# Architecture

This is a personal testing lab, a sandbox where I get hands-on with a
multi-service containerized stack. It is **not production and does not replicate
a production environment**. It is intentionally multi-service so I can practice
the operational concerns I care about: reverse-proxy routing, TLS, a shared
database with per-service isolation, network segmentation, automation, and backups.

```
                         Internet / LAN
                               │  :80 / :443
                        ┌──────▼───────┐
                        │   Traefik    │  TLS (Let's Encrypt), host routing
                        └──────┬───────┘
            web network ┌──────┼───────────────┬──────────┬─────────┐
                        ▼      ▼               ▼          ▼         ▼
                     Grafana  Synapse/Element  Wiki.js   Zammad     MobSF
                        │      │               │          │
         internal net   └──────┴───────┬───────┴──────────┘
                                       ▼
                                  PostgreSQL  (grafana / wikijs / zammad DBs)
                                  Redis + Memcached (Zammad)
                                       ▲
                                    ops-bot  (Matrix -> Zammad automation)
```

## Design decisions

| Concern            | Approach |
|--------------------|----------|
| Ingress / TLS      | Single Traefik entrypoint; ACME TLS challenge; services opt in via labels |
| Database           | One PostgreSQL; `db/init/` creates an isolated DB + role per service |
| Segmentation       | `web` network for edge-facing services, `internal` for DB/cache + bots |
| Secrets            | `.env` (gitignored); `.env.example` documents required values |
| State              | Named volumes per service; included in the backup job |
| Automation         | `ops-bot` shows service-to-service integration via APIs |

## Operations

- **Backups**, volumes + `pg_dump` per database on a nightly schedule
  (the dedicated [backup-dr-lab](https://github.com/armandorodriguezcloud/backup-dr-lab)
  repo covers the PBS/Veeam side).
- **Monitoring**, Grafana here is the in-stack dashboard layer; cluster-wide
  metrics live in
  [observability-stack](https://github.com/armandorodriguezcloud/observability-stack).
- **Upgrades**, image tags are pinned; bump + `docker compose up -d` per
  service, validating health before moving on.

## Why it's built this way

These are the patterns I want hands-on reps with, a reverse proxy in front of
containerized services, centralized TLS, isolated data stores, and custom
automation. It's a learning environment to go deeper on my own time, not a
production system.
