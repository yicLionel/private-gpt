"""Structured retrieval trace data used for observability and debugging."""

from __future__ import annotations

from typing import Any

from llama_index.core.schema import NodeWithScore
from pydantic import BaseModel, Field

from private_gpt.components.ingest.metadata_helper import MetadataKeys, MetadataFlags


class RetrievalTraceResult(BaseModel):
    """Safe-to-log metadata for one retrieved node."""

    rank: int
    node_id: str
    citation_id: str | None = None
    score: float | None = None
    filename: str | None = None
    artifact_id: str | None = None


class RetrievalTrace(BaseModel):
    """Summary of retrieval before and after post-processing."""

    query: str
    raw_count: int = Field(ge=0)
    final_count: int = Field(ge=0)
    results: list[RetrievalTraceResult] = Field(default_factory=list)


def build_retrieval_trace(
    query: str,
    raw_nodes: list[NodeWithScore],
    final_nodes: list[NodeWithScore],
) -> RetrievalTrace:
    """Build a trace without including document text or sensitive metadata."""

    results: list[RetrievalTraceResult] = []
    for rank, node in enumerate(final_nodes, start=1):
        metadata: dict[str, Any] = node.metadata or {}
        score = round(float(node.score), 6) if node.score is not None else None
        results.append(
            RetrievalTraceResult(
                rank=rank,
                node_id=node.node_id,
                citation_id=metadata.get(MetadataFlags.SHORTER_ID.value),
                score=score,
                filename=metadata.get(MetadataKeys.FILENAME.value),
                artifact_id=metadata.get(MetadataKeys.ARTIFACT_ID.value),
            )
        )

    return RetrievalTrace(
        query=query,
        raw_count=len(raw_nodes),
        final_count=len(final_nodes),
        results=results,
    )
