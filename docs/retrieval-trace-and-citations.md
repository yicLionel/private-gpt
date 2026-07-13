# Retrieval trace 与引用校验

## Retrieval trace

每次检索完成后，`RetrieverResultEvent.trace` 会记录不包含正文的结构化摘要：

- 原始召回数量与后处理后的数量；
- 每个结果的 rank、node id、citation id、score、文件名和 artifact id；
- 同一份 trace 会写入 `retrieval_trace=...` 日志，并放入 retriever tool 的 `raw_input.trace`。

示例：

```json
{
  "query": "公司假期政策",
  "raw_count": 5,
  "final_count": 3,
  "results": [
    {"rank": 1, "citation_id": "ABCD", "score": 0.91, "filename": "policy.pdf"}
  ]
}
```

trace 不记录文档正文，避免把完整知识库内容写入日志。

## Citation validation

回答结束时，`ExtractCitationInterceptor` 会检查模型输出中的 `[ABCD]` 等引用标识是否属于本次检索得到的文档：

- `valid_ids`：来自召回文档的引用；
- `invalid_ids`：未出现在召回文档中的引用；
- `validity`：有效引用数 / 引用总数；
- 结果写入当前 response context metadata，并通过结构化日志输出。

该校验只验证引用来源一致性，不判断引用内容是否真正支持回答。后续可以在此基础上增加 entailment 或 claim-level evaluation。

## Prompt Injection 防护

请求进入文档处理和模型调用前，`PromptInjectionRequestInterceptor` 会对用户文本和检索文档做确定性规则检查。命中后不会拒绝请求，而是把原文包在 `<untrusted_content>` 边界中，并明确提示模型其中的内容只能作为数据参考，不能改变系统规则、调用工具或覆盖既有指令。

防护摘要写入 response context metadata：

```json
{
  "detected": true,
  "rules": ["ignore_previous_instructions"],
  "user_count": 1,
  "document_count": 0
}
```

日志只记录规则名和计数，不记录完整用户消息或文档正文。文档的 citation id、artifact id 和 metadata 保持不变，因此不会影响已有引用校验。

运行测试：

```bash
uv run pytest -q \
  tests/components/workflows/test_retrieval_trace.py \
  tests/engines/test_citation_validation.py \
  tests/engines/test_prompt_injection_defense.py
```
