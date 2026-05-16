from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent


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

    Rules:
    - If the user asks about weather, delegate to weather_remote.
    - If the user asks about a GitHub repository, delegate to github_remote.
    - If the user asks about both, delegate to both agents and combine the results.
    - Always present the final results clearly to the user.
    - If you are unsure which agent to use, ask the user for clarification.""",
    sub_agents=[weather_remote, github_remote],
)
