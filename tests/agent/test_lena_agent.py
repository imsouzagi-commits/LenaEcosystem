# tests/agent/test_lena_agent.py

import pytest
from openjarvis.agent.lena_agent import LenaAgent
# tests/agent/test_lena_agent.py

from unittest.mock import patch


def test_open_app_mocked(agent):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = None

        result = agent.handle_local_command("abre safari")

        assert mock_run.called
        assert "Abrindo" in result["choices"][0]["message"]["content"]


class DummyEngine:
    def generate(self, messages, model=None):
        return {"content": "ok"}

    async def stream(self, messages, model=None):
        yield "ok"


@pytest.fixture
def agent():
    return LenaAgent(engine=DummyEngine(), model="test")


def test_open_app_basic(agent):
    result = agent.handle_local_command("abre safari")
    assert "Abrindo" in result["choices"][0]["message"]["content"]


def test_unknown_command(agent):
    result = agent.handle_local_command("faz alguma coisa aleatoria")
    assert "Não entendi" in result["choices"][0]["message"]["content"]


def test_multi_command(agent):
    result = agent.handle_local_command("abre safari e abre notes")
    content = result["choices"][0]["message"]["content"]
    assert "|" in content


def test_route_local(agent):
    route = agent.route_query("abre spotify")
    assert route == "local"


def test_cache(agent):
    msg = [{"role": "user", "content": "oi"}]
    r1 = agent.run(msg)
    r2 = agent.run(msg)
    assert r1 == r2


def test_run_basic(agent):
    msg = [{"role": "user", "content": "oi"}]
    result = agent.run(msg)
    assert "choices" in result

def test_close_app_mocked(agent):
    with patch("subprocess.run") as mock_run:
        result = agent.handle_local_command("fecha safari")

        assert mock_run.called
        assert "Fechando" in result["choices"][0]["message"]["content"]

def test_wifi_on(agent):
    with patch("subprocess.run") as mock_run:
        result = agent.handle_local_command("liga wifi")

        assert mock_run.called
        assert "Wi-Fi" in result["choices"][0]["message"]["content"]        

def test_fuzzy_match_typo(agent):
    result = agent.handle_local_command("abre spotfy")
    assert "Spotify" in result["choices"][0]["message"]["content"]

def test_app_not_found(agent):
    result = agent.handle_local_command("abre appinexistente123")
    assert "não encontrado" in result["choices"][0]["message"]["content"].lower()

def test_multi_partial_failure(agent):
    result = agent.handle_local_command("abre safari e abre appinexistente")
    content = result["choices"][0]["message"]["content"]
    assert "|" in content
    assert "Abrindo" in content

def test_empty_command(agent):
    result = agent.handle_local_command("")
    assert "não reconhecido" in result["choices"][0]["message"]["content"].lower()

def test_detect_intent_open(agent):
    assert agent.detect_intent("abre spotify") == "open"

def test_detect_intent_volume_up(agent):
    assert agent.detect_intent("aumenta volume") == "up"

def test_detect_intent_unknown(agent):
    assert agent.detect_intent("blablabla") == "unknown"

def test_normalize_query(agent):
    q = agent.normalize_query("Lena, abre o spotify por favor")
    assert q == "abre spotify"

def test_route_search(agent):
    route = agent.route_query("qual o tempo hoje")
    assert route == "search"

def test_route_llm(agent):
    route = agent.route_query("me conta uma piada")
    assert route == "llm"        