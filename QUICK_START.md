# NETVEXA Quick Start Guide

## 🚀 Deploy in 3 Steps

### 1. Start Docker Services
```bash
docker-compose up -d postgres redis
```

### 2. Start Backend
```bash
cd backend
./run_backend.sh
```

### 3. Start Frontend (New Terminal)
```bash
cd dashboard
./run_frontend.sh
```

## 📱 Access Your Application

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@netvexa.com / admin)

## 🔑 First Time Setup

1. **Update API Keys** in `backend/.env`:
   ```
   OPENAI_API_KEY=your-key-here
   ```

2. **Create Account**:
   - Go to http://localhost:3000/register
   - Sign up and create your first AI agent

## 🛠️ Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | React Dashboard |
| Backend | 8000 | FastAPI Server |
| PostgreSQL | 5433 | Database (with pgvector) |
| Redis | 6379 | Cache & Sessions |
| pgAdmin | 5050 | Database Management |

## 📝 Common Commands

```bash
# Check services
docker ps

# View backend logs
docker-compose logs backend

# Stop all services
docker-compose down

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

## 🐛 Troubleshooting

**Backend won't start?**
- Check PostgreSQL: `docker ps | grep postgres`
- Check `.env` file exists
- Run: `pip install -r requirements.txt`

**Frontend won't start?**
- Check backend is running first
- Run: `npm install`
- Check port 3000 is free

**Can't connect to database?**
- PostgreSQL runs on port 5433 (not 5432)
- Default password: `netvexa_password`
- Database name: `netvexa_db`