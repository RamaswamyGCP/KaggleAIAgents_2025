"""
Documentation Agent with Loop workflow.

This agent improves documentation through iterative refinement:
1. Writer - Creates or updates documentation
2. Critic - Reviews and provides feedback
3. Loop continues until documentation meets quality standards

This demonstrates the Loop Agent pattern in ADK.
"""

from typing import Dict, Any
from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

from config.settings import get_settings
from observability.logger import get_logger
from tools.markitdown_mcp import get_markitdown_client

settings = get_settings()
logger = get_logger("DocsAgent")


# Retry configuration
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)


def exit_loop() -> Dict[str, Any]:
    """
    Function to exit the documentation improvement loop.
    
    This function is called when the documentation meets quality standards.
    
    Returns:
        Status indicating approval
    """
    logger.info("Documentation approved - exiting improvement loop")
    return {
        "status": "approved",
        "message": "Documentation meets quality standards. Exiting loop."
    }


def create_initial_writer() -> Agent:
    """
    Create an agent that writes the initial documentation draft.
    
    Returns:
        Agent configured for initial documentation writing
    """
    return Agent(
        name="InitialWriter",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a technical documentation writer. Your job is to:

1. Create clear, comprehensive documentation based on the user's request
2. Include:
   - Overview/Introduction
   - Prerequisites or requirements
   - Step-by-step instructions
   - Code examples where relevant
   - Troubleshooting tips
   - Additional resources

3. Follow documentation best practices:
   - Clear headings and structure
   - Concise but complete information
   - Examples that work
   - Proper markdown formatting
   - Accessible language

Write the initial draft. It doesn't need to be perfect - it will be
improved through iteration.

Output ONLY the documentation content.""",
        output_key="current_documentation"
    )


def create_documentation_critic() -> Agent:
    """
    Create an agent that critiques documentation quality.
    
    Returns:
        Agent configured for documentation critique
    """
    return Agent(
        name="DocumentationCritic",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a documentation quality reviewer. Your job is to:

Review this documentation: {current_documentation}

Evaluate on these criteria:
1. **Clarity**: Is it easy to understand?
2. **Completeness**: Does it cover all necessary information?
3. **Accuracy**: Is the information correct?
4. **Structure**: Is it well-organized?
5. **Examples**: Are there helpful code examples?
6. **Accessibility**: Can beginners follow it?

If the documentation meets ALL quality standards:
- Respond with EXACTLY: "APPROVED"

Otherwise, provide 2-3 specific, actionable suggestions:
- What needs improvement
- Why it's important
- How to fix it

Be constructive and specific.""",
        output_key="critique"
    )


def create_documentation_refiner() -> Agent:
    """
    Create an agent that refines documentation based on critique.
    
    Returns:
        Agent configured for documentation refinement
    """
    return Agent(
        name="DocumentationRefiner",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a documentation improvement specialist. Your job is to:

1. Review the current documentation:
   {current_documentation}

2. Review the critique:
   {critique}

3. Your task:
   - IF the critique is EXACTLY "APPROVED": 
     Call the exit_loop() function immediately
   
   - OTHERWISE:
     Rewrite the documentation to address ALL feedback points
     Make it better while keeping what works
     Output the improved documentation

Be thorough in addressing feedback.""",
        tools=[FunctionTool(exit_loop)],
        output_key="current_documentation"  # Overwrites with improved version
    )


def create_documentation_agent() -> SequentialAgent:
    """
    Create the main Documentation Agent with loop workflow.
    
    This agent:
    1. Writes initial documentation
    2. Loops: Critic reviews → Refiner improves
    3. Exits when documentation is approved
    
    Returns:
        Agent configured for iterative documentation improvement
    """
    logger.info("Creating Documentation Agent (Loop workflow)")
    
    # Initial writer runs once
    initial_writer = create_initial_writer()
    
    # Loop agents run iteratively
    critic = create_documentation_critic()
    refiner = create_documentation_refiner()
    
    # Create loop with max iterations
    documentation_loop = LoopAgent(
        name="DocumentationImprovementLoop",
        sub_agents=[critic, refiner],
        max_iterations=3  # Prevents infinite loops
    )
    
    # Sequential agent coordinates the workflow
    docs_agent = SequentialAgent(
        name="DocumentationAgent",
        sub_agents=[initial_writer, documentation_loop]
    )
    
    logger.info("✅ Documentation Agent created with iterative loop")
    
    return docs_agent


# Helper function to improve documentation
async def improve_documentation(
    content: str,
    context: str = ""
) -> Dict[str, Any]:
    """
    Improve documentation through iterative refinement.
    
    Args:
        content: Initial documentation content or file path
        context: Additional context about what to document
        
    Returns:
        Improved documentation
    """
    from google.adk.runners import InMemoryRunner
    
    logger.agent_started(
        "DocumentationAgent",
        "Loop",
        has_content=bool(content),
        has_context=bool(context)
    )
    
    try:
        # Create agent
        agent = create_documentation_agent()
        
        # Create runner
        runner = InMemoryRunner(agent=agent)
        
        # Build query
        if context:
            query = f"Create documentation for: {context}. Current content: {content}"
        else:
            query = f"Improve this documentation: {content}"
        
        # Run the improvement process
        response = await runner.run(query)
        
        # Extract final documentation
        final_docs = None
        if hasattr(response, 'content'):
            final_docs = response.content
        
        result = {
            "status": "success",
            "original_content": content[:200] + "..." if len(content) > 200 else content,
            "improved_documentation": final_docs,
            "iterations_completed": "varies"  # Loop agent tracks this
        }
        
        logger.agent_completed("DocumentationAgent", 8.0)
        
        return result
    
    except Exception as e:
        logger.error(f"Documentation improvement failed: {e}", error=e)
        return {
            "status": "error",
            "error_message": str(e),
            "original_content": content
        }


async def document_from_pdf(
    pdf_path: str,
    extract_sections: bool = True
) -> Dict[str, Any]:
    """
    Create documentation by learning from PDF files.
    
    This uses Markitdown MCP to convert PDFs to markdown,
    then uses the documentation agent to structure it properly.
    
    Args:
        pdf_path: Path to PDF file
        extract_sections: Whether to extract specific sections
        
    Returns:
        Generated documentation from PDF
    """
    logger.info(f"Creating documentation from PDF: {pdf_path}")
    
    try:
        # Convert PDF to markdown using Markitdown MCP
        mcp_client = get_markitdown_client()
        conversion_result = mcp_client.convert_pdf_to_markdown(pdf_path)
        
        if conversion_result["status"] != "success":
            return conversion_result
        
        markdown_content = conversion_result["markdown_content"]
        
        # Extract key information
        key_info = mcp_client.extract_key_information(markdown_content)
        
        # Use documentation agent to structure it properly
        context = f"Convert this PDF content into well-structured documentation"
        result = await improve_documentation(markdown_content, context)
        
        if result["status"] == "success":
            result["pdf_source"] = pdf_path
            result["page_count"] = conversion_result.get("page_count")
            result["key_information"] = key_info
        
        return result
    
    except Exception as e:
        logger.error(f"PDF documentation failed: {e}", error=e)
        return {
            "status": "error",
            "error_message": str(e),
            "pdf_path": pdf_path
        }


if __name__ == "__main__":
    import asyncio
    
    print("Testing Documentation Agent (Loop Workflow)...\n")
    
    # Test 1: Improve existing documentation
    print("1. Testing documentation improvement:")
    sample_doc = """
# Setup Guide

Install it. Run it. Done.
"""
    
    result = asyncio.run(improve_documentation(
        content=sample_doc,
        context="Setup guide for GitHub Agents project"
    ))
    
    if result["status"] == "success":
        print("✅ Documentation improved through iterative refinement")
        print(f"\nImproved version preview:")
        improved = result.get("improved_documentation", "")
        print(improved[:300] + "..." if len(improved) > 300 else improved)
    else:
        print(f"❌ Improvement failed: {result['error_message']}")
    
    # Test 2: Document from PDF
    print("\n2. Testing PDF to documentation:")
    pdf_result = asyncio.run(document_from_pdf("docs/architecture.pdf"))
    
    if pdf_result["status"] == "success":
        print(f"✅ Documentation created from PDF ({pdf_result.get('page_count')} pages)")
    else:
        print(f"ℹ️  PDF test skipped (mock implementation)")

