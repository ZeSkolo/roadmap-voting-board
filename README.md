# Roadmap Voting Board

**Web development** · A persistent feature-request board with idempotent voting and a responsive browser client.

## Run locally

Python 3.11+; no third-party packages required. From this directory:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

`example.json` is the input contract and contains only synthetic or fictional data. `core.run(payload)` returns a JSON-serializable result. Invalid inputs produce an error and a nonzero CLI exit code.

## What it implements

- SQLite-backed idea creation and vote counts with unique voter/idea constraints.
- Duplicate votes are idempotent; user-generated titles are rendered as text, never HTML.
- Browser form, ranked ideas, refresh and visible API errors.
- Local-only HTTP server, same-origin checks, JSON-only mutations and body limits.

## Design and limitations

A single-user/local reference app, not a production multi-user platform. Voter IDs are client-generated pseudonyms, not authenticated identities; users can create another ID and vote again. There is no organizer account, moderation, login, anti-fraud system or public hosting. The default demo command uses an in-memory database; server mode persists .data/app.sqlite3.

## Suggested next step

Add your own data and domain-specific acceptance tests. Read and understand the implementation before presenting it in interviews. No live deployment is implied.

## Browser client

Run `python server.py --port 8000`, then open http://127.0.0.1:8000. Server mode persists `.data/app.sqlite3`. The demo CLI does not seed that database. Delete the local database only when you want to reset your own demo data. HTTP mutation clients must send JSON and `X-Local-Client: 1`; foreign browser origins are rejected.

<!-- AH-INDEPTH-DOCS:START -->
## In-depth engineering guide

### Problem and scope

A persistent feature-request board with idempotent voting and a responsive browser client.

This is an independent runnable reference implementation, with synthetic sample input and explicit limits. It is not a deployed service or independently validated business result.

### Architecture and end-to-end flow

```text
Browser form → same-origin JSON API → validated SQLite insert/vote → ranked idea list → DOM text rendering
```

| File | Responsibility |
|---|---|
| core.py | Domain validation and project-specific algorithm/state transitions |
| main.py | Bounded JSON CLI input, demo dispatch and JSON output |
| example.json | Exact reproducible sample input |
| tests/test_core.py | Unit and edge-case coverage |
| server.py | Loopback HTTP transport, Host/Origin/body guards, persistent SQLite mode |
| index.html / styles.css / app.js | Responsive browser UI and safe text rendering |

### Design decisions and trade-offs

1. The SQLite schema separates ideas from votes and enforces unique idea/voter pairs. Duplicate votes are idempotent for a given browser-generated identifier.

2. The browser stores a random pseudonymous voter ID in localStorage. Clearing storage or using another browser creates a new identity; this is not authentication or anti-fraud protection.

3. The CLI runs an isolated in-memory demo unless a db_path is supplied by a Python caller. server.py persists .data/app.sqlite3. User text is rendered with textContent rather than injected HTML.

### Reproducible setup

Requires Python 3.11+ and no third-party Python packages. Run from this project folder:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

CLI inputs are JSON objects, bounded to 1 MB. Supported domain errors produce a JSON error on stderr and a nonzero exit; inspect the message rather than treating a failed run as a result. The demo does not require a model key, network access or production data.

### Exact example input

```json
{
  "action": "demo"
}
```

### Core implementation interfaces

| Callable | Boundary |
|---|---|
| `connect(path)` | Implementation boundary; see source for validation and return structure. |
| `run(p, db_path=None)` | Implementation boundary; see source for validation and return structure. |

The Python `run` result is JSON-serializable. Inspect the source and `main.py run example.json` output for the exact return keys; do not assume another project’s result schema.

### HTTP contract

| Method/path | Behavior |
|---|---|
| GET /health | Liveness JSON; does not prove production readiness |
| GET /api | Current local records/jobs |
| POST /api | Domain action JSON; header X-Local-Client: 1 required |

JSON Content-Type is required for POST. Missing mutation header or foreign Origin produces 403; invalid JSON/domain input produces 400; non-JSON input produces 415; oversized/empty input produces 413. Only explicit static routes are served, never .data or arbitrary files. No accounts, TLS termination or public abuse protection are included.

Start `python server.py --port 8000`. Default persistence is `.data/app.sqlite3`; override PROJECT_DB for a separate environment. Do not delete a database you need to keep. The default server binds loopback; --container is an explicit all-interface mode; no Compose deployment is included in this standalone repository.

### Test coverage and reproducibility

- `tests/test_core.py::test_persistence`
- `tests/test_core.py::test_idempotent_vote`
- `tests/test_core.py::test_invalid`
- `tests/test_core.py::test_missing_idea`
- `tests/test_core.py::test_literal_content`
- `tests/test_http.py::test_health`
- `tests/test_http.py::test_post_guard`
- `tests/test_http.py::test_foreign_origin`
- `tests/test_http.py::test_private_files`
- `tests/test_http.py::test_malformed_json`

10 named tests are present in this folder. Run the command above to reproduce the local test results. Provider calls are mocked; Docker build/run was not executed; no real cloud/model/production-cluster validation is claimed.

### Security and failure boundaries

A single-user/local reference app, not a production multi-user platform. Voter IDs are client-generated pseudonyms, not authenticated identities; users can create another ID and vote again. There is no organizer account, moderation, login, anti-fraud system or public hosting. The default demo command uses an in-memory database; server mode persists .data/app.sqlite3.

Never commit .env, real API keys, runtime databases, approval material or customer data. See SECURITY.md. A successful example demonstrates the included workflow, not safe internet deployment.

### Troubleshooting

- **Import error:** run from this project’s own folder; each project intentionally has its own core.py.
- **Invalid sample/schema:** start from example.json, then change one field at a time and read the returned validation message.
- **Port already in use:** stop the previous process or select another --port where server.py exists.
- **SQLite lock/state surprise:** close duplicate processes, confirm PROJECT_DB and back up before deliberate resets. Do not delete unrelated project data.
- **External dependency unavailable:** default demos run offline; live provider calls and container pulls require your own working access and may incur external costs.

### Known limitations

A single-user/local reference app, not a production multi-user platform. Voter IDs are client-generated pseudonyms, not authenticated identities; users can create another ID and vote again. There is no organizer account, moderation, login, anti-fraud system or public hosting. The default demo command uses an in-memory database; server mode persists .data/app.sqlite3.

### Extension roadmap — not implemented

Add real identity, per-user authorization, moderation, rate limiting, migrations and abuse controls before accepting public votes.
<!-- AH-INDEPTH-DOCS:END -->
