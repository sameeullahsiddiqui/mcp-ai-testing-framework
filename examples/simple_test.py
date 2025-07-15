import asyncio
import os
import sys
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.ai_agent import MultiPhaseTestingAgent, AgentConfig, AIProvider, TestPhase
from dotenv import load_dotenv

load_dotenv()

async def run_basic_multiphasetesting_example():
    """
    Simple example showing how to use the Multi-Phase Testing framework.
    """
    print("🚀 Starting Multi-Phase AI testing example...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    config = set_config()

    # Create Multi-Phase Testing Agent
    agent = MultiPhaseTestingAgent(config)
    print("✅ Multi-Phase Testing Agent initialized")
    
    # Target application for testing
    target_url = "https://demo.playwright.dev/todomvc/"
    # Alternative targets:
    # target_url = "https://www.saucedemo.com/"
    # target_url = "https://demowebshop.tricentis.com/"
    
    # Define specific testing requirements
    requirements = """
    Focus on the following key areas:
    1. **Todo Management**: Creating, editing, and deleting todos
    2. **Filtering**: All, Active, Completed filter functionality
    3. **Bulk Operations**: Mark all complete, clear completed
    4. **Data Persistence**: Todo state management
    5. **User Interface**: Responsive design and accessibility
    6. **Edge Cases**: Empty states, long text, special characters
    """
    
    try:
        print(f"🎯 Starting complete testing cycle for: {target_url}")
        print("📋 This will execute 4 phases: Analysis → Planning → Execution → Reporting")
        
        # Execute complete testing cycle
        results = await agent.run_complete_testing_cycle(
            target_url=target_url,
            requirements=requirements
        )
        
        # Display results summary
        print("\n" + "="*60)
        print("📊 TESTING CYCLE RESULTS")
        print("="*60)
        print(f"🎯 Target URL: {results['target_url']}")
        print(f"⏰ Timestamp: {results['timestamp']}")
        print(f"📈 Overall Status: {results['overall_status'].upper()}")
        print(f"📄 Summary Report: {results.get('summary_file', 'N/A')}")
        
        print(f"\n📁 Generated Reports:")
        for phase_name, phase_result in results["phases"].items():
            status_icon = "✅" if phase_result.get("status") == "completed" else "❌"
            print(f"   {status_icon} {phase_name.title()} Phase: {phase_result.get('filepath', 'N/A')}")
        
        # Provide next steps
        if results['overall_status'] == 'completed':
            print(f"\n🎉 SUCCESS: Complete testing cycle finished!")
            print(f"📖 Next steps:")
            print(f"   1. Review individual phase reports for detailed findings")
            print(f"   2. Check execution phase for any issues found")
            print(f"   3. Implement recommendations from reporting phase")
        else:
            print(f"\n⚠️ PARTIAL: Testing cycle completed with some issues")
            print(f"📖 Recommended actions:")
            print(f"   1. Check individual phase reports for errors")
            print(f"   2. Verify MCP server connectivity")
            print(f"   3. Review Azure OpenAI configuration")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during testing cycle: {str(e)}")
        print(f"🔧 Troubleshooting suggestions:")
        print(f"   1. Verify Azure OpenAI credentials")
        print(f"   2. Check internet connectivity")
        print(f"   3. Ensure Node.js and npx are installed")
        print(f"   4. Verify target URL is accessible")
        return None

def set_config():
    try:
        config = AgentConfig(
                provider=AIProvider.AZURE_OPENAI, 
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION")
            )
                
        print("✅ Configuration loaded from file")
        return config
        
    except ValueError:
        # Validate configuration
        if not all([config.api_key, config.endpoint, config.deployment_name]):
            print("❌ Missing required Azure OpenAI environment variables:")
            print("   - AZURE_OPENAI_API_KEY")
            print("   - AZURE_OPENAI_ENDPOINT") 
            print("   - AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL")

    return None    
    

async def run_individual_phase_example():
    """
    Example showing how to run individual testing phases.
    """
    print("\n🔍 Running Individual Phase Example...")
    
    # Load configuration
    config = set_config()
    
    agent = MultiPhaseTestingAgent(config)
    target_url = "https://demo.playwright.dev/todomvc/"
    
    try:
        # Example: Run only Analysis phase
        print("📊 Running Analysis Phase only...")
        analysis_result = await agent._execute_phase(
            TestPhase.ANALYSIS, 
            target_url, 
            "Focus on todo application structure and core functionality"
        )
        
        print(f"✅ Analysis completed: {analysis_result.get('filepath', 'N/A')}")
        
        # Example: Run Planning phase with analysis context
        if analysis_result.get('status') == 'completed':
            print("📋 Running Planning Phase with analysis context...")
            planning_result = await agent._execute_phase(
                TestPhase.PLANNING,
                target_url,
                f"Analysis results: {analysis_result['result'][:500]}..."
            )
            
            print(f"✅ Planning completed: {planning_result.get('filepath', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual phase example failed: {str(e)}")
        return False

async def main():
    """
    Main function demonstrating different usage patterns.
    """
    print("🤖 Multi-Phase AI Testing Framework Examples")
    print("=" * 50)
    
    # Example 1: Complete testing cycle (recommended)
    print("\n1️⃣ COMPLETE TESTING CYCLE EXAMPLE")
    results = await run_basic_multiphasetesting_example()
    
    if results and results['overall_status'] == 'completed':
        print("✅ Complete cycle example finished successfully!")

if __name__ == "__main__":
    asyncio.run(main())