# NexusParse - Asynchronous AI Extraction Fleet

NexusParse isn't just an API; it is a distributed, production-ready system designed to extract strict JSON schemas from unstructured data at scale. It securely processes workloads, tolerates failure, and gracefully handles traffic spikes through an event-driven architecture.

## Why this Architecture?

> La extracción de PDFs complejos con LLMs es I/O bound y propensa a latencias altas; un diseño asíncrono garantiza alta disponibilidad, previene bloqueos del API Gateway y permite escalar los workers de IA horizontalmente según la demanda.

Instead of monolithic blocking routines, we abstract complexity into discrete microservices:
1. **FastAPI Gateway**: Instantly authenticates, stores payloads in object storage, broadcasts events, and returns `202 Accepted` immediately.
2. **Celery Worker Fleet**: Independent containers capable of running heavily computational LLM queries asynchronously, implementing Retry Backoff strategies when mathematical hallucination or strict schema violations occur.
3. **Object Storage & Message Broker**: MinIO and Redis decouple the ingestion pipeline from the processing workload, preventing data loss during traffic spikes.

## Prerequisites
- Docker & Docker Compose
- `make`

## Quickstart (DevOps Guide)

Everything is pre-configured to build from scratch securely. Ensure you have your `OPENAI_API_KEY` mapped in your environment.

```bash
# Export your key explicitly before launching
export OPENAI_API_KEY="sk-..."

# 1. Spin up the entire ecosystem
make up

# 2. View streaming structured JSON logs
make logs

# 3. Verify health and linting
make test
make lint

# 4. Tear down
make down
```

## Sending a Payload

You'll need a JWT to push data. (In dev mode, check `api/auth.py` for token signature).

```bash
curl -X POST "http://localhost:8000/api/v1/extract/" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -F "file=@/path/to/invoice.pdf"
```

The server responds instantly while the Worker handles Langchain/OpenAI inference in the background.

## Schema Integrity

NexusParse sets a bold validation standard using `Pydantic`.
LLM hallucinations represent a systemic vulnerability in generic extraction platforms. Our implementation enforces mathematical rigidness over the AI's output. If the response violates structural integrity (e.g. `quantity * unit_price != total_price`), the pipeline intercepts the error, flags the hallucination, and automatically invokes an exponential retry backoff routine against the model to self-correct.
