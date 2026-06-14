# How to get your Junior.so token

Junior.so uses **magic-link login** (email code, no password),
so junior2api uses a static token extracted from your browser session.

## Step-by-step

1. Open [junior.so](https://junior.so) and log in
2. Press **F12** to open DevTools
3. Click the **Network** tab
4. Send any message to Junior in the chat
5. In the Network tab, find and click the request named `messages`
6. Click the **Headers** tab on the right
7. Scroll to **Request Headers** and copy these three values:

```
token: niwQc7CoO0VCVLx4d...   ← JUNIOR_TOKEN
uid: u_1f054c3ec4560fb4       ← JUNIOR_UID
junior-id: tm_90c590ee8b67f70f ← JUNIOR_TENANT_ID
```

## Put them in .env

```env
JUNIOR_TOKEN=niwQc7CoO0VCVLx4d...
JUNIOR_UID=u_1f054c3ec4560fb4
JUNIOR_TENANT_ID=tm_90c590ee8b67f70f
```

## Multi-account

To rotate across multiple accounts, log in as each user and collect their tokens:

```env
JUNIOR_ACCOUNTS=[{"token":"token1","uid":"u_xxx1","tenant_id":"tm_xxx"},{"token":"token2","uid":"u_xxx2","tenant_id":"tm_xxx"}]
```

## Token lifetime

The token is a long-lived session token — it stays valid until you log out of Junior.so.
If you get a 401/403 error, your token expired; just repeat these steps.
