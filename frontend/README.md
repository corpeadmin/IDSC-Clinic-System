# IDSC Clinic System — Frontend

React 19 + Vite project for the IDSC Clinic System.

> **Status: the clinic UI is not implemented.** This directory contains the unmodified Vite + React
> starter template. `src/App.jsx` renders the Vite demo landing page — a counter, template logos, and
> links to the Vite and React sites. There is no clinic screen, no routing, no state management, and
> no API client.

## Current contents

| File | Purpose |
| :--- | :--- |
| `index.html` | HTML entry template |
| `package.json` | Dependencies and npm scripts |
| `vite.config.js` | Vite config — React plugin only |
| `eslint.config.js` | ESLint configuration |
| `src/main.jsx` | React root mount point |
| `src/App.jsx` | Vite starter landing page |
| `src/App.css` | Template stylesheet |
| `src/index.css` | Template stylesheet and CSS custom properties |
| `src/assets/` | `hero.png`, `react.svg`, `vite.svg` — template images |
| `public/` | `favicon.svg`, `icons.svg` — template assets |

## Scripts

```bash
npm install     # install dependencies
npm run dev     # start the dev server on http://localhost:5173
npm run build   # production build to dist/
npm run lint    # run ESLint
npm run preview # preview the production build
```

## Backend connection

There is currently **no configured connection to the backend**.

`vite.config.js` contains only the React plugin — no `server.proxy` and no API base URL. No `fetch`
or `axios` call exists anywhere in `src/`.

The Django backend runs on `http://127.0.0.1:8000` and serves CORS headers for
`http://localhost:5173` and `http://127.0.0.1:5173`, so those origins may call it directly.

## Reference

- API contract: [../API.md](../API.md), [../openapi.json](../openapi.json)
- Endpoint inventory and screen status: [../docs/architecture.md](../docs/architecture.md)
- UI and design-system status: [../docs/design-system.md](../docs/design-system.md)