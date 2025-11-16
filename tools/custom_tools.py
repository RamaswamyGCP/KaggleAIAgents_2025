"""
Custom GitHub operation tools.

This module provides custom functions for GitHub operations that can be used
as tools by the AI agents. These are simpler operations that don't require
MCP integration.
"""

from typing import Dict, List, Any, Optional
from observability.logger import get_logger

logger = get_logger("CustomTools")


def get_pr_details(repo: str, pr_number: int) -> Dict[str, Any]:
    """
    Get details about a pull request.
    
    This is a mock implementation for demonstration. In production,
    this would connect to GitHub API or use GitHub MCP.
    
    Args:
        repo: Repository name in format "owner/repo"
        pr_number: Pull request number
        
    Returns:
        Dictionary with PR details or error message
    """
    logger.tool_called("get_pr_details", {"repo": repo, "pr_number": pr_number})
    
    try:
        # Mock implementation - in production, use GitHub API
        mock_pr = {
            "status": "success",
            "pr_number": pr_number,
            "repo": repo,
            "title": f"Sample PR #{pr_number}",
            "author": "developer123",
            "state": "open",
            "files_changed": 5,
            "additions": 150,
            "deletions": 75,
            "commits": 3,
            "description": "This is a sample pull request for testing.",
            "branch": "feature/new-feature",
            "base_branch": "main",
            "created_at": "2025-01-15T10:00:00Z",
            "updated_at": "2025-01-15T14:30:00Z"
        }
        
        logger.tool_response("get_pr_details", "success", 0.1)
        return mock_pr
    
    except Exception as e:
        logger.error(f"Error getting PR details: {e}", error=e)
        return {
            "status": "error",
            "error_message": f"Failed to get PR details: {str(e)}"
        }


def get_pr_diff(repo: str, pr_number: int) -> Dict[str, Any]:
    """
    Get the code diff for a pull request.
    
    Args:
        repo: Repository name in format "owner/repo"
        pr_number: Pull request number
        
    Returns:
        Dictionary with diff content or error message
    """
    logger.tool_called("get_pr_diff", {"repo": repo, "pr_number": pr_number})
    
    try:
        # Mock implementation
        mock_diff = {
            "status": "success",
            "files": [
                {
                    "filename": "src/app.py",
                    "status": "modified",
                    "additions": 50,
                    "deletions": 20,
                    "patch": """
@@ -10,7 +10,7 @@ def authenticate(username, password):
-    query = f"SELECT * FROM users WHERE name = '{username}'"
+    query = "SELECT * FROM users WHERE name = ?"
+    cursor.execute(query, (username,))
"""
                },
                {
                    "filename": "src/auth.py",
                    "status": "modified",
                    "additions": 30,
                    "deletions": 15,
                    "patch": """
@@ -5,7 +5,7 @@ import os
-API_KEY = "sk_live_12345"
+API_KEY = os.getenv("API_KEY")
"""
                }
            ]
        }
        
        logger.tool_response("get_pr_diff", "success", 0.2)
        return mock_diff
    
    except Exception as e:
        logger.error(f"Error getting PR diff: {e}", error=e)
        return {
            "status": "error",
            "error_message": f"Failed to get PR diff: {str(e)}"
        }


def add_review_comment(
    repo: str, 
    pr_number: int, 
    comment: str,
    file_path: Optional[str] = None,
    line_number: Optional[int] = None
) -> Dict[str, Any]:
    """
    Add a review comment to a pull request.
    
    Args:
        repo: Repository name in format "owner/repo"
        pr_number: Pull request number
        comment: Comment text
        file_path: Optional file path for inline comment
        line_number: Optional line number for inline comment
        
    Returns:
        Dictionary with success status or error message
    """
    logger.tool_called(
        "add_review_comment",
        {
            "repo": repo,
            "pr_number": pr_number,
            "has_file_path": file_path is not None,
            "has_line_number": line_number is not None
        }
    )
    
    try:
        # Mock implementation
        result = {
            "status": "success",
            "message": "Comment added successfully",
            "comment_id": 12345,
            "comment_type": "inline" if file_path else "general"
        }
        
        logger.info(
            f"Review comment added to PR {pr_number}",
            repo=repo,
            comment_type=result["comment_type"]
        )
        logger.tool_response("add_review_comment", "success", 0.3)
        
        return result
    
    except Exception as e:
        logger.error(f"Error adding review comment: {e}", error=e)
        return {
            "status": "error",
            "error_message": f"Failed to add review comment: {str(e)}"
        }


def get_issue_details(repo: str, issue_number: int) -> Dict[str, Any]:
    """
    Get details about a GitHub issue.
    
    Args:
        repo: Repository name in format "owner/repo"
        issue_number: Issue number
        
    Returns:
        Dictionary with issue details or error message
    """
    logger.tool_called("get_issue_details", {"repo": repo, "issue_number": issue_number})
    
    try:
        # Mock implementation
        mock_issue = {
            "status": "success",
            "issue_number": issue_number,
            "repo": repo,
            "title": f"Issue #{issue_number}: Sample bug",
            "author": "user456",
            "state": "open",
            "labels": [],
            "description": "The application crashes when clicking submit button.",
            "created_at": "2025-01-14T09:00:00Z",
            "updated_at": "2025-01-14T09:00:00Z",
            "comments": 0
        }
        
        logger.tool_response("get_issue_details", "success", 0.1)
        return mock_issue
    
    except Exception as e:
        logger.error(f"Error getting issue details: {e}", error=e)
        return {
            "status": "error",
            "error_message": f"Failed to get issue details: {str(e)}"
        }


def update_issue_labels(
    repo: str, 
    issue_number: int, 
    labels: List[str]
) -> Dict[str, Any]:
    """
    Update labels on a GitHub issue.
    
    Args:
        repo: Repository name in format "owner/repo"
        issue_number: Issue number
        labels: List of label names to apply
        
    Returns:
        Dictionary with success status or error message
    """
    logger.tool_called(
        "update_issue_labels",
        {"repo": repo, "issue_number": issue_number, "labels": labels}
    )
    
    try:
        # Mock implementation
        result = {
            "status": "success",
            "message": f"Labels updated successfully: {', '.join(labels)}",
            "issue_number": issue_number,
            "labels_applied": labels
        }
        
        logger.info(
            f"Labels updated for issue {issue_number}",
            repo=repo,
            labels=labels
        )
        logger.tool_response("update_issue_labels", "success", 0.2)
        
        return result
    
    except Exception as e:
        logger.error(f"Error updating issue labels: {e}", error=e)
        return {
            "status": "error",
            "error_message": f"Failed to update issue labels: {str(e)}"
        }


def get_repository_info(repo: str) -> Dict[str, Any]:
    """
    Get general information about a repository.
    
    Args:
        repo: Repository name in format "owner/repo"
        
    Returns:
        Dictionary with repository info or error message
    """
    logger.tool_called("get_repository_info", {"repo": repo})
    
    try:
        # Mock implementation
        mock_repo = {
            "status": "success",
            "repo": repo,
            "name": repo.split("/")[-1],
            "owner": repo.split("/")[0],
            "description": "A sample repository for testing",
            "language": "Python",
            "stars": 42,
            "forks": 10,
            "open_issues": 5,
            "open_prs": 3,
            "default_branch": "main",
            "topics": ["python", "api", "testing"]
        }
        
        logger.tool_response("get_repository_info", "success", 0.1)
        return mock_repo
    
    except Exception as e:
        logger.error(f"Error getting repository info: {e}", error=e)
        return {
            "status": "error",
            "error_message": f"Failed to get repository info: {str(e)}"
        }


# Tool definitions for agent use
CUSTOM_GITHUB_TOOLS = [
    get_pr_details,
    get_pr_diff,
    add_review_comment,
    get_issue_details,
    update_issue_labels,
    get_repository_info
]


if __name__ == "__main__":
    # Test the tools
    print("Testing custom GitHub tools...\n")
    
    # Test PR details
    pr = get_pr_details("RamaswamyGCP/KaggleAgentTestRepo", 1)
    print(f"PR Details: {pr['title']}")
    
    # Test issue details
    issue = get_issue_details("RamaswamyGCP/KaggleAgentTestRepo", 1)
    print(f"Issue Details: {issue['title']}")
    
    # Test label update
    result = update_issue_labels("RamaswamyGCP/KaggleAgentTestRepo", 1, ["bug", "urgent"])
    print(f"Label Update: {result['message']}")
    
    print("\n✅ All tools tested successfully!")

