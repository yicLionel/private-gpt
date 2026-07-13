from llama_index.core.schema import NodeWithScore, TextNode

from private_gpt.components.workflows.retrieval.trace import build_retrieval_trace


def test_build_retrieval_trace_keeps_scores_and_source_metadata() -> None:
    raw = [
        NodeWithScore(
            node=TextNode(
                text="first",
                id_="node-1",
                metadata={
                    "shorter_id": "ABCD",
                    "file_name": "guide.pdf",
                    "artifact_id": "artifact-1",
                },
            ),
            score=0.91,
        ),
        NodeWithScore(node=TextNode(text="second", id_="node-2"), score=0.42),
    ]

    trace = build_retrieval_trace("where?", raw, raw[:1])

    assert trace.query == "where?"
    assert trace.raw_count == 2
    assert trace.final_count == 1
    assert trace.results[0].rank == 1
    assert trace.results[0].citation_id == "ABCD"
    assert trace.results[0].score == 0.91
    assert trace.results[0].filename == "guide.pdf"
