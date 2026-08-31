# Architecture Diagram

[Client/Request]
      │
      ▼
[Google Cloud Run / gcp_router]
      │
      ▼
[SGRM / Gemini 3.5 Selector] <--> [Strategy Decision]
      │
      ▼
[Deterministic Router / Router.py]
      │
      ├── [Deterministic Circuit] --> [Result]
      └── [Independent Oracle]  --> [Verify]
      │
      ▼
[Observability / Audit Logs]
