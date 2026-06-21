from ollama_handoff.config import (
    DEFAULT_MODEL,
    DEFAULT_NUM_CTX,
    DEFAULT_URL,
    Config,
)


def test_defaults_when_env_empty():
    cfg = Config.from_env(env={})
    assert cfg.url == DEFAULT_URL
    assert cfg.default_model == DEFAULT_MODEL
    assert cfg.num_ctx == DEFAULT_NUM_CTX


def test_env_overrides_are_applied_and_typed():
    cfg = Config.from_env(
        env={
            "OLLAMA_URL": "http://gpu.local:11434/",
            "OLLAMA_DEFAULT_MODEL": "llama3.1:8b",
            "OLLAMA_NUM_CTX": "8192",
            "OLLAMA_TIMEOUT_S": "120",
        }
    )
    assert cfg.url == "http://gpu.local:11434"  # trailing slash stripped
    assert cfg.default_model == "llama3.1:8b"
    assert cfg.num_ctx == 8192 and isinstance(cfg.num_ctx, int)
    assert cfg.timeout_s == 120.0 and isinstance(cfg.timeout_s, float)


def test_as_dict_is_json_shaped():
    d = Config(url="http://x:1").as_dict()
    assert d["ollama_url"] == "http://x:1"
    assert set(d) == {"ollama_url", "default_model", "num_ctx", "keep_alive", "timeout_s"}
