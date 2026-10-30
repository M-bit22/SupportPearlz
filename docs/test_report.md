# SupportPearlz — Test Report

**Project:** SupportPearlz — LangChain RAG Customer Support Agent  
**Evaluation date:** 30 October 2026

## 1. Evaluation approach

The evaluation dataset contains 20 test cases covering customer support hours, shipping, refunds, follow-up questions, missing information, and refusal behavior.

The automated evaluation was started but interrupted because sequential Gemini API requests were taking too long. Therefore, no complete automated evaluation results are claimed.

## 2. Test evidence

| Test area | Evidence | Status |
|---|---|---|
| Document ingestion | Screenshot 01 | Captured |
| FAISS index construction | Screenshot 02 | Captured |
| Answer with source citations | Screenshot 03 | Captured |
| Refusal for missing information | Screenshot 04 | Captured |
| Follow-up conversation | Screenshot 05 | Captured |
| Graceful error handling | Screenshot 06 | Captured |

## 3. Evaluation dataset

The 20 test cases are defined in `evaluation/test_questions.json`.

They cover:
- Directly answerable questions
- Questions requiring contextual understanding
- Partially documented policies
- Unanswerable questions
- Missing shipping and refund information
- Missing customer support contact details

## 4. Metrics

A complete automated metric report was not produced because the evaluation run was interrupted.

| Metric | Result |
|---|---|
| Total designed test cases | 20 |
| Completed automated test cases | Not established |
| Answer correctness | Not measured across all cases |
| Source retrieval coverage | Not measured across all cases |
| Refusal rate | Not measured across all cases |
| Hallucination count | Not measured |

## 5. Known limitations

- The knowledge base does not document every refund and shipping scenario.
- The model may generate unsupported details in some responses.
- The automated evaluation requires multiple sequential LLM requests and may be constrained by API quotas and response latency.
- Follow-up query rewriting is not independently exposed in the current interface.

## 6. Conclusion

The application demonstrates document ingestion, vector indexing, retrieval-augmented question answering, source display, refusal behavior, conversation follow-ups, and graceful error handling. The six captured screenshots provide implementation evidence. A complete automated evaluation remains outstanding.
