import asyncio
import os
from pathlib import Path
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import structlog
from openai import AsyncAzureOpenAI

# Import MCP Studio components
from agents.mcp import MCPServerStdio
from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    set_default_openai_client,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

logger = structlog.get_logger()

class AIProvider(Enum):
    AZURE_OPENAI = "AZURE_OPENAI"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class TestPhase(Enum):
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    REPORTING = "reporting"

@dataclass
class AgentConfig:
    provider: AIProvider
    api_key: str
    endpoint: str
    deployment_name: str
    api_version: str
    max_tokens: int = 4000
    temperature: float = 0.1

class MultiPhaseTestingAgent:
    """
    Multi-agent system for comprehensive web application testing.
    Each phase has its own specialized agent with dedicated responsibilities.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logger.bind(component="multi_phase_testing_agent")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
                # Set up proper directory structure
        self.project_root = Path(__file__).parent.parent.parent  # Go up to project root
        self.reports_dir = self.project_root / "reports/test_reports"
        self.fs_files_dir = self.project_root / "reports/fs_files"
        self.screenshots_dir = self.project_root / "reports/screenshots"
        
        # Create directories
        self.reports_dir.mkdir(exist_ok=True)
        self.fs_files_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Set up Azure OpenAI client
        self.client = AsyncAzureOpenAI(
            api_key=config.api_key,
            azure_endpoint=config.endpoint,
            api_version=config.api_version,
        )
        
        set_default_openai_client(self.client)
        set_tracing_disabled(disabled=True)

        # Initialize specialized agents
        self.agents = {}
        self._create_specialized_agents()
        
                # Progress indicator HTML
        self.progress_html = """
        <div id="testing-progress-bar" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
        ">
            <div style="display: flex; align-items: center;">
                <div id="progress-spinner" style="
                    width: 20px;
                    height: 20px;
                    border: 2px solid #ffffff40;
                    border-top: 2px solid #ffffff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-right: 10px;
                "></div>
                <span id="progress-text">Starting Multi-Phase Testing...</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span id="progress-phase" style="
                    background: rgba(255,255,255,0.2);
                    padding: 4px 12px;
                    border-radius: 20px;
                    margin-right: 10px;
                    font-size: 12px;
                ">INITIALIZING</span>
                <span id="progress-time" style="font-size: 12px; opacity: 0.8;"></span>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            body { margin-top: 60px !important; }
        </style>
        """
                                
        self.logger.info("Multi-phase testing agent initialized", 
                        timestamp=self.timestamp,
                        project_root=str(self.project_root))
    
    def _create_specialized_agents(self):
        """Create specialized agents for each testing phase."""
        
        # Analysis Agent
        self.agents[TestPhase.ANALYSIS] = {
            "name": "Web Application Analysis Agent",
            "instructions": """
                            You are a specialized Web Application Analysis Agent with expertise in understanding application structure and functionality.

                            **IMPORTANT FILE MANAGEMENT**:
                            - All files MUST be saved to: {self.fs_files_dir}
                            - Screenshots MUST be saved to: {self.screenshots_dir}
                            - Use absolute paths, not relative paths
                            - Create subdirectories as needed for organization

                            **IMPORTANT BROWSER MANAGEMENT**:
                            - Always inject progress indicator at start of each page
                            - Update progress indicator with current step
                            - Take screenshots after each major action
                            - Use descriptive screenshot names with timestamps

                            Your primary responsibilities:
                            1. **Application Discovery**:
                                - Navigate to the target URL
                                - Inject progress indicator HTML
                                - Take comprehensive screenshots of key pages
                                - Identify application type (e-commerce, dashboard, blog, etc.)
                                - Map out navigation structure and main sections

                            2. **Feature Identification**:
                                - Catalog all interactive elements (forms, buttons, links)
                                - Document user workflows and journeys
                                - Identify authentication mechanisms
                                - Note data entry points and validation

                            3. **Evidence Collection**:
                                - Take screenshot of homepage
                                - Take screenshots of main sections
                                - Save page source/HTML when relevant
                                - Document findings in JSON format
                            
                            4. **Technical Analysis**:
                                - Analyze page structure and DOM elements
                                - Identify JavaScript frameworks or libraries
                                - Document API endpoints if visible
                                - Note accessibility features

                            4. **Risk Assessment**:
                                - Identify critical functionalities requiring thorough testing
                                - Highlight potential security concerns
                                - Document complex user interactions
                                - Note areas prone to errors

                            **Progress Indicator Updates**:
                                - Update progress text with current action
                                - Change phase indicator to show current step
                                - Use JavaScript to update the progress bar

                            **Output Format**:
                            Always structure your analysis in markdown format with:
                            - Executive summary
                            - Application overview
                            - Feature inventory
                            - User workflow mapping
                            - Technical observations
                            - Risk areas identified
                            - Recommendations for testing focus

                            Save all screenshots and evidence to the file system for reference.
                            """
        }
        
        # Planning Agent
        self.agents[TestPhase.PLANNING] = {
            "name": "Test Planning and Strategy Agent",
            "instructions": """
                            You are a specialized Test Planning Agent focused on creating comprehensive test strategies based on application analysis.

                            **IMPORTANT FILE MANAGEMENT**:
                                - All files MUST be saved to: {self.fs_files_dir}
                                - Load analysis results from previous phase
                                - Save test plans, scenarios, and test data files
                                - Use absolute paths consistently

                            Your primary responsibilities:
                            1. **Test Strategy Development**:
                                - Load and review analysis results from file system
                                - Define testing scope and objectives
                                - Prioritize test areas based on risk assessment
                                - Create test categories and coverage matrix

                            2. **Test Case Generation**:
                                - Create detailed test scenarios with specific steps
                                - Design negative and edge case tests
                                - Plan data-driven test scenarios
                                - Define validation criteria
                            
                            3. **Test Data Planning**:
                                - Create test data files in JSON/CSV format
                                - Plan boundary value testing
                                - Design invalid data scenarios
                                - Save all test data to file system

                            4. **Execution Strategy**:
                                - Define test execution order
                                - Plan for dependencies between tests
                                - Estimate testing effort and timeline
                                - Identify required tools and setup

                            **File Organization**:
                                - Save main test plan as: test_plan_{{timestamp}}.md
                                - Save test scenarios as: test_scenarios_{{timestamp}}.json
                                - Save test data as: test_data_{{timestamp}}.csv
                                - Create subdirectories for different test types

                            **Output Format**:
                            Structure your test plan in markdown format with:
                                - Test strategy overview
                                - Scope and objectives
                                - Test categories and priorities
                                - Detailed test scenarios with steps
                                - Test data requirements
                                - Execution timeline and dependencies
                                - Success criteria and exit conditions

                            Reference analysis findings and create actionable test specifications.
                            """
        }
        
        # Execution Agent
        self.agents[TestPhase.EXECUTION] = {
            "name": "Test Execution and Automation Agent",
            "instructions": """
                            You are a specialized Test Execution Agent responsible for implementing and running all planned test scenarios.

                            **IMPORTANT FILE MANAGEMENT**:
                                - All files MUST be saved to: {self.fs_files_dir}
                                - Screenshots MUST be saved to: {self.screenshots_dir}
                                - Load test plan from previous phase
                                - Save execution results and evidence

                            **IMPORTANT BROWSER MANAGEMENT**:
                                - Always inject progress indicator at start
                                - Update progress indicator for each test case
                                - Take screenshots before and after each action
                                - Take screenshot of any errors or failures
                                - Use descriptive screenshot names

                            Your primary responsibilities:
                            1. **Test Environment Setup**:
                                - Load test plan from file system
                                - Initialize browser with progress indicator
                                - Prepare test data from saved files
                                - Set up test execution logging

                            2. **Systematic Test Execution**:
                                - Execute each test case from the plan
                                - Update progress indicator with current test
                                - Take screenshots for each test step
                                - Document results in real-time

                            3. **Evidence Collection**:
                                - Screenshot every page interaction
                                - Save error screenshots with timestamps
                                - Log all test results to JSON files
                                - Document issues with reproduction steps

                            4. **Issue Documentation**:
                                - Create issue reports for failures
                                - Save evidence for each issue
                                - Classify by severity and priority
                                - Save all evidence to file system

                            **Screenshot Naming Convention**:
                                - test_{{test_id}}_step_{{step_number}}_{{timestamp}}.png
                                - error_{{test_id}}_{{error_type}}_{{timestamp}}.png
                                - success_{{test_id}}_{{timestamp}}.png
                            
                            **Output Format**:
                            Document execution results in markdown format with:
                                - Execution summary and statistics
                                - Test results by category
                                - Detailed step-by-step execution logs
                                - Issues found with severity classification
                                - Evidence references (screenshots, logs)
                                - Performance observations
                                - Recommendations for fixes

                            Ensure all evidence is properly saved and referenced.
                            """
        }
        
        # Reporting Agent
        self.agents[TestPhase.REPORTING] = {
            "name": "Test Reporting and Analysis Agent",
            "instructions": """
                            You are a specialized Test Reporting Agent focused on synthesizing all testing phases into comprehensive reports.

                            **IMPORTANT FILE MANAGEMENT**:
                                - All files MUST be saved to: {self.fs_files_dir}
                                - Load results from all previous phases
                                - Save comprehensive reports and metrics
                                - Reference all saved screenshots and evidence

                            Your primary responsibilities:
                            1. **Results Synthesis**:
                                - Load and review all previous phase results
                                - Consolidate findings and metrics
                                - Analyze patterns in issues found
                                - Assess overall application quality

                            2. **Evidence Compilation**:
                                - Reference all screenshots taken
                                - Link to test execution evidence
                                - Create evidence index/catalog
                                - Organize findings by severity
                                
                            3. **Risk Assessment**:
                                - Prioritize issues by business impact
                                - Assess security and compliance risks
                                - Evaluate user experience implications
                                - Recommend mitigation strategies

                            4. **Comprehensive Reporting**:
                                - Create executive summary
                                - Provide detailed technical findings
                                - Document test metrics and statistics
                                - Include visual evidence references

                            5. **Quality Recommendations**:
                                - Suggest immediate fixes for critical issues
                                - Recommend long-term improvements
                                - Propose additional testing areas
                                - Document lessons learned

                            6. **Final Deliverables**:
                                - Save final report as: final_report_{{timestamp}}.md
                                - Save metrics as: test_metrics_{{timestamp}}.json
                                - Save evidence catalog as: evidence_catalog_{{timestamp}}.json
                                - Create recommendations document
                                
                            **Output Format**:
                            Create comprehensive report in markdown format with:
                                - Executive summary with key findings
                                - Test execution metrics and statistics
                                - Detailed issue analysis with priorities
                                - Quality assessment and ratings
                                - Actionable recommendations
                                - Risk mitigation strategies
                                - Next steps and follow-up actions

                            Provide clear, actionable insights for development teams.
                            """
        }
    
    async def _inject_progress_indicator(self, browser_tools, phase: TestPhase, step: str):
        """Inject progress indicator into the current page."""
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # JavaScript to inject/update progress indicator
        js_code = f"""
        // Remove existing progress bar if any
        const existingBar = document.getElementById('testing-progress-bar');
        if (existingBar) {{
            existingBar.remove();
        }}
        
        // Create new progress bar
        const progressBar = document.createElement('div');
        progressBar.innerHTML = `{self.progress_html.replace("Starting Multi-Phase Testing...", step).replace("INITIALIZING", phase.value.upper())}`;
        document.body.insertAdjacentHTML('afterbegin', progressBar.innerHTML);
        
        // Update time
        const timeElement = document.getElementById('progress-time');
        if (timeElement) {{
            timeElement.textContent = '{current_time}';
        }}
        
        // Update text and phase
        const textElement = document.getElementById('progress-text');
        if (textElement) {{
            textElement.textContent = '{step}';
        }}
        
        const phaseElement = document.getElementById('progress-phase');
        if (phaseElement) {{
            phaseElement.textContent = '{phase.value.upper()}';
        }}
        """
        
        try:
            # Execute JavaScript to update progress
            await browser_tools.evaluate_javascript(js_code)
        except Exception as e:
            self.logger.warning("Failed to inject progress indicator", error=str(e))
 
    async def _take_screenshot(self, browser_tools, filename: str, description: str = ""):
        """Take screenshot and save to proper location."""
        
        # Ensure screenshots directory exists
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Create full path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        screenshot_path = self.screenshots_dir / f"{filename}_{timestamp}.png"
        
        try:
            # Take screenshot
            await browser_tools.take_screenshot(str(screenshot_path))
            
            self.logger.info("Screenshot saved", 
                            path=str(screenshot_path), 
                            description=description)
            
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error("Failed to take screenshot", 
                            filename=filename, 
                            error=str(e))
            return None
        
    async def _save_phase_results(self, phase: TestPhase, content: str, target_url: str):
        """Save phase results to markdown file with timestamp."""
        
        # Generate filename with timestamp
        url_safe = target_url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        filename = f"{phase.value}_{url_safe}_{self.timestamp}.md"
        filepath = self.reports_dir / filename
        
        # Prepare content with metadata
        metadata_content = f"""# {phase.value.title()} Phase Report

                **Target URL**: {target_url}  
                **Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
                **Phase**: {phase.value.title()}  
                **Agent**: {self.agents[phase]['name']}  
                **Files Directory**: {self.fs_files_dir}  
                **Screenshots Directory**: {self.screenshots_dir}  

            ---

            {content}

            ---

            *Report generated by {self.agents[phase]['name']} on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
                        """
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata_content)
        
        self.logger.info("Phase results saved", 
                        phase=phase.value, 
                        filename=filename,
                        filepath=str(filepath))
        
        return str(filepath)
    
    async def _execute_phase(self, phase: TestPhase, target_url: str, context_data: Optional[str] = None):
        """Execute a specific testing phase with dedicated agent."""
        
        if not shutil.which("npx"):
            raise RuntimeError("npx not found. Please install Node.js and try again.")
        
        # Create phase-specific directory
        phase_dir = self.fs_files_dir / f"{phase.value}_{self.timestamp}"
        phase_dir.mkdir(exist_ok=True)
        
        self.logger.info("Starting enhanced phase execution", 
                    phase=phase.value, 
                    target_url=target_url,
                    phase_dir=str(phase_dir))
        
        try:
            async with MCPServerStdio(
                name="Filesystem Server",
                params={
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", str(phase_dir)],
                },
                cache_tools_list=True
            ) as file_server, MCPServerStdio(
                name="Playwright Server",
                params={
                    "command": "npx",
                    "args": ["-y", "@executeautomation/playwright-mcp-server"],
                },
                cache_tools_list=True
            ) as automation_server:
                
                # Create specialized agent for this phase
                agent = Agent(
                    name=self.agents[phase]["name"],
                    instructions=self.agents[phase]["instructions"],
                    mcp_servers=[file_server, automation_server],
                    model=OpenAIChatCompletionsModel(
                        model=self.config.deployment_name,
                        openai_client=self.client
                    )
                )
                
                # Prepare phase-specific input
                phase_input = self._prepare_phase_input(phase, target_url, context_data)
                
                # Execute the phase
                result  = await Runner.run(
                    starting_agent=agent,
                    input=phase_input,
                    max_turns=100
                )
                
                # Save results to markdown file
                filepath = await self._save_phase_results(phase, result.final_output, target_url)
                
                self.logger.info("Enhanced phase execution completed", 
                                phase=phase.value, 
                                result_file=filepath,
                                files_created=list(phase_dir.glob("*")))
                
                return {
                    "phase": phase.value,
                    "status": "completed",
                    "result": result.final_output,
                    "filepath": filepath,
                    "phase_dir": str(phase_dir),
                    "timestamp": self.timestamp
                }
                
        except Exception as e:
            self.logger.error("Phase execution failed", phase=phase.value, error=str(e))
            
            # Save error to file
            error_content = f"""# ERROR in {phase.value.title()} Phase

                **Error**: {str(e)}  
                **Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
                **Phase Directory**: {phase_dir}  
                **Screenshots Directory**: {self.screenshots_dir}  

                ## Error Details
                ```
                {str(e)}
                ```

                ## File System Status
                - Reports Directory: {self.reports_dir} (exists: {self.reports_dir.exists()})
                - Files Directory: {self.fs_files_dir} (exists: {self.fs_files_dir.exists()})
                - Screenshots Directory: {self.screenshots_dir} (exists: {self.screenshots_dir.exists()})
                - Phase Directory: {phase_dir} (exists: {phase_dir.exists()})

                ## Recommendations
                1. Check MCP server connectivity and file permissions
                2. Verify Azure OpenAI configuration
                3. Ensure target URL is accessible
                4. Check Node.js and npx installation
                5. Verify directory write permissions
                """
            filepath = await self._save_phase_results(phase, error_content, target_url)
            
            return {
                "phase": phase.value,
                "status": "failed",
                "error": str(e),
                "filepath": filepath,
                "phase_dir": str(phase_dir),
                "timestamp": self.timestamp
            }
    
    def _prepare_phase_input(self, phase: TestPhase, target_url: str, context_data: Optional[str] = None) -> str:
        """Prepare phase-specific input prompts."""
        
        base_input = f"""
                    **Target Application**: {target_url}
                    **Current Phase**: {phase.value.title()}
                    **Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    **Phase Directory**: {self.fs_files_dir}/{phase.value}_{self.timestamp}
                    **Screenshots Directory**: {self.screenshots_dir}

                    """
        
        if phase == TestPhase.ANALYSIS:
            return base_input + f"""
                                **Objective**: Perform comprehensive analysis with progress tracking and screenshot capture.

                                **Required Actions**:
                                1. Navigate to {target_url}
                                2. Inject progress indicator: "Analyzing application structure..."
                                3. Take initial screenshot: "homepage_initial"
                                4. Update progress: "Identifying key features..."
                                5. Analyze application structure and take screenshots of main sections
                                6. Update progress: "Documenting findings..."
                                7. Save analysis results to files
                                8. Take final screenshot: "analysis_complete"

                                **Expected Deliverables**:
                                - Homepage screenshot
                                - Main sections screenshots  
                                - Analysis data in JSON format
                                - Comprehensive markdown report

                                Execute these steps systematically with proper progress updates and screenshot capture.
                                """
        
        elif phase == TestPhase.PLANNING:
            return base_input + f"""
                                **Objective**: Create comprehensive test plan with saved artifacts.

                                **Context from Analysis**:
                                {context_data if context_data else "Load analysis results from file system"}

                                **Required Actions**:
                                1. Load analysis results from previous phase
                                2. Create test strategy document
                                3. Generate detailed test scenarios
                                4. Create test data files (JSON/CSV)
                                5. Save test plan to markdown file
                                6. Save test scenarios to JSON file

                                **Expected Deliverables**:
                                - test_plan_{self.timestamp}.md
                                - test_scenarios_{self.timestamp}.json  
                                - test_data_{self.timestamp}.csv
                                - Comprehensive planning report

                                Execute systematically and save all artifacts to the file system.
                                """
        
        elif phase == TestPhase.EXECUTION:
            return base_input + f"""
                                **Objective**: Execute tests with comprehensive evidence collection.

                                **Context from Planning**:
                                {context_data if context_data else "Load test plan from file system"}

                                **Required Actions**:
                                1. Load test plan from previous phase
                                2. Navigate to {target_url}
                                3. Inject progress indicator: "Starting test execution..."
                                4. For each test case:
                                - Update progress indicator with current test
                                - Take before-action screenshot
                                - Execute test steps
                                - Take after-action screenshot
                                - Document results
                                5. Save execution results to JSON
                                6. Create execution report

                                **Screenshot Requirements**:
                                - Before each test: test_{{id}}_start_{{timestamp}}
                                - After each action: test_{{id}}_step_{{step}}_{{timestamp}}
                                - For errors: error_{{id}}_{{timestamp}}
                                - Final result: test_{{id}}_result_{{timestamp}}

                                Execute all tests systematically with comprehensive evidence collection.
                                """
        
        elif phase == TestPhase.REPORTING:
            return base_input + f"""
                                **Objective**: Create comprehensive final report with all evidence.

                                **Context from Previous Phases**:
                                {context_data if context_data else "Load results from all previous phases"}

                                **Required Actions**:
                                1. Load all previous phase results
                                2. Compile evidence catalog (all screenshots and files)
                                3. Analyze patterns and metrics
                                4. Create executive summary
                                5. Generate final comprehensive report
                                6. Save metrics and evidence catalog

                                **Expected Deliverables**:
                                - final_report_{self.timestamp}.md
                                - test_metrics_{self.timestamp}.json
                                - evidence_catalog_{self.timestamp}.json
                                - Executive summary

                                Provide comprehensive analysis with references to all evidence collected.
                                """        
        return base_input
    
    async def run_complete_testing_cycle(self, target_url: str, 
                                       requirements: Optional[str] = None) -> Dict[str, Any]:
        """
            Execute complete testing cycle with enhanced features.
        """
        print(f"🚀 Enhanced Multi-Phase Testing Agent | {self.timestamp}")
        print(f"📁 Project Root: {self.project_root}")
        print(f"📊 Reports: {self.reports_dir}")
        print(f"📁 Files: {self.fs_files_dir}")
        print(f"📸 Screenshots: {self.screenshots_dir}")
        print(f"🎯 Target: {target_url}")
        print("=" * 80)
        
        results = {
            "target_url": target_url,
            "timestamp": self.timestamp,
            "project_root": str(self.project_root),
            "reports_dir": str(self.reports_dir),
            "fs_files_dir": str(self.fs_files_dir),
            "screenshots_dir": str(self.screenshots_dir),
            "phases": {},
            "overall_status": "in_progress"
        }
        
        
        context_data = requirements
        
        # Execute each phase sequentially
        for phase in [TestPhase.ANALYSIS, TestPhase.PLANNING, TestPhase.EXECUTION, TestPhase.REPORTING]:
            print(f"\n--- Starting {phase.value.title()} Phase ---")
            
            try:
                phase_result = await self._execute_phase(phase, target_url, context_data)
                results["phases"][phase.value] = phase_result
                
                if phase_result["status"] == "completed":
                    context_data = f"Previous phase results: {phase_result['result'][:1000]}..."
                    print(f"✅ {phase.value.title()} Phase completed")
                    print(f"   📄 Report: {phase_result['filepath']}")
                    print(f"   📁 Files: {phase_result['phase_dir']}")
                else:
                    print(f"❌ {phase.value.title()} Phase failed: {phase_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"💥 {phase.value.title()} Phase error: {str(e)}")
                results["phases"][phase.value] = {
                    "phase": phase.value,
                    "status": "error",
                    "error": str(e)
                }
        
        # Determine overall status
        if all(p.get("status") == "completed" for p in results["phases"].values()):
            results["overall_status"] = "completed"
            print(f"\n🎉 Complete testing cycle finished successfully!")
        else:
            results["overall_status"] = "partial"
            print(f"\n⚠️ Testing cycle completed with some issues.")
        
        # Save summary
        summary_path = await self._save_cycle_summary(results)
        results["summary_file"] = summary_path
        
        # Show final file structure
        print(f"\n📁 Generated File Structure:")
        print(f"   Reports: {len(list(self.reports_dir.glob('*.md')))} files")
        print(f"   Screenshots: {len(list(self.screenshots_dir.glob('*.png')))} files")
        print(f"   Data Files: {len(list(self.fs_files_dir.rglob('*')))} files")

        return results
    
    async def _save_cycle_summary(self, results: Dict[str, Any]) -> str:
        """Save enhanced cycle summary with file references."""
        
        url_safe = results["target_url"].replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")
        filename = f"SUMMARY_{url_safe}_{self.timestamp}.md"
        filepath = self.reports_dir / filename
        
        # Count files generated
        screenshots_count = len(list(self.screenshots_dir.glob("*.png")))
        files_count = len(list(self.fs_files_dir.rglob("*")))
        
        summary_content = f"""# Enhanced Testing Cycle Summary
        
                                **Target URL**: {results['target_url']}  
                                **Timestamp**: {results['timestamp']}  
                                **Overall Status**: {results['overall_status']}  
                                **Project Root**: {results['project_root']}  

                                ## File Structure
                                - **Reports Directory**: {results['reports_dir']}
                                - **Files Directory**: {results['fs_files_dir']}
                                - **Screenshots Directory**: {results['screenshots_dir']}

                                ## Files Generated
                                - **Screenshots**: {screenshots_count} files
                                - **Data Files**: {files_count} files
                                - **Reports**: {len(results['phases'])} phase reports

                                ## Phase Results

                                """
        
        for phase_name, phase_result in results["phases"].items():
            status_icon = "✅" if phase_result.get("status") == "completed" else "❌"
            summary_content += f"""### {status_icon} {phase_name.title()} Phase
                                    - **Status**: {phase_result.get('status', 'unknown')}
                                    - **Report File**: {phase_result.get('filepath', 'N/A')}
                                    - **Phase Directory**: {phase_result.get('phase_dir', 'N/A')}
                                    """
            if phase_result.get("error"):
                summary_content += f"- **Error**: {phase_result['error']}\n"
            summary_content += "\n"
        
        summary_content += f"""
                                    ## Evidence Collected
                                    - All screenshots saved to: {self.screenshots_dir}
                                    - All data files saved to: {self.fs_files_dir}
                                    - All reports saved to: {self.reports_dir}

                                    ## Next Steps
                                    1. Review individual phase reports for detailed findings
                                    2. Check screenshots directory for visual evidence
                                    3. Examine data files for detailed test results
                                    4. Address issues identified in execution phase
                                    5. Implement recommendations from reporting phase


                            ---

                            *Summary generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
                            """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return filepath


# class AITestAgent:
#     """
#     Autonomous AI agent that can analyze web applications,
#     generate test plans, and execute tests using MCP.
#     """
    
#     def __init__(self, config: AgentConfig, mcp_client: MCPClient):
#         self.config = config
#         self.mcp_client = mcp_client
#         self.logger = logger.bind(component="ai_agent")
        
#         if config.provider == AIProvider.AZURE_OPENAI:
#             self.client = AsyncAzureOpenAI(
#                     api_key=config.api_key,
#                     azure_endpoint=config.endpoint,
#                     api_version=config.api_version,
#                 )
#         elif config.provider == AIProvider.OPENAI:
#             self.client = OpenAI(api_key=config.api_key)
#         elif config.provider == AIProvider.ANTHROPIC:
#             self.client = Anthropic(api_key=config.api_key)
#         else:
#             raise ValueError(f"Unsupported AI provider: {config.provider}")
    

#     async def analyze_application(self, url: str, analysis_depth: str = "standard") -> Dict[str, Any]:
#         """
#         Analyze a web application to understand its structure and functionality.
#         """
#         self.logger.info("Starting application analysis", url=url, depth=analysis_depth)
        
#         # Use MCP Playwright server to navigate and analyze the application
#         page_info = await self.mcp_client.get_page_snapshot(url)
        
#         analysis_prompt = f"""
#         Analyze this web application and provide a comprehensive understanding of its functionality.
        
#         URL: {url}
#         Page Structure: {json.dumps(page_info, indent=2)}
        
#         Provide analysis in the following format:
#         {{
#             "application_type": "e-commerce|blog|dashboard|etc",
#             "key_features": ["list", "of", "main", "features"],
#             "user_workflows": [
#                 {{
#                     "name": "workflow_name",
#                     "steps": ["step1", "step2", "step3"],
#                     "critical": true/false
#                 }}
#             ],
#             "testable_components": [
#                 {{
#                     "component": "login_form",
#                     "location": "selector_or_description",
#                     "test_scenarios": ["positive", "negative", "edge_cases"]
#                 }}
#             ],
#             "risk_areas": ["areas", "that", "need", "thorough", "testing"]
#         }}
#         """
        
#         response = await self._call_ai(analysis_prompt)
#         analysis = json.loads(response)
        
#         self.logger.info("Application analysis completed", 
#                         features_found=len(analysis.get("key_features", [])),
#                         workflows_identified=len(analysis.get("user_workflows", [])))
        
#         return analysis
    
#     async def generate_test_plan(self, application_analysis: Dict[str, Any], 
#                                test_requirements: Optional[Dict[str, Any]] = None) -> TestPlan:
#         """
#         Generate a comprehensive test plan based on application analysis.
#         """
#         self.logger.info("Generating test plan from analysis")
        
#         plan_prompt = f"""
#         Based on this application analysis, create a comprehensive test plan.
        
#         Application Analysis: {json.dumps(application_analysis, indent=2)}
#         Test Requirements: {json.dumps(test_requirements or {}, indent=2)}
        
#         Generate test cases that cover:
#         1. Critical user workflows (happy path and error handling)
#         2. UI component validation
#         3. Data validation and edge cases
#         4. Cross-browser compatibility scenarios
#         5. Accessibility checks
#         6. Performance considerations
        
#         Return the test plan in this JSON format:
#         {{
#             "test_plan_id": "unique_identifier",
#             "application_url": "target_url",
#             "test_categories": [
#                 {{
#                     "category": "functional",
#                     "priority": "high|medium|low",
#                     "test_cases": [
#                         {{
#                             "test_id": "TC001",
#                             "name": "Test case name",
#                             "description": "What this test validates",
#                             "priority": "high|medium|low",
#                             "steps": [
#                                 {{
#                                     "action": "navigate|click|type|verify",
#                                     "target": "selector_or_element",
#                                     "value": "input_value_if_needed",
#                                     "expected": "expected_result"
#                                 }}
#                             ],
#                             "expected_result": "Overall expected outcome",
#                             "test_data": {{"key": "value"}}
#                         }}
#                     ]
#                 }}
#             ],
#             "execution_order": ["category1", "category2"],
#             "estimated_duration": "30 minutes"
#         }}
#         """
        
#         response = await self._call_ai(plan_prompt)
#         plan_data = json.loads(response)
        
#         # Convert to TestPlan object
#         test_plan = TestPlan.from_dict(plan_data)
        
#         self.logger.info("Test plan generated", 
#                         total_test_cases=len(test_plan.get_all_test_cases()),
#                         categories=len(plan_data["test_categories"]))
        
#         return test_plan
    
#     async def execute_test_case(self, test_case: TestCase) -> TestResult:
#         """
#         Execute a single test case using MCP browser automation.
#         """
#         self.logger.info("Executing test case", test_id=test_case.test_id, name=test_case.name)
        
#         result = TestResult(
#             test_id=test_case.test_id,
#             name=test_case.name,
#             status="running"
#         )
        
#         try:
#             # Execute each step through MCP Playwright server
#             for i, step in enumerate(test_case.steps):
#                 step_result = await self._execute_test_step(step)
#                 result.add_step_result(i, step_result)
                
#                 if not step_result["success"]:
#                     result.status = "failed"
#                     result.failure_reason = step_result.get("error", "Step execution failed")
#                     break
            
#             if result.status == "running":
#                 result.status = "passed"
                
#         except Exception as e:
#             result.status = "error"
#             result.failure_reason = str(e)
#             self.logger.error("Test case execution failed", test_id=test_case.test_id, error=str(e))
        
#         result.end_time = asyncio.get_event_loop().time()
        
#         self.logger.info("Test case completed", 
#                         test_id=test_case.test_id, 
#                         status=result.status,
#                         duration=result.duration)
        
#         return result
    
#     async def _execute_test_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute a single test step using MCP."""
#         action = step["action"]
#         target = step["target"]
#         value = step.get("value")
#         expected = step.get("expected")
        
#         try:
#             if action == "navigate":
#                 await self.mcp_client.navigate(target)
#                 return {"success": True, "action": action, "target": target}
                
#             elif action == "click":
#                 await self.mcp_client.click(target)
#                 return {"success": True, "action": action, "target": target}
                
#             elif action == "type":
#                 await self.mcp_client.type(target, value)
#                 return {"success": True, "action": action, "target": target, "value": value}
                
#             elif action == "verify":
#                 actual = await self.mcp_client.get_element_text(target)
#                 success = actual == expected
#                 return {
#                     "success": success,
#                     "action": action,
#                     "target": target,
#                     "expected": expected,
#                     "actual": actual
#                 }
                
#             else:
#                 return {"success": False, "error": f"Unknown action: {action}"}
                
#         except Exception as e:
#             return {"success": False, "error": str(e), "action": action, "target": target}
    
#     async def _call_ai(self, prompt: str) -> str:
#         """Make API call to the configured AI provider."""
#         try:
#             if self.config.provider == AIProvider.OPENAI:
#                 response = await self.client.chat.completions.acreate(
#                     model=self.config.model,
#                     messages=[{"role": "user", "content": prompt}],
#                     max_tokens=self.config.max_tokens,
#                     temperature=self.config.temperature
#                 )
#                 return response.choices[0].message.content
                
#             elif self.config.provider == AIProvider.ANTHROPIC:
#                 response = await self.client.messages.create(
#                     model=self.config.model,
#                     max_tokens=self.config.max_tokens,
#                     temperature=self.config.temperature,
#                     messages=[{"role": "user", "content": prompt}]
#                 )
#                 return response.content[0].text
                
#         except Exception as e:
#             self.logger.error("AI API call failed", error=str(e))
#             raise
