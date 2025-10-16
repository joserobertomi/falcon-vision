# Testing Guide

## Overview

Falcon Vision uses a comprehensive testing strategy covering unit tests, integration tests, and end-to-end tests across all components.

## Testing Stack

### Backend Testing
- **Framework**: pytest
- **Database**: PostgreSQL test database
- **HTTP Client**: httpx
- **Coverage**: coverage.py
- **Mocking**: unittest.mock

### Frontend Testing
- **Unit Tests**: Vitest
- **E2E Tests**: Playwright
- **Component Tests**: React Testing Library
- **Mocking**: MSW (Mock Service Worker)

### UI Testing
- **Framework**: pytest
- **Streamlit Testing**: streamlit-testing
- **Selenium**: WebDriver for UI automation

## Backend Testing

### Test Structure
```
backend/
├── tests/
│   ├── conftest.py          # Test configuration
│   ├── test_auth.py         # Authentication tests
│   ├── test_detections.py   # Detection API tests
│   ├── test_analytics.py    # Analytics tests
│   ├── test_websocket.py    # WebSocket tests
│   └── fixtures/            # Test fixtures
│       ├── users.json
│       └── detections.json
```

### Running Backend Tests

#### All Tests
```bash
cd backend
pytest
```

#### Specific Test Categories
```bash
# Authentication tests
pytest tests/test_auth.py

# API tests
pytest tests/test_api/

# Integration tests
pytest tests/test_integration/

# With coverage
pytest --cov=app --cov-report=html
```

#### Test Configuration
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from app.main import app
from app.database import get_db

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///./test.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(test_db):
    def get_test_db():
        return test_db
    
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Test Examples

#### Authentication Tests
```python
# test_auth.py
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_login_user(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_route(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

#### Detection API Tests
```python
# test_detections.py
def test_detect_person(client, auth_headers, test_image):
    response = client.post(
        "/api/v1/detections/person",
        headers=auth_headers,
        files={"image": test_image}
    )
    assert response.status_code == 200
    assert "detections" in response.json()

def test_get_detections(client, auth_headers):
    response = client.get(
        "/api/v1/detections/person",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "detections" in response.json()
```

## Frontend Testing

### Test Structure
```
frontend/
├── src/
│   ├── __tests__/           # Test files
│   │   ├── components/      # Component tests
│   │   ├── hooks/          # Hook tests
│   │   └── utils/          # Utility tests
│   └── tests/              # E2E tests
│       ├── auth.spec.ts
│       ├── detection.spec.ts
│       └── analytics.spec.ts
```

### Running Frontend Tests

#### Unit Tests
```bash
cd frontend
npm test
```

#### E2E Tests
```bash
# Run E2E tests
npm run test:e2e

# Run specific test
npm run test:e2e -- tests/auth.spec.ts

# Run in headed mode
npm run test:e2e -- --headed
```

#### Test Configuration
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
})
```

### Test Examples

#### Component Tests
```typescript
// __tests__/components/LoginForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { LoginForm } from '../components/LoginForm'

describe('LoginForm', () => {
  it('renders login form', () => {
    render(<LoginForm />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    const mockSubmit = jest.fn()
    render(<LoginForm onSubmit={mockSubmit} />)
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    
    expect(mockSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    })
  })
})
```

#### E2E Tests
```typescript
// tests/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('user can login', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('[data-testid="email-input"]', 'test@example.com')
    await page.fill('[data-testid="password-input"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })

  test('user can logout', async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'test@example.com')
    await page.fill('[data-testid="password-input"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    // Logout
    await page.click('[data-testid="user-menu"]')
    await page.click('[data-testid="logout-button"]')
    
    await expect(page).toHaveURL('/login')
  })
})
```

## UI Testing

### Test Structure
```
ui/
├── tests/
│   ├── test_analytics.py    # Analytics tests
│   ├── test_dashboard.py    # Dashboard tests
│   └── test_integration.py  # Integration tests
```

### Running UI Tests
```bash
cd ui
pytest tests/
```

### Test Examples
```python
# test_dashboard.py
import pytest
from streamlit.testing import StreamlitTestClient
from app.main import main

@pytest.fixture
def client():
    return StreamlitTestClient(main)

def test_dashboard_renders(client):
    client.run()
    assert client.get_text("h1") == "Falcon Vision Analytics"

def test_metrics_display(client):
    client.run()
    assert "Total Detections" in client.get_text()
    assert "Active Users" in client.get_text()
```

## Integration Testing

### API Integration Tests
```python
# test_integration.py
def test_detection_workflow(client, auth_headers, test_image):
    # 1. Upload image for detection
    response = client.post(
        "/api/v1/detections/person",
        headers=auth_headers,
        files={"image": test_image}
    )
    assert response.status_code == 200
    detection_id = response.json()["detections"][0]["id"]
    
    # 2. Get detection details
    response = client.get(
        f"/api/v1/detections/person/{detection_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # 3. Get analytics
    response = client.get(
        "/api/v1/analytics/detections",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### WebSocket Integration Tests
```python
# test_websocket.py
import asyncio
import websockets

async def test_video_streaming():
    uri = "ws://localhost:8000/ws/video-stream"
    async with websockets.connect(uri) as websocket:
        # Send test frame
        await websocket.send(test_frame_data)
        
        # Receive detection result
        response = await websocket.recv()
        data = json.loads(response)
        assert data["type"] == "detection"
        assert "detections" in data
```

## Performance Testing

### Load Testing
```python
# test_performance.py
import asyncio
import aiohttp

async def test_concurrent_detections():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):
            task = session.post(
                "http://localhost:8000/api/v1/detections/person",
                headers=auth_headers,
                data=test_image_data
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        for response in responses:
            assert response.status == 200
```

### Memory Testing
```python
# test_memory.py
import psutil
import pytest

def test_memory_usage():
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Perform memory-intensive operations
    for i in range(1000):
        # Detection operations
        pass
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Assert memory usage is reasonable
    assert memory_increase < 100 * 1024 * 1024  # 100MB
```

## Test Data Management

### Fixtures
```python
# conftest.py
@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }

@pytest.fixture
def test_image():
    return ("test_image.jpg", open("tests/fixtures/test_image.jpg", "rb"), "image/jpeg")

@pytest.fixture
def auth_headers(client, test_user):
    # Login and get token
    response = client.post("/api/v1/auth/login", data=test_user)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Test Database
```python
@pytest.fixture(scope="function")
def test_db():
    # Create test database
    engine = create_engine("sqlite:///./test.db")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    # Cleanup
    os.remove("test.db")
```

## Continuous Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
```

## Test Coverage

### Coverage Goals
- **Backend**: >90% code coverage
- **Frontend**: >80% code coverage
- **Critical Paths**: 100% coverage

### Coverage Reports
```bash
# Backend coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term

# Frontend coverage
cd frontend
npm run test:coverage
```

## Debugging Tests

### Backend Debug
```bash
# Run specific test with debug output
pytest -v -s tests/test_auth.py::test_login_user

# Run with pdb debugger
pytest --pdb tests/test_auth.py

# Run with logging
pytest --log-cli-level=DEBUG tests/test_auth.py
```

### Frontend Debug
```bash
# Run tests in watch mode
npm run test:watch

# Run with debug output
npm run test -- --verbose

# Run specific test file
npm run test -- tests/auth.test.tsx
```

## Best Practices

### Test Organization
- Group related tests in describe blocks
- Use descriptive test names
- Keep tests independent and isolated
- Use proper setup and teardown

### Test Data
- Use factories for test data generation
- Keep test data minimal and focused
- Use realistic test data
- Clean up test data after tests

### Assertions
- Use specific assertions
- Test both positive and negative cases
- Verify side effects
- Check error conditions

### Performance
- Keep tests fast
- Use mocks for external dependencies
- Avoid unnecessary I/O operations
- Use parallel test execution when possible
