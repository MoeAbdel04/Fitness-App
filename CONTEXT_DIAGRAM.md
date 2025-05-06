                                              ┌───────────────────────┐   ← Developer & CI: Push code, run tests, build & deploy pipeline
                                              │   Developer / CI      │
                                              │ (GitHub + Actions)    │
                                              └────────────┬──────────┘
                                                           │
                                                           ▼  (1) Push & Build
                                        ┌─────────────────────────────────────┐   ← CI/CD: Lint, tests, security scans, Docker image build
                                        │    CI/CD Pipeline (Docker Build)    │
                                        └─────────────────────────────────────┘
                                                           │
                                                           ▼  (2) Deploy
                               ┌────────────────────────────────────────────────┐   ← Hosting: Runs your container, scales app
                               │   Hosting Platform / Orchestration           │
                               │  (AWS ECS / Heroku / DigitalOcean / k8s)     │
                               └────────────────────────────────────────────────┘
                                                           │
                                                           ▼
                                        ┌─────────────────────────────────┐   ← Ingress: SSL termination & routing
                                        │     Ingress / Reverse Proxy     │
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
  ┌────────────────────────────────────────────┐
  │ • SQLAlchemy ORM ↔ Primary DB (Postgres)  │  ← Persists users, logs, plans
  │ • Sessions → Redis                        │  ← Stores login sessions & cache
  │ • Celery + Redis Broker                   │  ← Background tasks: emails, reminders
  │ • Sentry                                  │  ← Error tracking
  │ • Prometheus / Grafana                    │  ← Metrics & dashboards
  └────────────────────────────────────────────┘
             │                  │                   │
      (G)    │                  │                   │  (H)
─────────────▼──────────  ┌─────▼──────┐   ┌────────▼────────┐
│   Primary DB (Postgres) │  Redis     │   │  AWS S3 (or GCS) │
│ • User data & logs      │  Cache &   │   │ • Exports &      │
│ • Migrations & backups  │  Sessions  │   │   Media storage  │
└─────────────────────────┘  └──────────┘   └─────────────────┘
             │                                    
             │ (I) Email / Notifications           
             ▼                                    
   ┌─────────────────────────┐                       
   │  Email Service          │  ← Sends signup confirmations, resets, reminders  
   │ (SMTP / SendGrid API)   │                       
   └─────────────────────────┘                       
