"""Tests for ModelConfig (Runtime Contract v1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from arkmind.runtime import ModelConfig


def test_defaults_temperature_to_zero() -> None:
    config = ModelConfig(model="fake")
    assert config.model == "fake"
    assert config.temperature == 0.0


def test_accepts_explicit_temperature() -> None:
    assert ModelConfig(model="fake", temperature=0.7).temperature == 0.7


def test_requires_model() -> None:
    with pytest.raises(ValidationError):
        ModelConfig()


def test_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        ModelConfig(model="fake", max_tokens=10)
