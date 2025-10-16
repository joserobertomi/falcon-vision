# Development Setup

## Prerequisites

Before setting up the development environment, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** (2.30+)
- **Node.js** (18+) and **npm** (8+)
- **Python** (3.10+) and **pip** (21+)
- **UV** (Python package manager)

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/falcon-vision/falcon-vision.git
cd falcon-vision
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start Development Environment
```bash
# Start all services
docker-compose up -d

# Or start specific services
docker-compose up -d backend frontend ui
```

### 4. Verify Installation
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

## Backend Development

### Local Development Setup

#### 1. Python Environment
```bash
cd backend

# Install UV if not already installed
pip install uv

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv sync
```

#### 2. Database Setup
```bash
# Run database migrations
alembic upgrade head

# Create initial data (optional)
python scripts/create_initial_data.py
```

#### 3. Start Development Server
```bash
# Start FastAPI server with hot reload
fastapi run --reload app/main.py

# Or using UV
uv run fastapi run --reload app/main.py
```

#### 4. API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Backend Testing

#### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run tests in watch mode
pytest-watch
```

#### Test Database
```bash
# Create test database
createdb falcon_vision_test

# Run tests with test database
pytest --test-db-url=postgresql://user:pass@localhost/falcon_vision_test
```

## Frontend Development

### Local Development Setup

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env.local

# Edit environment variables
nano .env.local
```

#### 3. Start Development Server
```bash
# Start Vite development server
npm run dev

# Or with specific port
npm run dev -- --port 3000
```

#### 4. Build for Production
```bash
# Build production bundle
npm run build

# Preview production build
npm run preview
```

### Frontend Testing

#### Run Tests
```bash
# Run unit tests
npm test

# Run E2E tests with Playwright
npm run test:e2e

# Run tests in watch mode
npm run test:watch
```

#### Code Quality
```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## UI Dashboard Development

### Local Development Setup

#### 1. Python Environment
```bash
cd ui

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Start Development Server
```bash
# Start Streamlit development server
streamlit run app/main.py

# Or with specific port
streamlit run app/main.py --server.port 8501
```

#### 3. Access Dashboard
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## Database Development

### Database Management

#### 1. Database Connection
```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d falcon_vision

# Or using Docker
docker-compose exec db psql -U postgres -d falcon_vision
```

#### 2. Migration Management
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Show migration history
alembic history
```

#### 3. Database Seeding
```bash
# Seed development data
python scripts/seed_dev_data.py

# Reset database
python scripts/reset_database.py
```

## Development Tools

### Code Quality

#### Backend (Python)
```bash
# Format code with Black
black app/

# Lint with Ruff
ruff check app/

# Type checking with MyPy
mypy app/

# Run all quality checks
pre-commit run --all-files
```

#### Frontend (TypeScript/React)
```bash
# Lint with Biome
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# Run all quality checks
npm run quality
```

### Git Hooks

#### Pre-commit Setup
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### IDE Configuration

#### VS Code
Recommended extensions:
- Python
- TypeScript and JavaScript Language Features
- Prettier
- ESLint
- Docker
- GitLens

#### PyCharm
Recommended plugins:
- Docker
- Database Tools
- Git Integration
- Markdown

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/falcon_vision

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_TLS=false
EMAILS_FROM_EMAIL=noreply@example.com

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Frontend (.env.local)
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Development
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
```

## Troubleshooting

### Common Issues

#### Backend Issues
```bash
# Database connection issues
docker-compose restart db
alembic upgrade head

# Port already in use
lsof -ti:8000 | xargs kill -9

# Permission issues
sudo chown -R $USER:$USER .
```

#### Frontend Issues
```bash
# Node modules issues
rm -rf node_modules package-lock.json
npm install

# Port already in use
lsof -ti:5173 | xargs kill -9

# Build issues
npm run clean
npm run build
```

#### Docker Issues
```bash
# Clean Docker cache
docker system prune -a

# Rebuild containers
docker-compose build --no-cache

# Reset Docker volumes
docker-compose down -v
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Start with debugger
python -m debugpy --listen 5678 --wait-for-client app/main.py
```

#### Frontend Debug
```bash
# Enable debug mode
export VITE_DEBUG=true
export VITE_LOG_LEVEL=debug

# Start with debugger
npm run dev -- --inspect
```

## Performance Optimization

### Backend Optimization
- Use async/await for I/O operations
- Implement database connection pooling
- Add Redis for caching
- Optimize database queries

### Frontend Optimization
- Implement code splitting
- Use React.memo for components
- Optimize bundle size
- Implement lazy loading

### Database Optimization
- Add proper indexes
- Optimize queries
- Use connection pooling
- Implement read replicas

## Contributing

### Development Workflow
1. Create feature branch
2. Make changes
3. Run tests
4. Commit changes
5. Push to remote
6. Create pull request

### Code Standards
- Follow PEP 8 for Python
- Follow Airbnb style guide for TypeScript
- Write comprehensive tests
- Document all public APIs
- Use meaningful commit messages
