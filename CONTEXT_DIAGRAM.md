                                              ┌───────────────────────┐
                                              │   Developer / CI      │ ← Push code, run tests, build & deploy pipeline
                                              │ (GitHub + Actions)    │
                                              └────────────┬──────────┘
                                                           │
                                                           ▼  (1) Push & Build
                                        ┌─────────────────────────────────────┐
                                        │    CI/CD Pipeline (Docker Build)    │ ← Lint, tests, security scans, Docker image build
                                        └─────────────────────────────────────┘
                                                           │
                                                           ▼  (2) Deploy
                               ┌────────────────────────────────────────────────┐
                               │   Hosting Platform / Orchestration           │ ← Runs your container, scales app
                               │  (AWS ECS / Heroku / DigitalOcean / k8s)     │
                               └────────────────────────────────────────────────┘
                                                           │
                                                           ▼
                                        ┌─────────────────────────────────┐
                                        │     Ingress / Reverse Proxy     │ ← SSL termination & routing
                                        │   (Nginx / Cloudflare + SSL)    │
                                        └─────────────────────────────────┘
                                                           │ HTTPS
                                                           ▼
    +────────────────┐         +───────────────────────────────┐          +──────────────────────────┐
    │    End User    │──(A)──▶│      Fit Fusion App           │──(B)───▶│     OpenAI Chat API       │
    │ (Browser/SPA)  │◀──(E)──│  (Flask + Jinja + REST + WS)   │◀──(F)───│   (gpt-3.5-turbo)          │
    └────────────────┘         └─────────┬─────────┬────────────┘          └──────────────────────────┘
            ▲                    renders │         │ proxies calls           ▲
            │                            ▼         ▼                       │
         (C)│                    +─────────────────────+             (D)   │
            │── fetch CSS/JS/Icons │     Static Assets   │◀───────────────┘
    +─────────────────+            │ (Templates, CSS, JS)│   ← Served via CDN for performance
    │    Static CDN   │            +─────────────────────+   
    │ (Bootstrap,     │
    │  Bootstrap Icons)│
    +─────────────────+

  Inside the App:
  ┌─────────────────────────────────────────────┐
  │ • SQLAlchemy ORM ↔ Primary DB (Postgres)   │ ← Persists users, workout logs & plans
  │ • Sessions         ↔ Redis                 │ ← Stores login sessions & powers Celery
  │ • Celery + Broker  (Redis)                 │ ← Runs background tasks (emails, reminders)
  │ • Sentry                                   │ ← Real-time error tracking
  │ • Prometheus / Grafana                     │ ← Metrics collection & dashboards
  └─────────────────────────────────────────────┘
             │                   │                   │
      ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐
      │  Primary    │     │   Redis      │     │   AWS S3     │
      │    DB       │     │ (Cache &     │     │ (Media &     │
      │ (Postgres)  │     │  Broker)     │     │  Exports)    │
      └─────────────┘     └─────────────┘     └─────────────┘
             │                                     │
             │                                     │
             ▼                                     ▼
      ┌────────────────────────────────────────────────┐
      │            Email Service                      │ ← Sends signup confirmations, resets & reminders
      │         (SMTP / SendGrid API)                 │
      └────────────────────────────────────────────────┘


         
