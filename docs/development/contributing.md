# Contributing Guide

## Overview

Thank you for your interest in contributing to Falcon Vision! This guide will help you get started with contributing to the project.

## Getting Started

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/falcon-vision.git
cd falcon-vision

# Add upstream remote
git remote add upstream https://github.com/falcon-vision/falcon-vision.git
```

### 2. Development Setup
```bash
# Follow the development setup guide
# See docs/development/setup.md for detailed instructions

# Install pre-commit hooks
pre-commit install
```

### 3. Create Feature Branch
```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

## Development Workflow

### 1. Make Changes
- Write clean, readable code
- Follow the coding standards
- Add tests for new functionality
- Update documentation as needed

### 2. Test Your Changes
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
npm run test:e2e

# UI tests
cd ui
pytest
```

### 3. Code Quality Checks
```bash
# Backend quality checks
cd backend
black app/
ruff check app/
mypy app/

# Frontend quality checks
cd frontend
npm run lint
npm run format
npm run type-check
```

### 4. Commit Changes
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add user authentication endpoint"

# Push to your fork
git push origin feature/your-feature-name
```

### 5. Create Pull Request
- Go to your fork on GitHub
- Click "New Pull Request"
- Fill out the PR template
- Request review from maintainers

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all public functions
- Use meaningful variable and function names

```python
def detect_persons(
    image: np.ndarray,
    confidence_threshold: float = 0.5
) -> List[Detection]:
    """
    Detect persons in an image using YOLOv8.
    
    Args:
        image: Input image as numpy array
        confidence_threshold: Minimum confidence for detections
        
    Returns:
        List of Detection objects
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)
- Follow Airbnb style guide
- Use strict TypeScript configuration
- Write JSDoc comments for complex functions
- Use functional components with hooks

```typescript
interface DetectionProps {
  detection: Detection;
  onSelect?: (detection: Detection) => void;
}

/**
 * Renders a single detection with bounding box
 */
export const DetectionComponent: React.FC<DetectionProps> = ({
  detection,
  onSelect
}) => {
  // Implementation here
};
```

### Markdown (Documentation)
- Use proper heading hierarchy
- Include code examples
- Add links to related documentation
- Keep lines under 100 characters

## Commit Message Convention

We use conventional commits for clear commit history:

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```bash
feat(auth): add JWT token refresh endpoint
fix(detection): resolve memory leak in image processing
docs(api): update authentication documentation
test(backend): add integration tests for detection API
```

## Pull Request Guidelines

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process
1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainers review code
3. **Testing**: Manual testing if needed
4. **Approval**: At least one approval required
5. **Merge**: Squash and merge to main

## Issue Guidelines

### Bug Reports
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 1.0.0]

## Additional Context
Any other context about the problem
```

### Feature Requests
```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives
Any alternative solutions considered?

## Additional Context
Any other context about the feature
```

## Development Environment

### Required Tools
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Node.js**: 18+
- **Python**: 3.10+
- **UV**: Python package manager

### IDE Configuration
- **VS Code**: Use recommended extensions
- **PyCharm**: Use project settings
- **WebStorm**: Use project configuration

### Environment Variables
```bash
# Copy and customize
cp .env.example .env
```

## Testing Requirements

### Test Coverage
- **Backend**: >90% code coverage
- **Frontend**: >80% code coverage
- **Critical Paths**: 100% coverage

### Test Types
- **Unit Tests**: Individual functions/components
- **Integration Tests**: API endpoints
- **E2E Tests**: User workflows
- **Performance Tests**: Load testing

## Documentation Requirements

### Code Documentation
- Docstrings for all public functions
- Inline comments for complex logic
- Type hints for all functions
- README files for each module

### API Documentation
- OpenAPI/Swagger specifications
- Example requests/responses
- Error code documentation
- Authentication requirements

### User Documentation
- Installation guides
- Configuration instructions
- Usage examples
- Troubleshooting guides

## Release Process

### Version Numbering
We use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Changelog updated
- [ ] Release notes written
- [ ] Tag created
- [ ] Release published

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the golden rule

### Communication
- Use GitHub issues for bugs and features
- Use GitHub discussions for questions
- Use pull request comments for code review
- Be patient with maintainers

### Recognition
- Contributors are recognized in README
- Significant contributions get commit access
- Community feedback is valued
- Open source spirit is maintained

## Getting Help

### Resources
- **Documentation**: Check the docs folder
- **Issues**: Search existing issues
- **Discussions**: Use GitHub discussions
- **Discord**: Join our community server

### Contact
- **Maintainers**: @falcon-vision/maintainers
- **Email**: maintainers@falcon-vision.com
- **Discord**: #contributing channel

## License

By contributing to Falcon Vision, you agree that your contributions will be licensed under the MIT License.

## Thank You

Thank you for contributing to Falcon Vision! Your contributions help make this project better for everyone.
