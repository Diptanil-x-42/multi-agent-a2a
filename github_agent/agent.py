from dotenv import load_dotenv
import requests
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

load_dotenv()


def get_repo_info(owner: str, repo: str) -> dict:
    """Get information about a GitHub repository.

    Args:
        owner: The owner (user or organization) of the repository.
        repo: The name of the repository.

    Returns:
        A dictionary with repository information or an error message.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github+json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 404:
            return {"status": "error", "error_message": f"Repository '{owner}/{repo}' not found."}

        data = response.json()
        return {
            "status": "success",
            "repo": {
                "full_name": data["full_name"],
                "description": data.get("description", "No description"),
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "open_issues": data["open_issues_count"],
                "language": data.get("language", "Not specified"),
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "html_url": data["html_url"],
            },
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_open_issues(owner: str, repo: str, count: int = 5) -> dict:
    """Get the most recent open issues for a GitHub repository.

    Args:
        owner: The owner (user or organization) of the repository.
        repo: The name of the repository.
        count: Number of issues to retrieve (default 5, max 10).

    Returns:
        A dictionary with a list of open issues or an error message.
    """
    count = min(count, 10)
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {"Accept": "application/vnd.github+json"}
    params = {"state": "open", "per_page": count, "sort": "created", "direction": "desc"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 404:
            return {"status": "error", "error_message": f"Repository '{owner}/{repo}' not found."}

        data = response.json()
        issues = []
        for item in data:
            if "pull_request" not in item:
                issues.append({
                    "number": item["number"],
                    "title": item["title"],
                    "state": item["state"],
                    "created_at": item["created_at"],
                    "html_url": item["html_url"],
                    "labels": [label["name"] for label in item.get("labels", [])],
                })

        return {
            "status": "success",
            "repository": f"{owner}/{repo}",
            "issues": issues,
            "total_count": len(issues),
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


github_agent = Agent(
    model="gemini-2.5-flash",
    name="github_insights_agent",
    description="An agent that provides insights about GitHub repositories including stats, open issues, and project health.",
    instruction="""You are a GitHub repository analyst. When a user asks about a
    GitHub repository, use the available tools to fetch real data.
    Use get_repo_info for general repository statistics like stars, forks, and language.
    Use get_open_issues to list recent open issues.
    Present the information in a clear, structured format.
    If a repository is not found, let the user know politely.""",
    tools=[get_repo_info, get_open_issues],
)

# Define explicit streaming capabilities
capabilities = AgentCapabilities(streaming=True)

# Create a custom Agent Card with streaming enabled
custom_card = AgentCard(
    name="github_agent",
    description="An agent that provides GitHub repository insights including repo details and open issues.",
    version="1.0.0",
    url="http://localhost:8002/",
    capabilities=capabilities,
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    skills=[
        AgentSkill(
            id="get_repo_info",
            name="Repository Info",
            description="Get details about a GitHub repository including stars, forks, and description.",
            tags=["github", "repository", "info"],
            examples=["Tell me about the google/adk-python repo."],
        ),
        AgentSkill(
            id="get_open_issues",
            name="Open Issues",
            description="List open issues for a GitHub repository.",
            tags=["github", "issues", "bugs"],
            examples=["What are the open issues in google/adk-python?"],
        ),
    ],
    supportsAuthenticatedExtendedCard=False,
)


a2a_app = to_a2a(github_agent, port=8002, agent_card=custom_card)

