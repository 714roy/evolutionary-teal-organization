"""Bootstrap Bundle 单元测试 — 独立运行，无外部依赖"""
import json
import os
import shutil
import sys
from pathlib import Path

# Ensure package is importable regardless of test run location
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

# Import modules under test (relative to bootstrap root)
from bootstrap.seed_profiles import init as seed_profiles_init
from bootstrap.seed_sample_skills import SEED as SKILLS_SEED
from bootstrap.config_template import make_config


# ── Fixture: temporary directory for isolated test runs ─────────────

@pytest.fixture()
def tmp_dir(tmp_path):
    return str(tmp_path)


# ── seed_profiles tests ────────────────────────────────────────────

class TestSeedProfiles:
    def test_init_creates_file(self, tmp_dir):
        path = os.path.join(tmp_dir, "profiles.json")
        r = seed_profiles_init(path, force=False)
        assert r["status"] == "ok"
        assert r["count"] == 3
        assert os.path.exists(path)

    def test_init_skips_if_exists(self, tmp_dir):
        path = os.path.join(tmp_dir, "profiles.json")
        Path(path).write_text("[]", "utf-8")
        r = seed_profiles_init(path, force=False)
        assert r["status"] == "skipped"

    def test_force_overwrites(self, tmp_dir):
        path = os.path.join(tmp_dir, "profiles.json")
        Path(path).write_text("[]", "utf-8")
        r = seed_profiles_init(path, force=True)
        assert r["status"] == "ok"
        assert r["count"] == 3

    def test_seed_data_structure(self, tmp_dir):
        path = os.path.join(tmp_dir, "profiles.json")
        seed_profiles_init(path, force=False)
        data = json.loads(Path(path).read_text("utf-8"))
        names = [p["name"] for p in data]
        assert set(names) == {"researcher", "coder", "auditor"}
        for p in data:
            assert "weights" in p
            assert "maxSubtasks" in p


# ── seed_sample_skills tests ───────────────────────────────────────

class TestSeedSkills:
    def test_seed_count(self):
        assert len(SKILLS_SEED) == 5

    def test_required_fields_present(self):
        for s in SKILLS_SEED:
            assert all(k in s for k in ("skill_name", "context", "reward", "source"))

    def test_rewards_non_negative(self):
        for s in SKILLS_SEED:
            assert s["reward"] >= 0



# ── config_template tests ─────────────────────────────────────────

class TestConfigTemplate:
    @pytest.mark.parametrize("provider", ["deepseek", "ollama", "skip"])
    def test_provider_value(self, provider):
        cfg = json.loads(make_config(provider))
        assert cfg["router"]["provider"] == provider

    def test_always_has_two_models(self):
        for provider in ("deepseek", "ollama", "skip"):
            cfg = json.loads(make_config(provider))
            assert len(cfg["router"]["models"]) == 2
            assert set(cfg["router"]["models"].keys()) == {"deepseek", "ollama"}

    def test_fallback_is_keyword(self):
        for provider in ("deepseek", "ollama", "skip"):
            cfg = json.loads(make_config(provider))
            assert cfg["router"]["fallback"] == "keyword"

    @pytest.mark.parametrize("provider", ["deepseek", "ollama"])
    def test_model_urls_valid(self, provider):
        cfg = json.loads(make_config(provider))
        for model_name in ("deepseek", "ollama"):
            assert "url" in cfg["router"]["models"][model_name]
            assert "model" in cfg["router"]["models"][model_name]
