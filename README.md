# junior2api

A project converting the [Junior.so](https://junior.so) web interface to an OpenAI-compatible API.

> Inspired by [ds2api](https://github.com/venjye/ds2api) and [qwen2API](https://github.com/venjye/qwen2API)

## Features

- OpenAI-compatible — drop-in replacement for any OpenAI client
- Static token auth — works with Junior.so's magic-link login (no password needed)
- Multi-account rotation — round-robin across multiple accounts
- Streaming support — `stream: true` works out of the box
- Docker ready — one command deploy

## Quick Start (Local)

### 1. Get your token

Junior.so uses email-code login (no password), so you extract the token from your browser:

1. Open [junior.so](https://junior.so) and log in
2. Open DevTools → **Network** tab → send any message to Junior
3. Click the `messages` request → **Headers** tab → copy:
   - `token: xxx` → your `JUNIOR_TOKEN`
   - `uid: u_xxx` → your `JUNIOR_UID`
   - `junior-id: tm_xxx` → your `JUNIOR_TENANT_ID`

See [GET_TOKEN.md](./GET_TOKEN.md) for detailed instructions.

### 2. Configure

```bash
git clone https://github.com/venjye/junior2api
cd junior2api
cp .env.example .env
# Edit .env — paste your token, uid, tenant_id
```

### 3. Run

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker

```bash
cp .env.example .env
# Edit .env
docker-compose up -d
```

## Usage

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="any")
response = client.chat.completions.create(
    model="junior",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"junior","messages":[{"role":"user","content":"Hello!"}]}'
```

## Configuration (.env)

| Variable | Description |
|---|---|
| `JUNIOR_TOKEN` | Your session token from browser DevTools |
| `JUNIOR_UID` | Your user ID (`u_xxx`) |
| `JUNIOR_TENANT_ID` | Your workspace ID (`tm_xxxx`) |
| `JUNIOR_ACCOUNTS` | JSON array for multi-account rotation |
| `API_KEY` | Optional: protect your endpoint |

### Multi-account

```env
JUNIOR_ACCOUNTS=[{"token":"tok1","uid":"u_xxx1","tenant_id":"tm_xxx"},{"token":"tok2","uid":"u_xxx2","tenant_id":"tm_xxx"}]
```

## Token Expiry

The token is long-lived (lasts until you log out of Junior.so). If it expires, repeat the DevTools steps and update `.env`.

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /v1/models` | List models |
| `POST /v1/chat/completions` | Chat (OpenAI-compatible) |

## License

MIT
