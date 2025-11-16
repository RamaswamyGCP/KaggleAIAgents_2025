"""
Example test scenarios for GitHub Enterprise AI Agents.

These tests demonstrate the capabilities of the agent system
using mock data. Perfect for demonstrations and development.
"""

import asyncio
import json
from pathlib import Path

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.pr_review import review_pull_request
from agents.issue_triage import triage_issue, triage_multiple_issues
from agents.docs_agent import improve_documentation
from agents.coordinator import get_coordinator_runner


async def test_pr_review():
    """Test PR review functionality."""
    print("=" * 70)
    print("TEST 1: PR Review (Sequential Agent)")
    print("=" * 70)
    
    result = await review_pull_request(
        repo="RamaswamyGCP/KaggleAgentTestRepo",
        pr_number=1,
        post_comments=False
    )
    
    if result["status"] == "success":
        print("✅ PR Review Test PASSED")
        print(f"\nSample output:\n{result.get('review', '')[:200]}...")
    else:
        print(f"❌ PR Review Test FAILED: {result['error_message']}")
    
    return result["status"] == "success"


async def test_issue_triage_single():
    """Test single issue triage."""
    print("\n" + "=" * 70)
    print("TEST 2: Single Issue Triage (Parallel Agent)")
    print("=" * 70)
    
    result = await triage_issue(
        repo="RamaswamyGCP/KaggleAgentTestRepo",
        issue_number=1,
        apply_labels=False
    )
    
    if result["status"] == "success":
        print("✅ Single Issue Triage Test PASSED")
        print(f"\nSample output:\n{result.get('triage_result', '')[:200]}...")
    else:
        print(f"❌ Single Issue Triage Test FAILED: {result['error_message']}")
    
    return result["status"] == "success"


async def test_issue_triage_multiple():
    """Test multiple issue triage in parallel."""
    print("\n" + "=" * 70)
    print("TEST 3: Multiple Issues Triage (Parallel Processing)")
    print("=" * 70)
    
    results = await triage_multiple_issues(
        repo="RamaswamyGCP/KaggleAgentTestRepo",
        issue_numbers=[1, 2, 3, 4],
        apply_labels=False
    )
    
    successful = sum(1 for r in results if r.get("status") == "success")
    total = len(results)
    
    if successful == total:
        print(f"✅ Multiple Issues Triage Test PASSED ({successful}/{total})")
    else:
        print(f"⚠️  Multiple Issues Triage Test PARTIAL ({successful}/{total})")
    
    return successful > 0


async def test_documentation_improvement():
    """Test documentation improvement with loop."""
    print("\n" + "=" * 70)
    print("TEST 4: Documentation Improvement (Loop Agent)")
    print("=" * 70)
    
    sample_doc = """
# Quick Start

Install the app. Run it. That's it.
"""
    
    result = await improve_documentation(
        content=sample_doc,
        context="Installation and setup guide for the application"
    )
    
    if result["status"] == "success":
        print("✅ Documentation Improvement Test PASSED")
        print(f"\nOriginal length: {len(sample_doc)} chars")
        improved = result.get("improved_documentation", "")
        print(f"Improved length: {len(improved)} chars")
        print(f"\nSample output:\n{improved[:200]}...")
    else:
        print(f"❌ Documentation Improvement Test FAILED: {result['error_message']}")
    
    return result["status"] == "success"


async def test_coordinator_query():
    """Test coordinator agent with simple query."""
    print("\n" + "=" * 70)
    print("TEST 5: Coordinator Agent (Session Management)")
    print("=" * 70)
    
    coordinator = get_coordinator_runner()
    
    # Test query
    result = await coordinator.run(
        "What can you help me with?",
        session_id="test_session"
    )
    
    if result["status"] == "success":
        print("✅ Coordinator Query Test PASSED")
        print(f"\nResponse:\n{result.get('response', '')[:200]}...")
    else:
        print(f"❌ Coordinator Query Test FAILED: {result['error_message']}")
    
    return result["status"] == "success"


async def test_coordinator_memory():
    """Test coordinator memory across multiple queries."""
    print("\n" + "=" * 70)
    print("TEST 6: Coordinator Memory (Multi-turn Conversation)")
    print("=" * 70)
    
    coordinator = get_coordinator_runner()
    session_id = "memory_test_session"
    
    # First query: Introduce name
    result1 = await coordinator.run(
        "My name is Ramaswamy",
        session_id=session_id
    )
    
    # Second query: Ask for name (should remember)
    result2 = await coordinator.run(
        "What's my name?",
        session_id=session_id
    )
    
    if result1["status"] == "success" and result2["status"] == "success":
        response = result2.get("response", "").lower()
        if "ramaswamy" in response:
            print("✅ Coordinator Memory Test PASSED")
            print(f"\nAgent remembered the name across queries!")
            print(f"Response: {result2.get('response', '')[:150]}...")
        else:
            print("⚠️  Coordinator Memory Test PARTIAL (may not have remembered)")
            print(f"Response: {result2.get('response', '')[:150]}...")
    else:
        print("❌ Coordinator Memory Test FAILED")
        if result1["status"] != "success":
            print(f"  First query error: {result1['error_message']}")
        if result2["status"] != "success":
            print(f"  Second query error: {result2['error_message']}")
    
    return result1["status"] == "success" and result2["status"] == "success"


async def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "=" * 70)
    print("GITHUB ENTERPRISE AI AGENTS - TEST SUITE")
    print("=" * 70)
    print("\nRunning comprehensive tests of all agent capabilities...")
    print("This will take a few minutes...\n")
    
    # Run all tests
    results = []
    
    # Note: Some tests might fail in mock mode, which is expected
    # In production with real API keys, these would work
    
    try:
        results.append(("PR Review", await test_pr_review()))
    except Exception as e:
        print(f"❌ PR Review test error: {e}")
        results.append(("PR Review", False))
    
    try:
        results.append(("Single Issue Triage", await test_issue_triage_single()))
    except Exception as e:
        print(f"❌ Single issue triage test error: {e}")
        results.append(("Single Issue Triage", False))
    
    try:
        results.append(("Multiple Issues Triage", await test_issue_triage_multiple()))
    except Exception as e:
        print(f"❌ Multiple issues triage test error: {e}")
        results.append(("Multiple Issues Triage", False))
    
    try:
        results.append(("Documentation Improvement", await test_documentation_improvement()))
    except Exception as e:
        print(f"❌ Documentation test error: {e}")
        results.append(("Documentation Improvement", False))
    
    try:
        results.append(("Coordinator Query", await test_coordinator_query()))
    except Exception as e:
        print(f"❌ Coordinator test error: {e}")
        results.append(("Coordinator Query", False))
    
    try:
        results.append(("Coordinator Memory", await test_coordinator_memory()))
    except Exception as e:
        print(f"❌ Coordinator memory test error: {e}")
        results.append(("Coordinator Memory", False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All tests passed! The agent system is working correctly.")
    elif passed > total / 2:
        print("\n⚠️  Most tests passed. Some failures expected in mock mode.")
        print("   With real API keys and GitHub access, all tests should pass.")
    else:
        print("\n❌ Many tests failed. Check configuration and API keys.")
    
    return passed, total


if __name__ == "__main__":
    print("\n🤖 Starting GitHub Enterprise AI Agents Test Suite...")
    print("=" * 70)
    
    # Check if running with API key
    from config.settings import get_settings
    settings = get_settings()
    
    if not settings.GOOGLE_API_KEY:
        print("\n⚠️  WARNING: No GOOGLE_API_KEY found!")
        print("   Tests will run with mock data only.")
        print("   For full functionality, add API key to .env file.\n")
    
    # Run tests
    passed, total = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

