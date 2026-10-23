---
name: frontend-ui
description: Build clean, working React (Vite) UIs — pages, forms, tables, chat views, dashboards — wired to an API with loading/error/empty states. Use for any user-facing interface work.
---
# Frontend UI

## Reuse first
Check registry for existing components/hooks (chat box, file upload, markdown renderer, toast, modal). Match the repo's existing styling approach (CSS modules / Tailwind / plain CSS) — never introduce a second one.

## Rules
- One API wrapper (`src/lib/api.js`); components never hardcode URLs.
- Every data view: loading, error (message + retry), empty state.
- Forms: controlled inputs, client validation mirroring server rules, disable submit while pending, show server `{error}`.
- Lists: key by id, search/filter client-side if <200 rows else server-side.
- Accessibility basics: `<label htmlFor>`, buttons are `<button>`, visible focus, alt text.
- Layout: max-width container, 8px spacing scale, one accent color, system font stack or one web font. Mobile-first; test at 375px.
- State: `useState`/`useReducer`; add Context only for auth/user; no Redux unless required.
- Chat UIs: auto-scroll, disable input while streaming, render markdown safely (no `dangerouslySetInnerHTML` with model output unless sanitized), show citations as clickable chips.

## Patterns
```jsx
const { data, error, loading, reload } = useFetch('/api/items'); // hooks/useFetch.js
if (loading) return <Spinner/>; if (error) return <ErrorBox msg={error} onRetry={reload}/>;
if (!data.items.length) return <Empty text="No items yet"/>;
```

## Verify
`npm run build` · open the app, click through the main flow, check browser console is clean.
