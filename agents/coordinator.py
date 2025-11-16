"""
Root Coordinator Agent with Session Management.

This agent coordinates all specialized agents and maintains conversation
context using DatabaseSessionService. It acts as the main entry point for
all user interactions.

Key features:
- Session management for persistent conversations
- Delegation to specialized agents (PR Review, Issue Triage, Docs)
- Memory access across sessions
- Integration with A2A services
"""

from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pathlib import Path

from config.settings import get_settings
from observability.logger import get_logger
from agents.pr_review import create_pr_review_agent
from agents.issue_triage import create_issue_triage_agent
from agents.docs_agent import create_documentation_agent
from tools.custom_tools import CUSTOM_GITHUB_TOOLS

settings = get_settings()
logger = get_logger("CoordinatorAgent")


# Retry configuration
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)


def create_session_service():
    """
    Create the session service for maintaining conversation state.
    
    For capstone demonstration, we use InMemorySessionService.
    In production, this would be DatabaseSessionService with SQLite/PostgreSQL.
    
    Returns:
        Session service instance
    """
    # For now, using InMemorySessionService for simplicity
    # In production: DatabaseSessionService(db_url=settings.DATABASE_URL)
    session_service = InMemorySessionService()
    logger.info("Session service created (InMemory)")
    return session_service


def create_coordinator_agent(
    use_a2a_services: bool = False
) -> Agent:
    """
    Create the root coordinator agent.
    
    This agent:
    1. Understands user intent
    2. Delegates to specialized agents
    3. Maintains conversation context
    4. Can access A2A services for knowledge
    
    Args:
        use_a2a_services: Whether to connect to A2A services
        
    Returns:
        Configured coordinator agent
    """
    logger.info("Creating Root Coordinator Agent")
    
    # Create specialized agents
    pr_review_agent = create_pr_review_agent()
    issue_triage_agent = create_issue_triage_agent()
    docs_agent = create_documentation_agent()
    
    # Wrap agents as tools
    tools = [
        AgentTool(agent=pr_review_agent),
        AgentTool(agent=issue_triage_agent),
        AgentTool(agent=docs_agent),
    ]
    
    # Add custom GitHub tools
    tools.extend(CUSTOM_GITHUB_TOOLS)
    
    # Create coordinator
    coordinator = Agent(
        name="GitHubCoordinator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the GitHub Enterprise AI Coordinator. Your job is to help users
with GitHub operations by coordinating specialized agents and tools.

**Your Capabilities:**

1. **PR Review** (PRReviewAgent):
   - Review pull requests for code quality and security
   - Identify vulnerabilities and bugs
   - Provide constructive feedback
   - Use this for: "review PR", "check pull request", "analyze code changes"

2. **Issue Triage** (IssueTriageAgent):
   - Classify and prioritize GitHub issues
   - Apply appropriate labels
   - Assess urgency and impact
   - Use this for: "triage issue", "classify bug", "prioritize issues"

3. **Documentation** (DocumentationAgent):
   - Create and improve documentation
   - Learn from PDF files
   - Ensure documentation quality
   - Use this for: "improve docs", "create documentation", "update README"

4. **Direct GitHub Operations**:
   - Get PR details, issue details, repository info
   - Use these for quick information lookups

**How to work:**

1. **Understand the request**: What does the user want to do?
2. **Choose the right tool**: Which agent or tool is best for this task?
3. **Delegate**: Call the appropriate agent/tool
4. **Summarize**: Provide clear, helpful response to the user

**Remember:**
- Ask for clarification if the request is unclear
- Provide specific, actionable information
- Be helpful and constructive
- Remember context from previous messages in this session

**Example interactions:**

User: "Review PR #42 in my-repo/project"
You: Call PRReviewAgent with the repo and PR number

User: "Triage issues 10, 11, and 12"
You: Call IssueTriageAgent for each issue

User: "Help me understand our architecture"
You: Check if there's a PDF to learn from, then explain

Always be helpful, clear, and efficient!""",
        tools=tools
    )
    
    logger.info("✅ Coordinator Agent created with all specialized agents")
    
    return coordinator


class CoordinatorRunner:
    """
    Runner for the Coordinator Agent with session management.
    
    This class provides a high-level interface for interacting with
    the agent system while maintaining conversation state.
    """
    
    def __init__(self, app_name: str = "GitHubAgents"):
        """
        Initialize the coordinator runner.
        
        Args:
            app_name: Application name for session management
        """
        self.app_name = app_name
        self.session_service = create_session_service()
        self.coordinator = create_coordinator_agent()
        logger.info(f"Coordinator Runner initialized: {app_name}")
    
    async def run(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a query through the coordinator agent.
        
        Args:
            query: User query
            session_id: Optional session ID for maintaining context
            
        Returns:
            Response from the coordinator
        """
        from google.adk.runners import Runner
        
        # Use session ID or create new one
        if not session_id:
            session_id = f"session_{hash(query) % 10000}"
        
        logger.info(
            f"Processing query in session {session_id}",
            query_length=len(query)
        )
        
        try:
            # Create runner with session service
            runner = Runner(
                agent=self.coordinator,
                app_name=self.app_name,
                session_service=self.session_service
            )
            
            # Run the query
            response = await runner.run(query, session_id=session_id)
            
            # Extract response content
            response_text = ""
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            
            result = {
                "status": "success",
                "query": query,
                "response": response_text,
                "session_id": session_id
            }
            
            logger.info(
                "Query processed successfully",
                session_id=session_id,
                response_length=len(response_text)
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Query processing failed: {e}", error=e, query=query)
            return {
                "status": "error",
                "error_message": str(e),
                "query": query,
                "session_id": session_id
            }
    
    async def run_interactive(self):
        """
        Run interactive session with the coordinator.
        
        This allows continuous conversation with context maintained
        across multiple queries.
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        
        print("🤖 GitHub Enterprise AI Agent System")
        print("=" * 50)
        print(f"Session ID: {session_id}")
        print("Type 'exit' or 'quit' to end the session.\n")
        
        while True:
            try:
                # Get user input
                query = input("You: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye! Session ended.")
                    break
                
                # Process query
                result = await self.run(query, session_id=session_id)
                
                # Display response
                if result["status"] == "success":
                    print(f"\n🤖 Agent: {result['response']}\n")
                else:
                    print(f"\n❌ Error: {result['error_message']}\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}\n")
                logger.error(f"Interactive session error: {e}", error=e)


# Global coordinator instance
_coordinator_runner = None


def get_coordinator_runner() -> CoordinatorRunner:
    """
    Get or create the global coordinator runner instance.
    
    Returns:
        CoordinatorRunner instance
    """
    global _coordinator_runner
    
    if _coordinator_runner is None:
        _coordinator_runner = CoordinatorRunner()
    
    return _coordinator_runner


if __name__ == "__main__":
    import asyncio
    
    print("Testing Coordinator Agent...\n")
    
    # Test 1: Simple query
    print("1. Testing simple query:")
    runner = get_coordinator_runner()
    result = asyncio.run(runner.run(
        "What can you help me with?",
        session_id="test_session_1"
    ))
    
    if result["status"] == "success":
        print(f"✅ Response: {result['response'][:150]}...")
    else:
        print(f"❌ Error: {result['error_message']}")
    
    # Test 2: Multi-turn conversation
    print("\n2. Testing multi-turn conversation:")
    session_id = "test_session_2"
    
    queries = [
        "My name is Ramaswamy",
        "What's my name?",  # Should remember from previous query
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        result = asyncio.run(runner.run(query, session_id=session_id))
        if result["status"] == "success":
            print(f"Response: {result['response'][:100]}...")
    
    print("\n✅ Coordinator test complete!")

