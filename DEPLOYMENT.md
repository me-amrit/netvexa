# NETVEXA Local Deployment Guide

## Prerequisites

Before deploying NETVEXA locally, ensure you have the following installed:

- **Docker & Docker Compose** - For PostgreSQL and Redis
- **Python 3.8+** - For the backend API
- **Node.js 16+** - For the React dashboard
- **Git** - For version control

## Quick Start

The easiest way to deploy locally is using the deployment script:

```bash
./deploy_local.sh
```

Choose option 3 to start both backend and frontend.

## Manual Deployment

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Update `.env` with your configuration:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/netvexa
JWT_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

6. Create the database:
```bash
createdb netvexa
```

7. Run migrations:
```bash
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

8. Start the backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend Setup

1. Navigate to the dashboard directory:
```bash
cd dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file:
```bash
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

4. Start the development server:
```bash
npm start
```

The dashboard will be available at http://localhost:3000

## Default Credentials

After deployment, you can create a new account by:
1. Going to http://localhost:3000/register
2. Creating an account with your email
3. Logging in with your credentials

## Testing the Deployment

1. **Backend Health Check**:
```bash
curl http://localhost:8000/health
```

2. **Create a Test User**:
- Navigate to http://localhost:3000/register
- Create an account
- Login and create your first AI agent

3. **Test Agent Creation**:
- Go to Agents page
- Click "Create Agent"
- Fill in the details and save
- Test the agent using the test chat feature

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>

# Find process using port 3000
lsof -i :3000
# Kill the process
kill -9 <PID>
```

### PostgreSQL Connection Issues
1. Ensure PostgreSQL is running:
```bash
# macOS
brew services start postgresql

# Ubuntu/Debian
sudo systemctl start postgresql
```

2. Check PostgreSQL is accepting connections:
```bash
pg_isready
```

3. Create the database manually if needed:
```bash
psql -U postgres -c "CREATE DATABASE netvexa;"
```

### Missing Dependencies
If you encounter module not found errors:

Backend:
```bash
pip install -r requirements.txt --upgrade
```

Frontend:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Development Tips

1. **Backend API Documentation**: Visit http://localhost:8000/docs for interactive API docs

2. **Frontend Hot Reload**: The React app will automatically reload when you make changes

3. **Database Viewer**: Use a tool like pgAdmin or DBeaver to view the database

4. **Testing API Endpoints**: Use the Swagger UI at http://localhost:8000/docs or tools like Postman

## Next Steps

1. Configure your OpenAI API key in the backend `.env` file
2. Set up Stripe keys for billing (when ready)
3. Upload documents to train your agents
4. Integrate the WordPress plugin with your API key

## Support

If you encounter any issues, check:
1. Console logs in both terminal windows
2. Browser developer console for frontend errors
3. Backend logs at http://localhost:8000/docs for API errors