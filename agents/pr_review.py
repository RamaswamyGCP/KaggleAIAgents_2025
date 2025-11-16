"""
PR Review Agent with Sequential workflow.

This agent reviews pull requests using a sequential workflow:
1. Code Analysis - Analyzes code changes
2. Security Check - Identifies security vulnerabilities  
3. Generate Review - Creates comprehensive review comments

This demonstrates the Sequential Agent pattern in ADK.
"""

from typing import Dict, Any
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.settings import get_settings
from observability.logger import get_logger
from tools.custom_tools import get_pr_details, get_pr_diff, add_review_comment
from tools.github_mcp import get_github_mcp_client

settings = get_settings()
logger = get_logger("PRReviewAgent")


# Retry configuration for API calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)


def create_code_analysis_agent() -> Agent:
    """
    Create an agent that analyzes code changes in a PR.
    
    Returns:
        Agent configured for code analysis
    """
    return Agent(
        name="CodeAnalysisAgent",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a code analysis specialist. Your job is to:

1. Review the code changes in the pull request
2. Identify code quality issues:
   - Complexity problems
   - Missing error handling
   - Poor naming conventions
   - Code duplication
   - Performance issues
3. Check for best practice violations
4. Note any missing tests

Provide your analysis in a structured format with:
- File name
- Line number
- Issue type
- Description
- Recommendation

Be constructive and specific in your feedback.""",
        tools=[get_pr_details, get_pr_diff],
        output_key="code_analysis"
    )


def create_security_check_agent() -> Agent:
    """
    Create an agent that performs security analysis.
    
    Returns:
        Agent configured for security checking
    """
    return Agent(
        name="SecurityCheckAgent",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a security analysis specialist. Your job is to:

1. Review the code changes for security vulnerabilities:
   - SQL Injection risks
   - Cross-Site Scripting (XSS)
   - Hardcoded secrets/credentials
   - Insecure authentication
   - Missing input validation
   - Insecure data storage
   - Exposure of sensitive information

2. Rate each vulnerability by severity:
   - CRITICAL: Immediate security risk
   - HIGH: Significant security concern
   - MEDIUM: Should be addressed
   - LOW: Minor security improvement

3. Provide specific remediation steps for each issue

Access the code analysis from the previous step: {code_analysis}

Focus ONLY on security issues. Be thorough and specific.""",
        tools=[get_pr_diff],
        output_key="security_analysis"
    )


def create_review_generator_agent() -> Agent:
    """
    Create an agent that generates the final PR review.
    
    Returns:
        Agent configured for review generation
    """
    return Agent(
        name="ReviewGeneratorAgent",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a PR review specialist. Your job is to:

1. Combine the code analysis and security analysis:
   - Code Analysis: {code_analysis}
   - Security Analysis: {security_analysis}

2. Create a comprehensive, well-structured PR review with:
   - Summary of changes
   - Critical issues that MUST be fixed
   - Important suggestions for improvement
   - Minor recommendations
   - Positive feedback on good practices

3. Format your review professionally:
   - Start with an overview
   - Group issues by severity
   - Provide actionable recommendations
   - Be constructive and helpful

4. Include specific file names and line numbers for each issue

Your review should help the developer improve their code while being 
encouraging and constructive.""",
        output_key="final_review"
    )


def create_pr_review_agent() -> SequentialAgent:
    """
    Create the main PR Review agent with sequential workflow.
    
    This agent coordinates three sub-agents in sequence:
    1. Code Analysis
    2. Security Check
    3. Review Generation
    
    Returns:
        SequentialAgent configured for PR review
    """
    logger.info("Creating PR Review Agent (Sequential workflow)")
    
    # Create sub-agents
    code_analyzer = create_code_analysis_agent()
    security_checker = create_security_check_agent()
    review_generator = create_review_generator_agent()
    
    # Create sequential workflow
    pr_review_agent = SequentialAgent(
        name="PRReviewAgent",
        sub_agents=[
            code_analyzer,
            security_checker,
            review_generator
        ]
    )
    
    logger.info("✅ PR Review Agent created with 3 sequential sub-agents")
    
    return pr_review_agent


# Helper function to run PR review
async def review_pull_request(
    repo: str,
    pr_number: int,
    post_comments: bool = False
) -> Dict[str, Any]:
    """
    Review a pull request using the PR Review Agent.
    
    Args:
        repo: Repository name (owner/repo)
        pr_number: Pull request number
        post_comments: Whether to post comments to GitHub
        
    Returns:
        Review results
    """
    from google.adk.runners import InMemoryRunner
    
    logger.agent_started("PRReviewAgent", "Sequential", repo=repo, pr_number=pr_number)
    
    try:
        # Create agent
        agent = create_pr_review_agent()
        
        # Create runner
        runner = InMemoryRunner(agent=agent)
        
        # Run the review
        query = f"Review pull request #{pr_number} in repository {repo}"
        response = await runner.run(query)
        
        # Extract the final review
        final_review = None
        if hasattr(response, 'content'):
            final_review = response.content
        
        result = {
            "status": "success",
            "repo": repo,
            "pr_number": pr_number,
            "review": final_review,
            "comments_posted": post_comments
        }
        
        # Optionally post comments
        if post_comments and final_review:
            comment_result = add_review_comment(
                repo=repo,
                pr_number=pr_number,
                comment=final_review
            )
            result["comment_posted"] = comment_result.get("status") == "success"
        
        logger.agent_completed("PRReviewAgent", 5.0)
        
        return result
    
    except Exception as e:
        logger.error(f"PR review failed: {e}", error=e, repo=repo, pr_number=pr_number)
        return {
            "status": "error",
            "error_message": str(e),
            "repo": repo,
            "pr_number": pr_number
        }


if __name__ == "__main__":
    import asyncio
    
    print("Testing PR Review Agent (Sequential Workflow)...\n")
    
    # Test with mock data
    result = asyncio.run(review_pull_request(
        repo="RamaswamyGCP/KaggleAgentTestRepo",
        pr_number=1,
        post_comments=False
    ))
    
    if result["status"] == "success":
        print(f"✅ PR Review completed for PR #{result['pr_number']}")
        print(f"\nReview:\n{result.get('review', 'No review generated')[:200]}...")
    else:
        print(f"❌ PR Review failed: {result['error_message']}")

