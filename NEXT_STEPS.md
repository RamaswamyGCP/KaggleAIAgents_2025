# 🎯 Next Steps: Get Your Agents Running!

This guide will take you from "code on GitHub" to "working demo" in about 30 minutes.

---

## ✅ **Current Status**

- ✅ Agent system code complete (KaggleAIAgents_2025)
- ✅ Test target code complete (KaggleAgentTestRepo)
- ✅ Both repositories on GitHub
- ✅ .env file created (needs your API keys)
- ⏳ **Next: Set up, test, and verify everything works!**

---

## 📝 **Phase 1: Environment Setup (5 minutes)**

### Step 1: Add Your Google API Key

You mentioned you have a Google Gemini API key. Let's add it:

```bash
cd /Users/ramaswamy/Documents/KaggleStudy/github_enterprise_agents

# Open .env file and add your API key
open .env
```

**Edit the .env file to include:**
```bash
# Google Gemini API Key (from Google AI Studio)
GOOGLE_API_KEY=your_actual_api_key_here

# GitHub Personal Access Token (optional for now - we'll use mock data first)
GITHUB_TOKEN=

# For local testing, keep this as 0
GOOGLE_GENAI_USE_VERTEXAI=0

# Test repository details
GITHUB_TEST_REPO_OWNER=RamaswamyGCP
GITHUB_TEST_REPO_NAME=KaggleAgentTestRepo
```

**Where to get your Google API Key:**
- Go to: https://aistudio.google.com/app/apikey
- Sign in with your Google account
- Click "Create API Key"
- Copy and paste into .env file

### Step 2: Create Virtual Environment

```bash
cd /Users/ramaswamy/Documents/KaggleStudy/github_enterprise_agents

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Your prompt should now show (venv)
```

### Step 3: Install Dependencies

```bash
# Make sure venv is activated (you should see "(venv)" in your prompt)
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:**
```
Installing collected packages: google-genai, google-adk, fastapi, uvicorn, ...
Successfully installed...
```

**If you get errors**, you might need:
```bash
# Install Node.js for MCP servers (if not already installed)
brew install node

# Or download from: https://nodejs.org/
```

---

## 🧪 **Phase 2: Quick Test (5 minutes)**

### Test 1: Verify Installation

```bash
cd /Users/ramaswamy/Documents/KaggleStudy/github_enterprise_agents
source venv/bin/activate  # If not already activated

# Test if main.py works
python main.py --help
```

**Expected output:**
```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  GitHub Enterprise AI Agents CLI.

Commands:
  interactive   Starts an interactive chat session with the coordinator...
  review-pr     Reviews a pull request.
  triage-issue  Triages GitHub issues.
  update-docs   Updates documentation.
```

### Test 2: Interactive Mode (Using Mock Data)

```bash
python main.py interactive
```

**Try these commands:**
```
User > Hello! What can you help me with?
# Agent should respond with its capabilities

User > Analyze this code for security issues: 
query = f"SELECT * FROM users WHERE username = '{username}'"
# Agent should identify SQL injection

User > exit
```

---

## 📋 **Phase 3: Create Test Issues on GitHub (10 minutes)**

Now let's create real GitHub issues for your agents to triage!

### Go to your test repo:
https://github.com/RamaswamyGCP/KaggleAgentTestRepo/issues/new

### Create Issue #1: Critical Bug
```
Title: App crashes on user login with invalid credentials

Labels: (leave blank - let agent add them)

Description:
When attempting to login with incorrect username/password, the application 
crashes instead of returning a proper error message. This is impacting user 
experience and needs immediate attention.

Steps to reproduce:
1. POST to /api/login with wrong credentials
2. Server returns 500 error with full traceback

Expected: 401 Unauthorized with user-friendly message
Actual: 500 Internal Server Error with stack trace

Priority: This is affecting all users and should be fixed ASAP.
```

### Create Issue #2: Security Vulnerability
```
Title: SQL Injection vulnerability in user lookup endpoint

Labels: security (add this label manually)

Description:
The get_user_by_username function in database.py uses string concatenation 
to build SQL queries, making it vulnerable to SQL injection attacks.

File: database.py
Line: 45
Function: get_user_by_username()

Attack example:
GET /api/user/admin' OR '1'='1

This could allow attackers to dump the entire user database or delete records.

Priority: CRITICAL - This needs immediate attention!
```

### Create Issue #3: Feature Request
```
Title: Implement password hashing for user security

Labels: (leave blank)

Description:
Currently, passwords are stored in plain text in the database. This is a 
major security concern. We should implement proper password hashing using 
bcrypt or argon2.

Note: I noticed there are hash_password and verify_password functions in 
auth.py but they're not being used anywhere!

Suggested solution:
- Install bcrypt or passlib
- Hash passwords before storing
- Update authenticate_user to compare hashed passwords
- Migrate existing passwords (if any)
```

### Create Issue #4: Documentation
```
Title: API documentation is incomplete

Labels: documentation (add this label)

Description:
The README.md lacks proper API documentation. We need:

- Detailed request/response examples for each endpoint
- Authentication requirements clearly stated
- Error codes and their meanings
- Rate limiting information
- Example cURL commands

This will help developers integrate with our API more easily and reduce 
support requests.

Current state: Basic endpoint list only
Desired state: Comprehensive API reference
```

### Create Issue #5: Enhancement
```
Title: Add rate limiting to prevent API abuse

Labels: (leave blank)

Description:
The API currently has no rate limiting, as seen in config.py where 
RATE_LIMIT_ENABLED = False. This makes us vulnerable to:

- Brute force attacks on login endpoint
- API abuse and DoS attacks
- Excessive resource consumption

Suggested implementation:
- Use Flask-Limiter or similar
- Reasonable limits: 100 requests/minute per IP
- Stricter limits on auth endpoints: 5 login attempts/minute
- Return 429 Too Many Requests with Retry-After header
```

**After creating these, note the issue numbers!** (They'll be #1, #2, #3, #4, #5)

---

## 🚀 **Phase 4: Test Your Agents (10 minutes)**

Now the fun part - let's see your agents in action!

### Test A: Issue Triage Agent (Parallel Processing)

```bash
cd /Users/ramaswamy/Documents/KaggleStudy/github_enterprise_agents
source venv/bin/activate

# Triage all 5 issues at once!
python main.py triage-issue --repo-owner RamaswamyGCP --repo-name KaggleAgentTestRepo --issue-numbers 1 2 3 4 5
```

**Watch the agent:**
- Process multiple issues in parallel
- Classify each one (bug/security/feature/documentation/enhancement)
- Assign priority levels (low/medium/high/critical)
- The agent will try to update labels (you might need GitHub token for this)

**Expected output:**
```
Agent > Analyzing issue #1: "App crashes on user login with invalid credentials"
Agent > Classification: bug, Priority: high
Agent > Analyzing issue #2: "SQL Injection vulnerability..."
Agent > Classification: security, Priority: critical
...
```

### Test B: PR Review Agent (Once you create a PR)

First, let's create a quick test PR:

```bash
cd /Users/ramaswamy/Documents/KaggleStudy/KaggleAgentTestRepo

# Create a branch
git checkout -b fix/add-validation

# Make a small change (that still has issues)
echo "# TODO: Add input validation" >> app.py
git add app.py
git commit -m "Add TODO for input validation"
git push origin fix/add-validation

# Go to GitHub and create a PR from this branch
```

Then test the agent:
```bash
cd /Users/ramaswamy/Documents/KaggleStudy/github_enterprise_agents

# Replace <PR_NUMBER> with the actual PR number
python main.py review-pr --repo-owner RamaswamyGCP --repo-name KaggleAgentTestRepo --pr-number <PR_NUMBER>
```

### Test C: Documentation Agent

```bash
python main.py update-docs --repo-owner RamaswamyGCP --repo-name KaggleAgentTestRepo --file-path README.md
```

**Watch the agent:**
- Analyze current documentation
- Suggest improvements
- Iterate based on critique

---

## 🔍 **Phase 5: Test with Mock Data (If GitHub API Issues)**

If you don't have a GitHub token yet or want faster testing:

```bash
# Use the mock data we created
python main.py review-pr --repo-owner mock-owner --repo-name mock-repo --pr-number 1 --mock-data

python main.py triage-issue --repo-owner mock-owner --repo-name mock-repo --issue-numbers 101 102 --mock-data
```

The mock data is in:
- `tests/demo_data/sample_pr.json`
- `tests/demo_data/sample_issues.json`

---

## 🐛 **Troubleshooting**

### Error: "ModuleNotFoundError: No module named 'google.adk'"

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Error: "GOOGLE_API_KEY not found"

**Solution:**
- Make sure you edited `.env` file
- Add your actual API key from https://aistudio.google.com/app/apikey
- The file should have: `GOOGLE_API_KEY=your_actual_key_here`

### Error: "GitHub token not found"

**Solution for testing:**
- Use `--mock-data` flag to test without GitHub API
- OR create a GitHub Personal Access Token:
  1. Go to: https://github.com/settings/tokens
  2. Generate new token (classic)
  3. Select `repo` scope
  4. Add to `.env`: `GITHUB_TOKEN=your_token_here`

### Error: MCP server issues

**Solution:**
```bash
# Install Node.js if you haven't
brew install node

# Test if npx works
npx --version
```

---

## ✅ **Success Criteria**

You'll know everything is working when:

- ✅ `python main.py --help` shows commands
- ✅ Interactive mode responds to queries
- ✅ Issue triage agent classifies your GitHub issues
- ✅ PR review agent analyzes code changes
- ✅ No Python errors or import issues

---

## 🎯 **After Testing: Prepare for Demo**

Once everything works:

### 1. Document Your Results

Create a file with screenshots/logs:
```bash
cd /Users/ramaswamy/Documents/KaggleStudy/github_enterprise_agents
mkdir demo_results
```

Take screenshots of:
- Agent analyzing issues
- Agent detecting vulnerabilities
- GitHub issues with updated labels

### 2. Practice Your Demo Flow

```bash
# Demo Script
# 1. Show GitHub repos (both)
# 2. Show vulnerable code in KaggleAgentTestRepo
# 3. Show issues that need triaging
# 4. Run: python main.py triage-issue ...
# 5. Show results
# 6. Explain the architecture
# 7. Q&A
```

### 3. Prepare Your Presentation

Key points to highlight:
- **Problem**: Manual code review is slow and error-prone
- **Solution**: Multi-agent AI system with specialized agents
- **Implementation**: 6 ADK concepts demonstrated
- **Results**: Detects vulnerabilities in seconds vs hours manually
- **Future**: Deploy to Google Cloud, add more agents

---

## 🎬 **Ready to Present?**

Once you complete all phases:

✅ Environment set up  
✅ Dependencies installed  
✅ Agents tested and working  
✅ GitHub issues created  
✅ Demo script prepared  
✅ Screenshots captured  

**You're ready for your capstone presentation! 🎉**

---

## 📞 **Need Help?**

Common next questions:

**Q: How do I deploy to Google Cloud?**  
A: That's Phase 6! For capstone, local demo is sufficient. Cloud deployment can be future work.

**Q: Can I customize the agents?**  
A: Yes! Edit the agent files in `/agents/` directory. Change prompts, add tools, adjust workflows.

**Q: What if I find bugs?**  
A: Fix them! That shows debugging skills. Document what broke and how you fixed it.

**Q: Should I add more features?**  
A: For capstone, focus on getting core features working smoothly. Polish beats features.

---

## 🚀 **Let's Start!**

Your immediate action items:

1. **Right now**: Add your Google API key to `.env`
2. **In 5 minutes**: Create virtual environment and install dependencies
3. **In 10 minutes**: Test interactive mode
4. **In 20 minutes**: Create 5 GitHub issues
5. **In 30 minutes**: Run agents and capture results

**You've got this! 💪**

