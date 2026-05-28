from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
import requests



weather_remote = RemoteA2aAgent(
    name="weather_remote",
    description="Remote agent that provides current weather information for any city worldwide.",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)

github_remote = RemoteA2aAgent(
    name="github_remote",
    description="Remote agent that provides insights about GitHub repositories including stats and open issues.",
    agent_card="http://localhost:8002/.well-known/agent-card.json",
)

def list_agents() -> dict:
    """Discover all available A2A agents and their capabilities.

    Returns:
        A dictionary with agent names, descriptions, and skills.
    """
    agent_card_urls = [
        "http://localhost:8001/.well-known/agent-card.json",
        "http://localhost:8002/.well-known/agent-card.json",
    ]
    agents = []

    for url in agent_card_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                card = response.json()
                agents.append({
                    "name": card["name"],
                    "description": card.get("description", ""),
                    "skills": [
                        skill.get("name", skill.get("id", "unknown"))
                        for skill in card.get("skills", [])
                    ],
                    "streaming": card.get("capabilities", {}).get("streaming", False),
                })
        except Exception as e:
            agents.append({"url": url, "status": "unreachable", "error": str(e)})

    return {"available_agents": agents, "total_count": len(agents)}

root_agent = Agent(
    model="gemini-2.5-flash",
    name="orchestrator_agent",
    description="An orchestrator agent that coordinates weather and GitHub insights agents.",
    instruction="""You are a helpful orchestrator that coordinates multiple specialized agents.
    You have access to the following remote agents:

    1. weather_remote: Use this for any weather-related questions. It can provide
       current weather data for any city worldwide.

    2. github_remote: Use this for any GitHub repository questions. It can provide
       repository statistics, open issues, and project health information.

    You also have a list_agents tool that discovers all available agents dynamically.

    Rules:
    - If the user asks about weather, delegate to weather_remote.
    - If the user asks about a GitHub repository, delegate to github_remote.
    - If the user asks what agents are available, use the list_agents tool.
    - If the user asks about both weather and GitHub, delegate to both and combine results.
    - Always present the final results clearly to the user.""",
    tools=[list_agents],
    sub_agents=[weather_remote, github_remote],
)
