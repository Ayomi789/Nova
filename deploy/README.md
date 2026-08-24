# Nova Live Demo — Deployment

Two ways to get a permanent portfolio link.

---

## Option A — Render (always-on, recommended)

Works even when your PC is off. Free tier; sleeps after 15 min
idle (first visitor waits ~50 s, then instant).

### 1. Push Nova to GitHub

`config/secrets.json` is already gitignored — your API key will NOT be uploaded.

```bash
cd C:\Users\DELL\Nova
git add -A
git commit -m "Nova agent with live demo"
git remote add origin https://github.com/<you>/nova.git
git push -u origin main
```

### 2. Deploy on Render

1. Sign up at https://render.com (use GitHub login)
2. New + → **Blueprint** → pick the `nova` repo → Apply
   (Render reads `render.yaml` automatically)
3. When prompted, paste your `NVIDIA_API_KEY`
4. Done — you get a permanent URL like:

```
https://nova-demo.onrender.com
```

Put that on your portfolio.

### Keep it warm (optional)

Free services sleep. Point a free monitor at it:
https://uptimerobot.com → HTTP monitor every 5 min → no more cold starts.

---

## Option B — Cloudflare quick tunnel (works right now)

Already running:

```
https://laptops-normally-gentleman-null.trycloudflare.com
```

- Lives only while this PC runs `nova` + the tunnel process
- URL changes if the tunnel restarts
- Good for demos/interviews on demand, not for a static portfolio link

Restart it any time:

```powershell
C:\Users\DELL\Nova\.bin\cloudflared.exe tunnel --url http://127.0.0.1:8788
```

---

## Local test of the deploy entrypoint

```bash
set NVIDIA_API_KEY=your_key
python serve_demo.py
# open http://127.0.0.1:8788
```
