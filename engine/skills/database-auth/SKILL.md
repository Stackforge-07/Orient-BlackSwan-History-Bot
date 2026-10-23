---
name: database-auth
description: Choose and wire a database (SQLite, MongoDB, Postgres) and implement secure authentication and role-based access (bcrypt + JWT or sessions). Use when a project needs persistence, login, registration or admin/user roles.
---
# Database & auth

## Pick the DB
Brief names one → use it. Else SQLite (file, no server) for demos/exams; MongoDB when "MERN"; Postgres only if installed or required. Never store data only in memory for a "management system".

## Schema rules
Constraints in the DB (NOT NULL, UNIQUE email, CHECK/enum role) + server validation. Timestamps `created_at`. SQL: prepared statements only. Mongo: schema validation in Mongoose, cast/validate ObjectId.

## Auth (JWT for SPA + API)
- `users(id, name, email UNIQUE, password_hash, role DEFAULT 'user')`.
- Register: validate, `bcrypt.hash(pw, 10)` (bcryptjs if native build fails), never return hash.
- Login: compare → `jwt.sign({sub:id, role}, process.env.JWT_SECRET, {expiresIn:'1d'})`. Same error for wrong email or password.
- `requireAuth`: read `Authorization: Bearer`, verify, `req.user`; 401 on failure.
- `requireRole(...roles)`: 403 if `req.user.role` not allowed. Check ownership for user-owned resources (`WHERE id=? AND user_id=?`).
- First admin: seed script or env-driven (`ADMIN_EMAIL`), never a hardcoded password in code.
- Client: store token in memory + localStorage (acceptable for demos; mention httpOnly cookie as hardening), attach header in `api.js`, redirect to login on 401, hide admin UI by role (server still enforces).
- `JWT_SECRET` required at startup; `.env.example` holds a placeholder only.

## Python equivalent
`passlib[bcrypt]` + `pyjwt`; `Depends(get_current_user)`; role check dependency.

## Test
register → login → protected 200; no token 401; user hitting admin route 403; duplicate email 409.
