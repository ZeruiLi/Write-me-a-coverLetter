filecap-service (sidecar)

Run locally:

  cd workers/filecap_service
  poetry install
  export GEMINI_API_KEY=...
  poetry run uvicorn main:app --port 8101

Endpoints:
- GET  /healthz
- POST /extract/resume_file (multipart file) -> ResumeExtractRaw
- POST /extract/jd_file     (multipart file) -> JDObjectV1

Main backend: set FILECAP_URL=http://127.0.0.1:8101
