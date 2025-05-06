                                             ┌───────────────────────┐        ┌─────────────────────────────────────────────┐
                                             │   Developer / CI      │        │               Inside the App:              │
                                             │ (GitHub + Actions)    │        │ • SQLAlchemy ORM ↔ Primary DB (Postgres)   │
                                             └────────────┬──────────┘        │   ← Persists users, workout logs & plans   │
                                                          │                   │ • Sessions         ↔ Redis                 │
                                                          ▼                   │   ← Stores login sessions & powers Celery  │
                                       ┌─────────────────────────────────────┐  │ • Celery + Broker  (Redis)                 │
                                       │    CI/CD Pipeline (Docker Build)    │  │   ← Runs background tasks (emails, reminders)│
                                       └─────────────────────────────────────┘  │ • Sentry                                   │
                                                          │                   │   ← Real-time error tracking              │
                                                          ▼                   │ • Prometheus / Grafana                     │
                              ┌────────────────────────────────────────────────┐  │   ← Metrics collection & dashboards       │
                              │   Hosting Platform / Orchestration           │  └─────────────────────────────────────────────┘
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

      ↓  
      └────────────────────────────────────────────────┐
                                                   │ Email Service                      │
                                                   │ (SMTP / SendGrid API)              │
                                                   │ ← Sends signup conf., resets, reminders │
                                                   └────────────────────────────────────────────────┘



         
