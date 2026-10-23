# Template: mern (MongoDB + Express + React + Node)

**Use when** MongoDB/Mongoose or "MERN" is required. Otherwise prefer `fullstack-crud` (SQLite, no DB server).

## Create
```bash
engine/scripts/create-project.sh mern ~/Desktop/<name>      # server/ starter + .env.example
cd ~/Desktop/<name>/server && npm install && npm i mongoose
npm create vite@latest ../client -- --template react && (cd ../client && npm install)
```
MongoDB: local `brew services start mongodb-community` or Atlas URI in `server/.env` (`MONGODB_URI`).

## Structure
```
server/src/
  index.js  app.js        app factory (testable without listen)
  db.js                   mongoose.connect(process.env.MONGODB_URI)
  models/<Thing>.js       schema + validation (required, enum, min/max)
  routes/<things>.js      express.Router; thin
  controllers/            optional for >3 handlers
  middleware/auth.js      requireAuth, requireRole('admin')  → see database-auth skill
client/src/  (react-vite template)
```

## API contract (per resource)
`GET /api/things?search=&page=` · `GET /api/things/:id` · `POST /api/things` · `PUT /api/things/:id` · `DELETE /api/things/:id`
Errors → `{ error: string }` with 400/401/403/404/500. Validate ObjectId → 400, not 500.

## Dev
Two terminals: `cd server && npm run dev` · `cd client && npm run dev`. Vite proxy (`vite.config.js` → `server.proxy: {'/api': 'http://localhost:5000'}`) avoids CORS in dev.

## Done when
CRUD works end-to-end in browser · `npm test` in server passes (supertest or node:test) · client builds · auth routes reject without token.
