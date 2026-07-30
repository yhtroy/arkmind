"""CLI entry point for Asset extraction.

Usage::

    arkmind-asset <input.json> <output.json> [--provider {fake,real}] [--model NAME]

Reads a Knowledge JSON array (as produced by the Dataset Runner), runs the
AssetExtractor and writes the resulting Assets as a JSON array. No business
logic lives here.

The provider defaults to ``fake`` (offline, deterministic) so CI and tests never
touch the network or consume API credits. ``--provider real`` selects the
OpenAI-compatible client, configured via ``ARKMIND_LLM_API_KEY`` /
``ARKMIND_LLM_BASE_URL`` and the ``--model`` argument.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from arkmind.asset.extractor import AssetExtractor
from arkmind.knowledge.models import Knowledge
from arkmind.runtime import (
    FakeLLMClient,
    LLMClient,
    ModelConfig,
    OpenAICompatibleClient,
    PromptLoader,
)


def _build_llm(provider: str, model: str | None) -> LLMClient:
    if provider == "real":
        if not model:
            raise SystemExit("--model is required when --provider real")
        return OpenAICompatibleClient.from_env(ModelConfig(model=model))
    return FakeLLMClient()


def main() -> None:
    parser = argparse.ArgumentParser(prog="arkmind-asset")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--provider", choices=["fake", "real"], default="fake")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    knowledge = [Knowledge.model_validate(item) for item in raw]

    llm = _build_llm(args.provider, args.model)
    assets = AssetExtractor(loader=PromptLoader(), llm=llm).extract(knowledge)

    Path(args.output).write_text(
        json.dumps(
            [asset.model_dump(mode="json") for asset in assets],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
