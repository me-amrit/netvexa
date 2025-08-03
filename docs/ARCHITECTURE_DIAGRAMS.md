# NETVEXA Architecture Diagrams

## 1. System Components Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              NETVEXA Platform                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │   Public Site   │  │   Admin App     │  │   Embeddable Widget     │  │
│  │  (Homepage)     │  │  (Dashboard)    │  │   (Customer Sites)      │  │
│  │                 │  │                 │  │                          │  │
│  │  Next.js SSR    │  │  React SPA      │  │  Vanilla JS (~10KB)     │  │
│  │  Port: 3001     │  │  Port: 3000     │  │  CDN Delivered          │  │
│  │  netvexa.com    │  │  app.netvexa.com│  │  customer-site.com      │  │
│  └─────────────────┘  └─────────────────┘  └──────────────────────────┘  │
│           │                    │                         │                  │
│           └────────────────────┴─────────────────────────┘                  │
│                                │                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Backend API (FastAPI)                          │  │
│  │                         Port: 8000                                    │  │
│  │                                                                       │  │
│  │  • Authentication    • Agent Management    • Knowledge Processing     │  │
│  │  • Billing          • Chat/WebSocket      • RAG Engine              │  │
│  │  • Usage Tracking   • Analytics           • LLM Integration         │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                │                                            │
│  ┌─────────────────────┐  ┌───────────────┐  ┌────────────────────────┐  │
│  │   PostgreSQL + pgvector │  │     Redis     │  │         S3            │  │
│  │   • User Data          │  │  • Cache      │  │  • Documents          │  │
│  │   • Embeddings         │  │  • Sessions   │  │  • Static Assets      │  │
│  │   • Conversations      │  │  • Rate Limit │  │  • Backups            │  │
│  └─────────────────────┘  └───────────────┘  └────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Request Flow Architecture

### A. Chat Widget Initialization

```
Customer Website                    CDN                         Backend
     │                              │                              │
     ├─[1]─Load Widget Script──────>│                              │
     │<────────Widget JS (10KB)─────┤                              │
     │                              │                              │
     ├─[2]─Initialize Widget────────┼──────────────────────────────>│
     │                              │                         [3] Validate Agent
     │                              │                              │
     │<─────────────────────────────┼──────Agent Config───────────┤
     │                              │                              │
     ├─[4]─Open WebSocket───────────┼──────────────────────────────>│
     │<─────────────────────────────┼────Connection Established────┤
     │                              │                              │
```

### B. Message Processing Flow

```
User Input ──> Widget ──> WebSocket ──> API Gateway ──> Backend
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ Rate Limiter    │
                                    └────────┬────────┘
                                             ▼
                                    ┌─────────────────┐
                                    │ Tenant Context  │
                                    └────────┬────────┘
                                             ▼
                                    ┌─────────────────┐
                                    │ Message Queue   │
                                    └────────┬────────┘
                                             ▼
                        ┌────────────────────┴────────────────────┐
                        ▼                                         ▼
              ┌─────────────────┐                      ┌─────────────────┐
              │ Semantic Cache  │                      │  RAG Pipeline   │
              └────────┬────────┘                      └────────┬────────┘
                       │                                         │
                       ▼                                         ▼
              ┌─────────────────┐                      ┌─────────────────┐
              │ Return Cached   │                      │ Vector Search   │
              └─────────────────┘                      └────────┬────────┘
                                                                │
                                                                ▼
                                                       ┌─────────────────┐
                                                       │ Context Builder │
                                                       └────────┬────────┘
                                                                │
                                                                ▼
                                                       ┌─────────────────┐
                                                       │ LLM Provider    │
                                                       └────────┬────────┘
                                                                │
                                                                ▼
                                                       ┌─────────────────┐
                                                       │ Stream Response │
                                                       └─────────────────┘
```

## 3. Multi-Tenant Data Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PostgreSQL Database                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Shared Tables                         │  │
│  │  • users (with tenant_id)                              │  │
│  │  • agents (with tenant_id)                             │  │
│  │  • subscriptions (with tenant_id)                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Row Level Security (RLS)                    │  │
│  │  All queries automatically filtered by tenant_id         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 Tenant Isolation                         │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  Starter/Growth:     Shared tables with RLS             │  │
│  │  Professional:       Dedicated schema                   │  │
│  │  Business:           Dedicated database                 │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Deployment Architecture (AWS)

```
┌─────────────────────────────────────────────────────────────────────┐
│                           AWS Cloud                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐     ┌──────────────────────────────────────┐ │
│  │   Route 53      │     │         CloudFront CDN               │ │
│  │                 │     │  • Widget files                      │ │
│  │ netvexa.com     │────>│  • Static assets                    │ │
│  │ *.netvexa.com   │     │  • Global edge locations            │ │
│  └─────────────────┘     └──────────────────────────────────────┘ │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    VPC (10.0.0.0/16)                        │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │  │
│  │  │ Public Subnet  │  │ Public Subnet  │  │   NAT        │ │  │
│  │  │ (10.0.1.0/24) │  │ (10.0.2.0/24) │  │   Gateway    │ │  │
│  │  │                │  │                │  │              │ │  │
│  │  │  ALB          │  │  ALB          │  └──────┬───────┘ │  │
│  │  └────────┬───────┘  └────────┬───────┘         │         │  │
│  │           │                    │                  │         │  │
│  │  ┌────────▼────────────────────▼─────────────────▼──────┐ │  │
│  │  │            Private Subnet (10.0.10.0/24)             │ │  │
│  │  │                                                       │ │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │ │  │
│  │  │  │ ECS Fargate │  │ ECS Fargate │  │ ECS Fargate │ │ │  │
│  │  │  │   Task 1    │  │   Task 2    │  │   Task N    │ │ │  │
│  │  │  │  (Backend)  │  │  (Backend)  │  │  (Backend)  │ │ │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘ │ │  │
│  │  │                                                       │ │  │
│  │  └───────────────────────────────────────────────────────┘ │  │
│  │                                                              │  │
│  │  ┌────────────────────────────────────────────────────────┐ │  │
│  │  │            Private Subnet (10.0.20.0/24)               │ │  │
│  │  │                                                         │ │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │  │
│  │  │  │ RDS Primary  │  │ RDS Standby  │  │ ElastiCache │ │ │  │
│  │  │  │ PostgreSQL   │  │ PostgreSQL   │  │   Redis     │ │ │  │
│  │  │  │ + pgvector   │  │ Multi-AZ     │  │   Cluster   │ │ │  │
│  │  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │  │
│  │  │                                                         │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    Supporting Services                       │  │
│  │                                                              │  │
│  │  • S3 Buckets (documents, backups, static assets)          │  │
│  │  • Lambda Functions (async processing)                      │  │
│  │  • SQS Queues (job processing)                             │  │
│  │  • CloudWatch (monitoring, logs)                           │  │
│  │  • Secrets Manager (API keys, credentials)                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 5. Scaling Strategy

### Horizontal Scaling Points

```
                Load Increases
                      │
                      ▼
        ┌─────────────────────────┐
        │   CloudWatch Alarms     │
        │   • CPU > 70%          │
        │   • Memory > 80%       │
        │   • Requests > 1000/min│
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐        ┌────────────────┐
│ ECS Service   │        │ Read Replicas  │
│ Auto Scaling  │        │ Auto Scaling   │
│               │        │                │
│ Min: 2 tasks  │        │ Min: 1 replica │
│ Max: 50 tasks │        │ Max: 5 replicas│
└───────────────┘        └────────────────┘
        │                         │
        ▼                         ▼
┌───────────────┐        ┌────────────────┐
│ Add ECS Tasks │        │ Add RDS Read   │
│ Behind ALB    │        │ Replicas       │
└───────────────┘        └────────────────┘
```

### Caching Layers

```
Request ──> CloudFront ──> ALB ──> API Gateway
               │                        │
               ▼                        ▼
         Static Assets            API Endpoints
         (1 year TTL)                  │
                                       ▼
                                 Redis Cache
                                 • Sessions (24h)
                                 • API responses (5-60min)
                                 • Embeddings (7 days)
                                       │
                                       ▼
                                  PostgreSQL
                                 (Source of truth)
```

## 6. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Edge Security (CloudFront + WAF)                       │
│     • DDoS protection                                      │
│     • Geographic restrictions                              │
│     • Rate limiting                                        │
│                                                             │
│  2. Network Security (VPC)                                  │
│     • Private subnets for compute/data                     │
│     • Security groups (least privilege)                    │
│     • NACLs for subnet-level control                       │
│                                                             │
│  3. Application Security                                    │
│     • JWT tokens (short-lived)                            │
│     • API key scoping                                     │
│     • Request validation                                   │
│                                                             │
│  4. Data Security                                          │
│     • Encryption at rest (KMS)                            │
│     • Encryption in transit (TLS 1.3)                     │
│     • Field-level encryption for PII                      │
│                                                             │
│  5. Access Control                                         │
│     • IAM roles (least privilege)                         │
│     • Database RLS                                        │
│     • Audit logging                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 7. Cost Optimization Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 Cost Optimization Strategy                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Compute Optimization                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Fargate Spot for non-critical tasks (-70% cost)    │ │
│  │  • Reserved Instances for baseline load (-50% cost)   │ │
│  │  • Auto-scaling to match demand                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Storage Optimization                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • S3 Intelligent Tiering for documents               │ │
│  │  • Glacier for long-term backups                      │ │
│  │  • RDS storage auto-scaling                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  LLM Cost Control                                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Semantic caching (80% cache hit rate)              │ │
│  │  • Request batching                                    │ │
│  │  • Tiered model selection by customer tier            │ │
│  │  • Token limit enforcement                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Data Transfer Optimization                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • CloudFront for static assets                       │ │
│  │  • VPC endpoints for AWS services                     │ │
│  │  • Response compression                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 8. Development to Production Flow

```
Developer Workstation          GitHub              AWS
       │                         │                   │
       ├──[1] git push──────────>│                   │
       │                         │                   │
       │                    ┌────┴────┐              │
       │                    │ GitHub  │              │
       │                    │ Actions │              │
       │                    └────┬────┘              │
       │                         │                   │
       │                    [2] Run Tests            │
       │                         │                   │
       │                    [3] Build Images         │
       │                         ├──────────────────>│ ECR
       │                         │                   │
       │                    [4] Deploy to Staging    │
       │                         ├──────────────────>│ ECS Staging
       │                         │                   │
       │                    [5] Run E2E Tests        │
       │                         │                   │
       │                    [6] Manual Approval      │
       │<────────────────────────┤                   │
       │                         │                   │
       ├──[7] Approve───────────>│                   │
       │                         │                   │
       │                    [8] Blue/Green Deploy    │
       │                         ├──────────────────>│ ECS Production
       │                         │                   │
       │                    [9] Health Checks        │
       │                         │                   │
       │                    [10] Switch Traffic      │
       │                         ├──────────────────>│ ALB
       │                         │                   │
```

---

These diagrams provide a comprehensive view of NETVEXA's architecture, from high-level components to detailed deployment and security strategies.