# AI Business Intelligence Assistant

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Live Demo:** [https://bi-frontend-placeholder.onrender.com](https://bi-frontend-placeholder.onrender.com) *(Placeholder)*

A full-stack Business Intelligence dashboard with an AI-powered natural language querying feature. Built with FastAPI, Streamlit, PostgreSQL, and LangChain.

## Architecture & CI/CD
This project features a decoupled architecture:
1. **Frontend (Streamlit)**: Serves the interactive user interface and dashboards.
2. **Backend (FastAPI)**: Serves the analytical data and securely communicates with OpenAI via LangChain.
3. **Database (PostgreSQL)**: Stores sales, customer, and product data.

**CI/CD Pipeline**: 
A GitHub Actions workflow is triggered on every push to the `main` branch. It runs a syntax health check on the backend. Upon success, it triggers a Render Deploy Hook to instantly roll out the new version to the live servers.

## Prerequisites
- Docker
- Docker Compose
- An OpenAI API Key (for the AI Chat feature)

## Setup Instructions (Local Deployment)

1. **Configure Environment Variables**:
   Copy the example environment file to create your own `.env` file:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API Key.

2. **Start the Application**:
   Run the following single command to build the images and start all three services (database, backend, frontend):
   ```bash
   docker-compose up --build -d
   ```

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | The database username (default: bi_user) |
| `POSTGRES_PASSWORD` | The database password (default: bi_password) |
| `POSTGRES_DB` | The database name (default: bi_db) |
| `POSTGRES_HOST` | The database host (default: postgres) |
| `BACKEND_URL` | The URL of the FastAPI backend for the frontend to consume. |
| `OPENAI_API_KEY` | Your secret OpenAI API key for AI Chat queries. |
| `RENDER_DEPLOY_HOOK_URL` | (GitHub Secret) The URL provided by Render to trigger deployments. |

## Accessing the Services (Local)
Once the containers are running, you can access the services at the following URLs:
- **Streamlit Dashboard (Frontend)**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Backend (API Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database**: `localhost:5432`

## Shutting Down
To stop the services, run:
```bash
docker-compose down
```
If you want to wipe the database volume entirely (to re-run the seed script):
```bash
docker-compose down -v
```
