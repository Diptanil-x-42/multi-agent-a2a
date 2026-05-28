import httpx
from fastapi import FastAPI

health_app = FastAPI()

# URLs of your remote A2A agents
AGENT_URLS = [
    "http://localhost:8001/.well-known/agent-card.json",
    "http://localhost:8002/.well-known/agent-card.json",
]


@health_app.get("/health")
async def health_check():
    """Check the health of all registered A2A agents."""
    results = {}

    async with httpx.AsyncClient(timeout=5.0) as client:
        for url in AGENT_URLS:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    card = response.json()
                    results[card["name"]] = {
                        "status": "healthy",
                        "description": card.get("description", ""),
                        "streaming": card.get("capabilities", {}).get("streaming", False),
                    }
                else:
                    results[url] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
            except Exception as e:
                results[url] = {"status": "unreachable", "error": str(e)}

    all_healthy = all(agent["status"] == "healthy" for agent in results.values())
    return {
        "overall_status": "healthy" if all_healthy else "degraded",
        "agents": results,
    }