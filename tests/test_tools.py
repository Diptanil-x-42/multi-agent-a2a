import pytest
from weather_agent.agent import get_weather
from github_agent.agent import get_repo_info, get_open_issues


def test_get_weather_valid_city():
    result = get_weather("London")
    assert result["status"] == "success"
    assert "report" in result
    assert "temperature_celsius" in result["report"]
    assert result["report"]["city"] == "London"


def test_get_weather_invalid_city():
    result = get_weather("XyzNonexistentCity12345")
    assert result["status"] == "error"
    assert "error_message" in result


def test_get_repo_info_valid():
    result = get_repo_info("google", "adk-python")
    assert result["status"] == "success"
    assert "repo" in result
    assert result["repo"]["full_name"] == "google/adk-python"
    assert "stars" in result["repo"]


def test_get_repo_info_invalid():
    result = get_repo_info("nonexistent-user-xyz", "nonexistent-repo-xyz")
    assert result["status"] == "error"


def test_get_open_issues_valid():
    result = get_open_issues("google", "adk-python", count=3)
    assert result["status"] == "success"
    assert "issues" in result
    assert result["total_count"] <= 3


def test_get_open_issues_respects_max():
    result = get_open_issues("google", "adk-python", count=20)
    assert result["status"] == "success"
    assert result["total_count"] <= 10    