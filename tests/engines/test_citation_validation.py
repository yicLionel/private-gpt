from private_gpt.components.engines.citations.types import Document
from private_gpt.components.engines.citations.validation import validate_citations


def test_validate_citations_accepts_only_retrieved_document_ids() -> None:
    documents = [
        Document(
            type="document",
            id_="node-1",
            shorter_id="ABCD",
            document_id="artifact-1",
            text="one",
        ),
        Document(
            type="document",
            id_="node-2",
            shorter_id="EFGH",
            document_id="artifact-2",
            text="two",
        ),
    ]

    result = validate_citations("结论 [ABCD]，外部引用 [ZZZZ]。", documents)

    assert result.referenced_ids == ["ABCD", "ZZZZ"]
    assert result.valid_ids == ["ABCD"]
    assert result.invalid_ids == ["ZZZZ"]
    assert result.validity == 0.5


def test_validate_citations_reports_no_citation_without_failing() -> None:
    result = validate_citations("没有引用。", [])

    assert result.referenced_ids == []
    assert result.invalid_ids == []
    assert result.validity == 1.0
