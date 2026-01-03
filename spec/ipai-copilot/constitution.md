# Constitution: IPAI Copilot

## Mission
To provide immediate, grounded answers to Finance Ops and Accounting users directly within the Odoo interface, reducing context switching and operational friction during month-end closes and compliance tasks.

## Principles
1.  **Contextual & Immediate**: Answers should be available where the user is working, not in a separate tab.
2.  **Grounded in Truth**: ALl answers must cite specific documents, SOPs, or tasks. Hallucination is a failure.
3.  **Minimal Footprint**: The architecture should remain simple (Odoo -> Serverless RAG). No heavy middleware platforms.
4.  **Deterministic**: Ingestion of knowledge must be reproducible. Code is the source of truth for the codebase; Docs/Seeds are the source of truth for the RAG index.

## Operational Constraints
- **Odoo CE Only**: Must work without Enterprise features.
- **Privacy**: No user data sent to LLM without explicit context inclusion logic (v1 starts generic).
- **Performance**: UI must be non-blocking and lightweight.
