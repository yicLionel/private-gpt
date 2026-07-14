"""Validation helpers for citations emitted by an LLM."""

from __future__ import annotations

import re
from dataclasses import dataclass

from private_gpt.components.engines.citations.types import Document

_CITATION_PATTERN = re.compile(r"\[([A-Za-z0-9]{2,64})\]")


@dataclass(frozen=True)
class CitationValidationResult:
    """Whether citation identifiers refer to retrieved documents."""

    referenced_ids: list[str]
    valid_ids: list[str]
    invalid_ids: list[str]
    validity: float

    def as_dict(self) -> dict[str, object]:
        return {
            "referenced_ids": self.referenced_ids,
            "valid_ids": self.valid_ids,
            "invalid_ids": self.invalid_ids,
            "validity": self.validity,
        }


def validate_citations(
    response_text: str,
    documents: list[Document],
) -> CitationValidationResult:
    """Check bracketed citation IDs against the retrieved document set.

    This is intentionally syntactic: it verifies provenance, not whether the
    cited text semantically entails the answer.
    """

    referenced_ids = list(dict.fromkeys(_CITATION_PATTERN.findall(response_text)))
    available_ids = {document.id for document in documents}
    valid_ids = [
        citation_id for citation_id in referenced_ids if citation_id in available_ids
    ]
    invalid_ids = [
        citation_id
        for citation_id in referenced_ids
        if citation_id not in available_ids
    ]
    validity = round(len(valid_ids) / len(referenced_ids), 3) if referenced_ids else 1.0
    return CitationValidationResult(
        referenced_ids=referenced_ids,
        valid_ids=valid_ids,
        invalid_ids=invalid_ids,
        validity=validity,
    )
