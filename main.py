#!/usr/bin/env python3
"""
GitHub Enterprise AI Agents - Main CLI

This is the command-line interface for the GitHub Enterprise AI Agents system.
It provides access to all agent capabilities through simple commands.

Usage:
    python main.py review-pr <repo> <pr_number>
    python main.py triage-issue <repo> <issue_number>
    python main.py update-docs <content>
    python main.py interactive

Examples:
    python main.py review-pr RamaswamyGCP/KaggleAgentTestRepo 1
    python main.py triage-issue RamaswamyGCP/KaggleAgentTestRepo 1
    python main.py interactive
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from observability.logger import get_logger
from agents.coordinator import get_coordinator_runner
from agents.pr_review import review_pull_request
from agents.issue_triage import triage_issue, triage_multiple_issues
from agents.docs_agent import improve_documentation

settings = get_settings()
logger = get_logger("MainCLI")


def print_banner():
    """Print the application banner."""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     GitHub Enterprise AI Agents                            ║
║     Multi-Agent System for Code Review, Issue Triage,     ║
║     and Documentation                                      ║
║                                                            ║
║     Powered by Google Agent Development Kit (ADK)          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


async def cmd_review_pr(args):
    """
    Review a pull request.
    
    Args:
        args: Parsed arguments containing repo and pr_number
    """
    print(f"\n🔍 Reviewing PR #{args.pr_number} in {args.repo}...")
    print("=" * 60)
    
    result = await review_pull_request(
        repo=args.repo,
        pr_number=args.pr_number,
        post_comments=args.post_comments
    )
    
    if result["status"] == "success":
        print("\n✅ PR Review Complete!")
        print("\n" + "=" * 60)
        print("REVIEW:")
        print("=" * 60)
        review_text = result.get("review", "No review generated")
        print(review_text)
        print("=" * 60)
        
        if result.get("comments_posted"):
            print("\n📝 Comments posted to GitHub")
    else:
        print(f"\n❌ Review failed: {result['error_message']}")
        sys.exit(1)


async def cmd_triage_issue(args):
    """
    Triage one or more GitHub issues.
    
    Args:
        args: Parsed arguments containing repo and issue_numbers
    """
    issue_numbers = args.issue_numbers
    
    if len(issue_numbers) == 1:
        print(f"\n🏷️  Triaging issue #{issue_numbers[0]} in {args.repo}...")
        print("=" * 60)
        
        result = await triage_issue(
            repo=args.repo,
            issue_number=issue_numbers[0],
            apply_labels=args.apply_labels
        )
        
        if result["status"] == "success":
            print("\n✅ Issue Triage Complete!")
            print("\n" + "=" * 60)
            print("TRIAGE RESULT:")
            print("=" * 60)
            triage_result = result.get("triage_result", "No result generated")
            print(triage_result)
            print("=" * 60)
            
            if result.get("labels_applied"):
                print("\n🏷️  Labels applied to GitHub issue")
        else:
            print(f"\n❌ Triage failed: {result['error_message']}")
            sys.exit(1)
    else:
        print(f"\n🏷️  Triaging {len(issue_numbers)} issues in parallel...")
        print("=" * 60)
        
        results = await triage_multiple_issues(
            repo=args.repo,
            issue_numbers=issue_numbers,
            apply_labels=args.apply_labels
        )
        
        successful = sum(1 for r in results if r.get("status") == "success")
        
        print(f"\n✅ Triage Complete: {successful}/{len(results)} successful")
        
        for i, result in enumerate(results, 1):
            print(f"\nIssue #{result.get('issue_number', issue_numbers[i-1])}:")
            if result.get("status") == "success":
                print("  Status: ✅ Success")
                triage_result = result.get("triage_result", "")
                # Show first 100 chars
                preview = triage_result[:100] + "..." if len(triage_result) > 100 else triage_result
                print(f"  Result: {preview}")
            else:
                print(f"  Status: ❌ Failed - {result.get('error_message', 'Unknown error')}")


async def cmd_update_docs(args):
    """
    Update or improve documentation.
    
    Args:
        args: Parsed arguments containing content
    """
    print("\n📝 Improving documentation...")
    print("=" * 60)
    
    # Check if content is a file path
    content_path = Path(args.content)
    if content_path.exists() and content_path.is_file():
        print(f"Reading from file: {content_path}")
        content = content_path.read_text()
    else:
        content = args.content
    
    result = await improve_documentation(
        content=content,
        context=args.context
    )
    
    if result["status"] == "success":
        print("\n✅ Documentation Improved!")
        print("\n" + "=" * 60)
        print("IMPROVED DOCUMENTATION:")
        print("=" * 60)
        improved_docs = result.get("improved_documentation", "No documentation generated")
        print(improved_docs)
        print("=" * 60)
        
        # Optionally save to file
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(improved_docs)
            print(f"\n💾 Saved to: {output_path}")
    else:
        print(f"\n❌ Documentation improvement failed: {result['error_message']}")
        sys.exit(1)


async def cmd_interactive(args):
    """
    Run interactive mode.
    
    Args:
        args: Parsed arguments (not used for interactive mode)
    """
    coordinator = get_coordinator_runner()
    await coordinator.run_interactive()


def main():
    """Main entry point for the CLI."""
    # Validate configuration first
    if not settings.validate():
        print("\n❌ Configuration error. Please check your .env file.")
        print("   Copy .env.example to .env and add your GOOGLE_API_KEY")
        sys.exit(1)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="GitHub Enterprise AI Agents - Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Review a pull request:
    python main.py review-pr RamaswamyGCP/KaggleAgentTestRepo 1
  
  Triage an issue:
    python main.py triage-issue RamaswamyGCP/KaggleAgentTestRepo 1
  
  Triage multiple issues:
    python main.py triage-issue RamaswamyGCP/KaggleAgentTestRepo 1 2 3
  
  Improve documentation:
    python main.py update-docs README.md
  
  Interactive mode:
    python main.py interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Review PR command
    review_parser = subparsers.add_parser(
        "review-pr",
        help="Review a pull request"
    )
    review_parser.add_argument("repo", help="Repository (owner/repo)")
    review_parser.add_argument("pr_number", type=int, help="PR number")
    review_parser.add_argument(
        "--post-comments",
        action="store_true",
        help="Post comments to GitHub"
    )
    
    # Triage issue command
    triage_parser = subparsers.add_parser(
        "triage-issue",
        help="Triage one or more GitHub issues"
    )
    triage_parser.add_argument("repo", help="Repository (owner/repo)")
    triage_parser.add_argument(
        "issue_numbers",
        type=int,
        nargs="+",
        help="Issue number(s)"
    )
    triage_parser.add_argument(
        "--apply-labels",
        action="store_true",
        help="Apply labels to GitHub issues"
    )
    
    # Update docs command
    docs_parser = subparsers.add_parser(
        "update-docs",
        help="Improve documentation"
    )
    docs_parser.add_argument(
        "content",
        help="Documentation content or file path"
    )
    docs_parser.add_argument(
        "--context",
        default="",
        help="Additional context about what to document"
    )
    docs_parser.add_argument(
        "--output",
        help="Output file path"
    )
    
    # Interactive mode
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Run in interactive mode"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show banner
    print_banner()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Route to appropriate command handler
    try:
        if args.command == "review-pr":
            asyncio.run(cmd_review_pr(args))
        elif args.command == "triage-issue":
            asyncio.run(cmd_triage_issue(args))
        elif args.command == "update-docs":
            asyncio.run(cmd_update_docs(args))
        elif args.command == "interactive":
            asyncio.run(cmd_interactive(args))
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Command failed: {e}", error=e, command=args.command)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

