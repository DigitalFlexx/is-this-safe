# Is This Safe? — Extension Auditor

A Chrome extension that audits every other extension you have installed, explains their permissions in plain English, and flags the riskiest ones at the top.

**100% local — no data ever leaves your browser.**

---

## What it does

- Lists every installed extension with a **Trust Score (0–100)**
- Colour-coded verdict: **Safe** (green) · **Caution** (amber) · **High Risk** (red)
- Plain-English explanation of *why* each extension scored as it did
- One-click shortcut to Chrome's extension manager to disable or remove anything suspicious
- Background service worker badges the toolbar icon with the count of High Risk extensions

---

## Install (Developer Mode)

1. Clone or download this repository.
2. Generate the icons: `python3 create-icons.py`
3. Open Chrome and go to `chrome://extensions`.
4. Enable **Developer mode** (top-right toggle).
5. Click **Load unpacked** and select the `is-this-safe/` folder.
6. The shield icon appears in your toolbar.

---

## Trust Score model

Every extension starts at **100** and loses points for risky signals:

| Signal | Penalty |
|---|---|
| Access to all websites (`<all_urls>`) | −35 |
| Access to sensitive sites (banking, email, social) | −10 each, max −25 |
| `tabs` — can read all open tab URLs/titles | −10 |
| `webRequest` — can monitor network traffic | −20 |
| `cookies` — can read login cookies | −15 |
| `history` — can read full browsing history | −15 |
| `scripting` — can inject code into pages | −15 |
| `clipboardRead` — can read clipboard | −10 |
| `nativeMessaging` — talks to a local app | −15 |
| `debugger` — full browser debug access | −25 |
| Not from Chrome Web Store (sideloaded) | −20 |

Score ≥ 80 → **Safe** · 50–79 → **Caution** · < 50 → **High Risk**

Weights live in `src/scoring.js` so they are easy to tune.

---

## File structure

```
is-this-safe/
├── manifest.json
├── create-icons.py          # Run once to generate icons/
├── icons/                   # 16 / 32 / 48 / 128 px PNGs
├── src/
│   ├── background.js        # Service worker: badge, snapshot diff, notifications
│   ├── popup.html / .css / .js   # Extension popup UI
│   ├── scoring.js           # Trust score model (weights + logic)
│   ├── permissions-dictionary.js # Permission → plain-English map
│   └── storage.js           # Snapshot save/load/diff helpers
└── tests/
    └── scoring.test.html    # Open in Chrome to run unit tests
```

---

## Privacy

- **Zero network requests.** All scoring is computed locally from the data Chrome's `management` API returns.
- No analytics, no telemetry, no third-party SDKs in v1.
- The only permission that might look scary is `management` — it is required to read your other extensions' permissions, and nothing is transmitted anywhere.

---

## Roadmap

- [ ] Chrome Web Store submission
- [ ] Pro tier (ExtensionPay): continuous monitoring, change-history log, scheduled email reports
- [ ] Side panel option (wider view for power users)
- [ ] CRX hash / update-URL anomaly detection
