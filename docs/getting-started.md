# Getting Started with MCP-Driven AI Testing

This guide will help you set up and run your first AI-powered tests using the MCP framework.

## Prerequisites

- Python 3.9 or higher
- Node.js 16+ (for Playwright browser automation)
- An OpenAI API key or Anthropic API key
- Basic understanding of web testing concepts

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mcp-ai-testing-framework.git
cd mcp-ai-testing-framework
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Browser Dependencies

```bash
# Install Playwright browsers
playwright install

# Or install specific browsers
playwright install chromium firefox
```

### 4. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
# Required:
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional configurations:
AI_PROVIDER=openai  # or 'anthropic'
AI_MODEL=gpt-4-turbo  # or 'claude-3-sonnet'
DEFAULT_BROWSER=chromium
HEADLESS=true
```

## Your First AI Test

### Simple Example

Create a file called `my_first_test.py`:

```python
import asyncio
import os
from dotenv import load_dotenv
from src.core.ai_agent import AITestAgent, AgentConfig, AIProvider
from src.core.mcp_client import MCPClient

load_dotenv()

async def main():
    # Configure AI
    config = AgentConfig(
        provider=AIProvider.OPENAI,
        model="gpt-4-turbo",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize MCP client
    mcp_client = MCPClient()
    await mcp_client.initialize(browser_type="chromium", headless=False)
    
    # Create AI agent
    agent = AITestAgent(config, mcp_client)
    
    try:
        # Let AI analyze and test your application
        print("🔍 Analyzing application...")
        analysis = await agent.analyze_application("https://your-app.com")
        
        print("📋 Generating test plan...")
        test_plan = await agent.generate_test_plan(analysis)
        
        print("🧪 Running tests...")
        for test_case in test_plan.get_all_test_cases()[:3]:  # Run first 3 tests
            result = await agent.execute_test_case(test_case)
            print(f"✅ {test_case.name}: {result.status}")
            
    finally:
        await mcp_client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

Run your test:

```bash
python my_first_test.py
```

## Understanding the Output

The AI agent will:

1. **Analyze** your application's structure and functionality
2. **Generate** a comprehensive test plan with multiple test cases
3. **Execute** tests using intelligent browser automation
4. **Report** results with screenshots and detailed logs

Example output:
```
🔍 Analyzing application...
✅ Found 5 key features: ['user_registration', 'login', 'product_search', 'shopping_cart', 'checkout']

📋 Generating test plan...
✅ Generated 12 test cases across 4 categories

🧪 Running tests...
✅ User Registration Flow: passed
✅ Login with Valid Credentials: passed
✅ Product Search Functionality: failed
```

## Key Concepts

### 1. AI Agent
The brain of the system that understands your application and creates intelligent test strategies.

### 2. MCP Client
Handles communication between the AI and various tools (browsers, file systems, APIs).

### 3. Test Plan
AI-generated comprehensive testing strategy with prioritized test cases.

### 4. Self-Healing Tests
Tests that adapt to UI changes without manual maintenance.

## Common Configuration Options

### Browser Settings
```python
# Different browser types
await mcp_client.initialize(browser_type="firefox", headless=True)
await mcp_client.initialize(browser_type="webkit", headless=False)

# Custom viewport
await mcp_client.page.set_viewport_size({"width": 1920, "height": 1080})
```

### AI Provider Settings
```python
# OpenAI Configuration
config = AgentConfig(
    provider=AIProvider.OPENAI,
    model="gpt-4-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.1,  # Lower = more deterministic
    max_tokens=4000
)

# Anthropic Configuration
config = AgentConfig(
    provider=AIProvider.ANTHROPIC,
    model="claude-3-sonnet-20240229",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### Test Requirements
```python
# Customize test generation
test_requirements = {
    "focus_areas": ["checkout_flow", "user_authentication"],
    "test_types": ["functional", "usability", "security"],
    "browsers": ["chrome", "firefox", "safari"],
    "user_scenarios": ["new_user", "returning_user", "guest_checkout"]
}

test_plan = await agent.generate_test_plan(analysis, test_requirements)
```

## Best Practices

### 1. Start Small
Begin with a single page or feature before testing entire applications.

### 2. Use Descriptive Selectors
The AI works best with semantic selectors rather than brittle CSS paths:
```python
# Good
"Login button"
"Email input field"
"Submit form"

# Less ideal
"#login-btn-123"
"input[type='email'][data-id='user-email']"
```

### 3. Monitor API Usage
AI API calls can be expensive. Start with smaller test suites and monitor usage:
```python
# Limit test execution for development
critical_tests = test_plan.get_test_cases_by_priority("high")
for test_case in critical_tests[:5]:  # Only run 5 tests
    result = await agent.execute_test_case(test_case)
```

### 4. Review AI-Generated Plans
Always review the test plan before execution:
```python
test_plan = await agent.generate_test_plan(analysis)

# Review and save the plan
with open("test_plan.json", "w") as f:
    json.dump(test_plan.to_dict(), f, indent=2)

print(f"Generated {len(test_plan.get_all_test_cases())} test cases")
print("Review test_plan.json before proceeding...")
```

## Troubleshooting

### Common Issues

**1. "Browser not found" Error**
```bash
# Install Playwright browsers
playwright install chromium
```

**2. "API Key Invalid" Error**
```bash
# Verify your .env file contains valid API keys
cat .env | grep API_KEY
```

**3. "Element not found" Errors**
- The AI might need more context about your application
- Try providing more descriptive element selectors
- Check if the page has fully loaded before interaction

**4. Slow Test Execution**
- Reduce `temperature` in AI config for faster, more deterministic responses
- Use `headless=True` for faster browser automation
- Limit concurrent test execution

### Getting Help

1. Check the [FAQ](docs/faq.md)
2. Review [example tests](examples/)
3. Open an issue on GitHub
4. Join our Discord community

## Next Steps

- Explore [advanced configuration options](docs/configuration.md)
- Learn about [CI/CD integration](docs/ci-cd-integration.md)
- Read [best practices guide](docs/best-practices.md)
- Try the [comprehensive examples](examples/)

Happy testing! 🚀