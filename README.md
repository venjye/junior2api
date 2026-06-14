# junior2api

A project converting the [Junior.so](https://junior.so) web interface to an OpenAI-compatible API.

> Inspired by [ds2api](https://github.com/venjye/ds2api) and [qwen2API](https://github.com/venjye/qwen2API)

## Features

- OpenAI-compatible — drop-in replacement for any OpenAI client
- Auto session refresh — re-logs in automatically when token expires
- Multi-account rotation — round-robin across multiple Junior.so accounts
- Streaming support — `stream: true` works out of the box
- Docker ready — one command deploy

## Quick Start

```bash
git clone https://github.com/venjye/junior2api
cd junior2api
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker

```bash
cp .env.example .env
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

## Configuration

Copy `.env.example` to `.env`:

| Variable | Description |
|---|---|
| `JUNIOR_EMAIL` | Your Junior.so login email |
| `JUNIOR_PASSWORD` | Your Junior.so password |
| `JUNIOR_TENANT_ID` | Your workspace ID (`tm_xxxx`) |
| `JUNIOR_ACCOUNTS` | JSON array for multi-account rotation |
| `API_KEY` | Optional: protect your endpoint |

### Multi-account

```env
JUNIOR_ACCOUNTS=[{"email":"a@junior.so","password":"pass1","tenant_id":"tm_xxx"},{"email":"b@junior.so","password":"pass2","tenant_id":"tm_xxx"}]
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /v1/models` | List models |
| `POST /v1/chat/completions` | Chat (OpenAI-compatible) |

## License

MIT
