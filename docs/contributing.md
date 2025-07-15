# Contributing to MCP-Driven AI Testing Framework

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🚀 Quick Start for Contributors

1. **Fork the repository**
```bash
git clone https://github.com/yourusername/mcp-ai-testing-framework.git
cd mcp-ai-testing-framework
```

2. **Set up development environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

3. **Install pre-commit hooks**
```bash
pre-commit install
```

4. **Run tests to ensure everything works**
```bash
pytest tests/unit/
```

## 📋 Development Guidelines

### Code Style
- We use **Black** for code formatting (100 character line limit)
- **Flake8** for linting
- **MyPy** for type checking
- **isort** for import sorting

Format your code before committing:
```bash
black src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/
```

### Testing Standards
- **Unit tests**: Fast, isolated tests for individual components
- **Integration tests**: End-to-end tests with real AI APIs and browsers
- **All tests should be async-compatible**

Test categories:
```bash
# Run only unit tests
pytest tests/unit/ -m "not integration"

# Run integration tests (requires API keys)
pytest tests/integration/ -m integration

# Run all tests
pytest
```

### Documentation
- **Docstrings**: Use Google-style docstrings for all public functions
- **Type hints**: Required for all function parameters and return values
- **Examples**: Include practical examples in docstrings

Example:
```python
async def execute_test_case(self, test_case: TestCase) -> TestResult:
    \"\"\"Execute a single test case using MCP browser automation.
    
    Args:
        test_case: The test case to execute with steps and expected results.
        
    Returns:
        TestResult containing execution status, duration, and evidence.
        
    Example:
        >>> result = await agent.execute_test_case(test_case)
        >>> print(f"Test {test_case.name}: {result.status}")
    \"\"\"
```

## 🛠️ Types of Contributions

### 1. Bug Fixes
- **Check existing issues** before creating new ones
- **Include reproduction steps** and environment details
- **Add tests** that verify the fix

### 2. New Features
- **Discuss major features** in an issue before implementing
- **Follow the existing architecture** patterns
- **Include comprehensive tests** and documentation

### 3. MCP Server Implementations
We welcome new MCP server implementations! Examples:
- Database testing servers (MySQL, PostgreSQL, MongoDB)
- API testing servers (REST, GraphQL, gRPC)
- Security testing servers (OWASP ZAP integration)
- Performance testing servers (load testing, profiling)

Template for new MCP servers:
```python
class CustomMCPServer:
    \"\"\"Custom MCP server for [specific functionality].\"\"\"
    
    async def initialize(self):
        \"\"\"Initialize server resources.\"\"\"
        pass
    
    async def execute_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Execute server-specific operation.\"\"\"
        pass
    
    async def cleanup(self):
        \"\"\"Clean up server resources.\"\"\"
        pass
```

### 4. AI Agent Improvements
- **Prompt engineering** improvements for better test generation
- **New analysis capabilities** (accessibility, performance, security)
- **Enhanced error handling** and recovery strategies

### 5. Documentation
- **Tutorial improvements**
- **API documentation**
- **Example applications**
- **Best practices guides**

## 📝 Pull Request Process

### Before Submitting
1. **Update your fork**:
```bash
git checkout main
git pull upstream main
git checkout your-feature-branch
git rebase main
```

2. **Run full test suite**:
```bash
pytest
black --check src/ tests/ examples/
flake8 src/ tests/ examples/
mypy src/
```

3. **Update documentation** if needed

### PR Description Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] New tests added for new functionality

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🧪 Testing with Real APIs

### Setup for Integration Tests
```bash
# Copy test environment template
cp .env.test.example .env.test

# Add your API keys
OPENAI_API_KEY=your_test_key
ANTHROPIC_API_KEY=your_test_key

# Run integration tests
pytest tests/integration/ --env-file=.env.test
```

### Testing Best Practices
- **Use test-specific API keys** (not production keys)
- **Mock external services** in unit tests
- **Limit API calls** in CI/CD (use caching when possible)
- **Test error conditions** and edge cases

## 📊 Performance Considerations

### AI API Usage
- **Cache analysis results** to avoid repeated API calls
- **Batch test generation** when possible
- **Implement rate limiting** for API calls

### Browser Automation
- **Use headless mode** for CI/CD
- **Parallel test execution** with caution (resource limits)
- **Clean up browser resources** properly

## 🔒 Security Guidelines

### API Keys
- **Never commit API keys** to the repository
- **Use environment variables** for all sensitive data
- **Rotate test API keys** regularly

### MCP Servers
- **Validate all inputs** to MCP servers
- **Implement proper error handling**
- **Use secure communication** protocols

## 📋 Issue Templates

### Bug Report
- **Environment details** (OS, Python version, dependencies)
- **Reproduction steps**
- **Expected vs actual behavior**
- **Relevant logs or screenshots**

### Feature Request
- **Use case description**
- **Proposed solution**
- **Alternative approaches considered**
- **Implementation complexity estimate**

## 🏆 Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **Project documentation** for major features

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: Real-time chat with maintainers and community
- **Email**: [your.email@example.com] for private inquiries

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for helping make AI-powered testing more accessible and powerful! 🚀
