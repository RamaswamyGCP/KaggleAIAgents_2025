"""
Issue Triage Agent with Parallel workflow.

This agent triages GitHub issues using parallel execution:
1. Category Classifier - Determines issue category (bug, feature, docs, etc.)
2. Priority Assessor - Assesses urgency and priority (simultaneously)

Both sub-agents run in parallel, then results are combined.

This demonstrates the Parallel Agent pattern in ADK.
"""

from typing import Dict, Any, List
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.settings import get_settings
from observability.logger import get_logger
from tools.custom_tools import get_issue_details, update_issue_labels

settings = get_settings()
logger = get_logger("IssueTriageAgent")


# Retry configuration
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)


def create_category_classifier() -> Agent:
    """
    Create an agent that classifies issue categories.
    
    Returns:
        Agent configured for category classification
    """
    return Agent(
        name="CategoryClassifier",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are an issue categorization specialist. Your job is to:

1. Read the issue title and description
2. Classify the issue into ONE primary category:
   - bug: Something is broken or not working correctly
   - feature: Request for new functionality
   - enhancement: Improvement to existing functionality
   - docs: Documentation update or fix
   - security: Security vulnerability or concern
   - performance: Performance issue or optimization
   - question: User question or help request
   - infrastructure: DevOps, CI/CD, deployment issues

3. Optionally suggest secondary categories if applicable

4. Provide reasoning for your classification

Output format:
- Primary Category: [category]
- Secondary Categories: [list if any]
- Reasoning: [your explanation]

Be precise and consistent in your classifications.""",
        tools=[get_issue_details],
        output_key="category_classification"
    )


def create_priority_assessor() -> Agent:
    """
    Create an agent that assesses issue priority.
    
    Returns:
        Agent configured for priority assessment
    """
    return Agent(
        name="PriorityAssessor",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a priority assessment specialist. Your job is to:

1. Read the issue title and description
2. Assess the priority level:
   - critical: System down, data loss, security breach
   - high: Major functionality broken, affects many users
   - medium: Important but not urgent, workaround exists
   - low: Nice to have, minor issue, cosmetic

3. Consider factors:
   - Impact: How many users are affected?
   - Severity: How serious is the problem?
   - Workaround: Is there a temporary solution?
   - Business value: How important is this?

4. Suggest urgency labels:
   - urgent: Needs immediate attention
   - needs-review: Requires further investigation
   - good-first-issue: Suitable for new contributors

Output format:
- Priority: [critical/high/medium/low]
- Urgency Labels: [list]
- Impact Assessment: [your analysis]
- Recommendation: [next steps]

Be objective and consider user impact.""",
        tools=[get_issue_details],
        output_key="priority_assessment"
    )


def create_label_applicator() -> Agent:
    """
    Create an agent that applies labels based on classification and priority.
    
    Returns:
        Agent configured for label application
    """
    return Agent(
        name="LabelApplicator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are a label application specialist. Your job is to:

1. Review the classification and priority assessment:
   - Category: {category_classification}
   - Priority: {priority_assessment}

2. Determine the complete set of labels to apply:
   - Include the primary category
   - Add priority level
   - Add urgency labels if applicable
   - Add relevant tags (frontend, backend, api, etc.)

3. Create a concise summary for the issue triage:
   - What type of issue this is
   - How urgent it is
   - Who should handle it
   - Recommended next steps

Output the final label set and summary.

Be comprehensive but avoid over-labeling.""",
        tools=[update_issue_labels],
        output_key="final_labels"
    )


def create_issue_triage_agent() -> SequentialAgent:
    """
    Create the main Issue Triage agent with parallel workflow.
    
    This agent:
    1. Runs category classification and priority assessment in PARALLEL
    2. Then applies labels based on combined results (sequential)
    
    Returns:
        Agent configured for issue triage
    """
    logger.info("Creating Issue Triage Agent (Parallel workflow)")
    
    # Create sub-agents for parallel execution
    category_classifier = create_category_classifier()
    priority_assessor = create_priority_assessor()
    
    # Parallel agent runs both simultaneously
    parallel_analyzers = ParallelAgent(
        name="ParallelAnalyzers",
        sub_agents=[category_classifier, priority_assessor]
    )
    
    # Label applicator runs after parallel analysis
    label_applicator = create_label_applicator()
    
    # Sequential agent coordinates the workflow
    issue_triage_agent = SequentialAgent(
        name="IssueTriageAgent",
        sub_agents=[parallel_analyzers, label_applicator]
    )
    
    logger.info("✅ Issue Triage Agent created with parallel analysis")
    
    return issue_triage_agent


# Helper function to triage issues
async def triage_issue(
    repo: str,
    issue_number: int,
    apply_labels: bool = False
) -> Dict[str, Any]:
    """
    Triage a GitHub issue.
    
    Args:
        repo: Repository name (owner/repo)
        issue_number: Issue number
        apply_labels: Whether to apply labels to the issue
        
    Returns:
        Triage results
    """
    from google.adk.runners import InMemoryRunner
    
    logger.agent_started(
        "IssueTriageAgent",
        "Parallel",
        repo=repo,
        issue_number=issue_number
    )
    
    try:
        # Create agent
        agent = create_issue_triage_agent()
        
        # Create runner
        runner = InMemoryRunner(agent=agent)
        
        # Run the triage
        query = f"Triage issue #{issue_number} in repository {repo}"
        response = await runner.run(query)
        
        # Extract results
        final_labels = None
        if hasattr(response, 'content'):
            final_labels = response.content
        
        result = {
            "status": "success",
            "repo": repo,
            "issue_number": issue_number,
            "triage_result": final_labels,
            "labels_applied": apply_labels
        }
        
        logger.agent_completed("IssueTriageAgent", 3.0)
        
        return result
    
    except Exception as e:
        logger.error(
            f"Issue triage failed: {e}",
            error=e,
            repo=repo,
            issue_number=issue_number
        )
        return {
            "status": "error",
            "error_message": str(e),
            "repo": repo,
            "issue_number": issue_number
        }


async def triage_multiple_issues(
    repo: str,
    issue_numbers: List[int],
    apply_labels: bool = False
) -> List[Dict[str, Any]]:
    """
    Triage multiple issues efficiently.
    
    This demonstrates how parallel agents can process
    multiple items concurrently.
    
    Args:
        repo: Repository name (owner/repo)
        issue_numbers: List of issue numbers
        apply_labels: Whether to apply labels
        
    Returns:
        List of triage results
    """
    import asyncio
    
    logger.info(
        f"Triaging {len(issue_numbers)} issues in parallel",
        repo=repo,
        issue_count=len(issue_numbers)
    )
    
    # Create tasks for parallel execution
    tasks = [
        triage_issue(repo, issue_num, apply_labels)
        for issue_num in issue_numbers
    ]
    
    # Run all triages in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error dicts
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "status": "error",
                "error_message": str(result),
                "issue_number": issue_numbers[i]
            })
        else:
            processed_results.append(result)
    
    logger.info(
        f"Completed triaging {len(issue_numbers)} issues",
        successful=sum(1 for r in processed_results if r.get("status") == "success")
    )
    
    return processed_results


if __name__ == "__main__":
    import asyncio
    
    print("Testing Issue Triage Agent (Parallel Workflow)...\n")
    
    # Test single issue
    print("1. Testing single issue triage:")
    result = asyncio.run(triage_issue(
        repo="RamaswamyGCP/KaggleAgentTestRepo",
        issue_number=1,
        apply_labels=False
    ))
    
    if result["status"] == "success":
        print(f"✅ Issue #{result['issue_number']} triaged successfully")
    else:
        print(f"❌ Triage failed: {result['error_message']}")
    
    # Test multiple issues in parallel
    print("\n2. Testing multiple issues in parallel:")
    results = asyncio.run(triage_multiple_issues(
        repo="RamaswamyGCP/KaggleAgentTestRepo",
        issue_numbers=[1, 2, 3],
        apply_labels=False
    ))
    
    successful = sum(1 for r in results if r.get("status") == "success")
    print(f"✅ {successful}/{len(results)} issues triaged successfully")

