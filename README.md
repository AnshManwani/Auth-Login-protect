\# BE-04: Containerized Stack (Flask + Postgres)



A small Items API demonstrating layered architecture: routes → service → repository,

with the repository swapped from in-memory to Postgres without touching the other layers.



\## Stack

\- Flask (Python) app

\- Postgres 16 (Docker, with a persistent volume)

\- Docker Compose to run both together



\## Running it



1\. Copy `.env.example` to `.env` (already has working defaults for local dev).

2\. Run: docker compose up --build

3\. The app will be available at `http://localhost:5000`.



\## Endpoints

\- `POST /items` — create an item (`{"name": "...", "description": "..."}`)

\- `GET /items` — list all items

\- `GET /items/<id>` — get one item

\- `DELETE /items/<id>` — delete an item



\## Architecture note



`app/service.py` and `app/routes.py` were written once against an `InMemoryItemRepository`.

When switching to Postgres, only `app/\_\_init\_\_.py` changed — one line, swapping

`InMemoryItemRepository` for `PostgresItemRepository`. Both repositories implement the

same interface (`create`, `get\_all`, `get\_by\_id`, `delete`), so the service and routes

layers were never touched. This is confirmed by comparing the two repository files:

same method signatures, same return types.



\## Persistence proof



To verify data survives a restart:

1\. Started the stack with `docker compose up --build`.

2\. Created two items via `curl -X POST .../items`.

3\. Confirmed both items appeared in `curl .../items`.

4\. Stopped the stack completely: `docker compose down` (this removes containers

&#x20;  but keeps the named volume `pgdata`).

5\. Restarted with `docker compose up`.

6\. Ran `curl .../items` again — both items were still present, confirming that

&#x20;  data persisted across a full app + container restart via the Docker volume.



\## Environment variables



See `.env.example`. `DATABASE\_URL` uses the Docker Compose service name `db` as

the host (not `localhost`), since the app and database run in separate containers

on the same Docker network.


\## Authentication

\- `POST /register` — body: `{"email": "...", "password": "..."}`. Returns
  201 with the created user (password never included). Returns 409 if
  the email is already taken.
\- `POST /login` — body: `{"email": "...", "password": "..."}`. Returns
  200 with `{"token": "..."}` on success, 401 with a generic message on
  any failure (wrong email or wrong password look identical to the caller).
\- Protected route: `DELETE /items/<id>` requires an `Authorization:
  Bearer <token>` header.
  \- No token or invalid/expired token → 401
  \- Valid token, but the item belongs to someone else → 403
  \- Valid token, own item → 204

Passwords are hashed with werkzeug's `generate_password_hash`
(never stored in plain text). JWTs are signed with a secret read from
`JWT_SECRET` in `.env` (never committed, see `.env.example`), and
expire after 24 hours.

Verified with a full test pass: register, duplicate register, login,
wrong password, authenticated create, delete without token, delete
someone else's item, delete own item — all returned the expected
status codes, and existing (pre-auth) routes were confirmed unchanged.
