# Template: react-vite (frontend only)

**Use for:** websites, dashboards, portfolios, UI over an existing/mock API. **Not for:** anything needing server-side secrets (move that to a backend).

## Create
```bash
npm create vite@latest client -- --template react      # or react-ts
cd client && npm install && npm run dev                 # http://localhost:5173
```
Or `engine/scripts/create-project.sh react-vite <dest> --scaffold`.

## Structure
```
client/src/
  main.jsx  App.jsx
  pages/        one file per route
  components/   reusable UI (check registry first)
  hooks/        useFetch, useLocalStorage…
  lib/api.js    single fetch wrapper; base URL from import.meta.env.VITE_API_URL
  index.css
```
Routing (only if >1 page): `npm i react-router-dom`. Charts: `recharts`. Styling: plain CSS or Tailwind if already present — don't add both.

## Contracts
- `lib/api.js` exports `api(path, {method, body})` → JSON or throws `Error(message)`.
- Every async view handles **loading / error / empty** states.
- Only `VITE_*` vars reach the browser — never put API keys there.

## Done when
`npm run build` passes · main flow works in browser · no console errors · responsive at 375px.
