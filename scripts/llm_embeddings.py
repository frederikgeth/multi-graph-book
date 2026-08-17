#!/usr/bin/env python3
"""Optional, provenance-aware neural embedding support for the LLM corpus.

The repository does not vendor a model or a heavyweight inference runtime.
This module therefore loads sentence-transformers only when a caller asks for
neural retrieval and requires an immutable model revision.  The returned
metadata is part of every neural benchmark so results cannot be detached from
the model that produced them.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class EmbeddingConfigurationError(ValueError):
    """Raised when neural retrieval provenance is incomplete or unsafe."""


class EmbeddingRuntimeError(RuntimeError):
    """Raised when the optional neural runtime is not available."""


IMMUTABLE_REVISION_FORBIDDEN = {"main", "master", "latest", "default"}


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(path: Path) -> str:
    """Hash a local model directory with stable relative paths and bytes."""
    if path.is_file():
        return sha256_file(path)
    if not path.is_dir():
        raise EmbeddingConfigurationError(f"model artifact path does not exist: {path}")
    digest = hashlib.sha256()
    files = sorted(item for item in path.rglob("*") if item.is_file())
    if not files:
        raise EmbeddingConfigurationError(f"model artifact directory is empty: {path}")
    for item in files:
        relative = item.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(sha256_file(item).encode("ascii"))
    return digest.hexdigest()


def require_immutable_revision(revision: str) -> str:
    value = revision.strip()
    if not value or value.lower() in IMMUTABLE_REVISION_FORBIDDEN:
        raise EmbeddingConfigurationError(
            "neural retrieval requires an immutable model revision (commit hash or equivalent); "
            "do not use main, master, latest, or an empty revision"
        )
    return value


@dataclass(frozen=True)
class EmbeddingConfig:
    model_id: str
    revision: str
    device: str = "cpu"
    normalize_embeddings: bool = True
    artifact_sha256: str | None = None
    model_path: str | None = None
    local_files_only: bool = False

    def validated(self) -> "EmbeddingConfig":
        if not self.model_id.strip():
            raise EmbeddingConfigurationError("model_id must not be empty")
        revision = require_immutable_revision(self.revision)
        if self.artifact_sha256 is not None:
            artifact = self.artifact_sha256.lower()
            if len(artifact) != 64 or any(char not in "0123456789abcdef" for char in artifact):
                raise EmbeddingConfigurationError("artifact_sha256 must be a 64-character hexadecimal digest")
        return EmbeddingConfig(
            model_id=self.model_id.strip(),
            revision=revision,
            device=self.device,
            normalize_embeddings=self.normalize_embeddings,
            artifact_sha256=self.artifact_sha256.lower() if self.artifact_sha256 else None,
            model_path=self.model_path,
            local_files_only=self.local_files_only,
        )


class SentenceTransformerEmbeddings:
    """Thin adapter around sentence-transformers with explicit provenance."""

    provider_name = "sentence-transformers"

    def __init__(self, config: EmbeddingConfig) -> None:
        self.config = config.validated()
        try:
            package = importlib.import_module("sentence_transformers")
        except ImportError as error:
            raise EmbeddingRuntimeError(
                "sentence-transformers is not installed; install the optional neural-retrieval "
                "environment before running this benchmark"
            ) from error
        self._package = package
        model_source = self.config.model_path or self.config.model_id
        model_kwargs = {
            "device": self.config.device,
            "revision": self.config.revision,
        }
        if self.config.local_files_only:
            model_kwargs["local_files_only"] = True
        try:
            self._model = package.SentenceTransformer(model_source, **model_kwargs)
        except TypeError:
            # Older sentence-transformers versions do not expose
            # local_files_only.  Never silently drop the pinned revision.
            if "local_files_only" not in model_kwargs:
                raise
            model_kwargs.pop("local_files_only")
            self._model = package.SentenceTransformer(model_source, **model_kwargs)
        except Exception as error:
            raise EmbeddingRuntimeError(f"could not load neural model {model_source!r}: {error}") from error

        dimension_getter = getattr(self._model, "get_embedding_dimension", None)
        if dimension_getter is None:
            dimension_getter = self._model.get_sentence_embedding_dimension
        self.dimension = int(dimension_getter())
        if self.dimension < 1:
            raise EmbeddingRuntimeError("neural model returned an invalid embedding dimension")
        self.artifact_sha256, self.artifact_hash_source = self._artifact_provenance()

    def _artifact_provenance(self) -> tuple[str | None, str]:
        if self.config.artifact_sha256:
            return self.config.artifact_sha256, "declared"
        if self.config.model_path:
            path = Path(self.config.model_path).expanduser().resolve()
            return sha256_tree(path), "local_model_tree"
        return None, "not_available_for_remote_cache"

    def encode(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            vectors = self._model.encode(
                list(texts),
                normalize_embeddings=self.config.normalize_embeddings,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        except Exception as error:
            raise EmbeddingRuntimeError(f"neural encoding failed: {error}") from error
        rows = vectors.tolist() if hasattr(vectors, "tolist") else vectors
        if len(rows) != len(texts):
            raise EmbeddingRuntimeError("neural model returned the wrong number of embeddings")
        return [[float(value) for value in row] for row in rows]

    def provenance(self) -> dict:
        sentence_transformers_version = getattr(self._package, "__version__", "unknown")
        return {
            "provider": self.provider_name,
            "model_id": self.config.model_id,
            "model_revision": self.config.revision,
            "model_path": Path(self.config.model_path).name if self.config.model_path else None,
            "artifact_sha256": self.artifact_sha256,
            "artifact_hash_source": self.artifact_hash_source,
            "artifact_hash_complete": self.artifact_sha256 is not None,
            "embedding_dimension": self.dimension,
            "normalize_embeddings": self.config.normalize_embeddings,
            "device": self.config.device,
            "local_files_only": self.config.local_files_only,
            "sentence_transformers_version": sentence_transformers_version,
            "torch_version": package_version("torch"),
            "transformers_version": package_version("transformers"),
            "numpy_version": package_version("numpy"),
            "python_version": platform.python_version(),
            "implementation": f"{sys.implementation.name}-{platform.python_implementation()}",
        }


class CrossEncoderReranker:
    """Optional cross-encoder second-stage ranker with the same provenance rules."""

    provider_name = "sentence-transformers-cross-encoder"

    def __init__(self, config: EmbeddingConfig, max_length: int = 512) -> None:
        self.config = config.validated()
        if max_length < 1:
            raise EmbeddingConfigurationError("cross-encoder max_length must be positive")
        self.max_length = max_length
        try:
            package = importlib.import_module("sentence_transformers")
        except ImportError as error:
            raise EmbeddingRuntimeError(
                "sentence-transformers is not installed; install the optional neural-retrieval "
                "environment before running this benchmark"
            ) from error
        self._package = package
        model_source = self.config.model_path or self.config.model_id
        model_kwargs = {
            "device": self.config.device,
            "revision": self.config.revision,
            "max_length": self.max_length,
        }
        if self.config.local_files_only:
            model_kwargs["local_files_only"] = True
        try:
            self._model = package.CrossEncoder(model_source, **model_kwargs)
        except TypeError:
            if "local_files_only" not in model_kwargs:
                raise
            model_kwargs.pop("local_files_only")
            self._model = package.CrossEncoder(model_source, **model_kwargs)
        except Exception as error:
            raise EmbeddingRuntimeError(f"could not load cross-encoder {model_source!r}: {error}") from error
        self.artifact_sha256, self.artifact_hash_source = self._artifact_provenance()

    def _artifact_provenance(self) -> tuple[str | None, str]:
        if self.config.artifact_sha256:
            return self.config.artifact_sha256, "declared"
        if self.config.model_path:
            path = Path(self.config.model_path).expanduser().resolve()
            return sha256_tree(path), "local_model_tree"
        return None, "not_available_for_remote_cache"

    def predict(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        try:
            values = self._model.predict(list(pairs), show_progress_bar=False)
        except Exception as error:
            raise EmbeddingRuntimeError(f"cross-encoder reranking failed: {error}") from error
        rows = values.tolist() if hasattr(values, "tolist") else values
        if len(rows) != len(pairs):
            raise EmbeddingRuntimeError("cross-encoder returned the wrong number of scores")
        return [float(value[0] if isinstance(value, (list, tuple)) else value) for value in rows]

    def provenance(self) -> dict:
        sentence_transformers_version = getattr(self._package, "__version__", "unknown")
        return {
            "provider": self.provider_name,
            "model_id": self.config.model_id,
            "model_revision": self.config.revision,
            "model_path": Path(self.config.model_path).name if self.config.model_path else None,
            "artifact_sha256": self.artifact_sha256,
            "artifact_hash_source": self.artifact_hash_source,
            "artifact_hash_complete": self.artifact_sha256 is not None,
            "device": self.config.device,
            "max_length": self.max_length,
            "local_files_only": self.config.local_files_only,
            "sentence_transformers_version": sentence_transformers_version,
            "torch_version": package_version("torch"),
            "transformers_version": package_version("transformers"),
            "numpy_version": package_version("numpy"),
            "python_version": platform.python_version(),
            "implementation": f"{sys.implementation.name}-{platform.python_implementation()}",
        }
