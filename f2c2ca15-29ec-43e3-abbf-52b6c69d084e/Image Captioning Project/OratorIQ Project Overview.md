# OratorIQ Monorepo Project

This canvas initializes the **OratorIQ** project with a complete monorepo structure including:

## Project Structure
```
oratoriq/
├── client/          # Frontend (Vite + TypeScript)
├── server/          # Backend (Express + TypeScript)
├── shared/          # Shared types and utilities
├── package.json     # Root workspace config
└── .env.example     # Environment variables template
```

## Tech Stack
- **Client**: Vite, React, TypeScript
- **Server**: Express, TypeScript, Node.js
- **Build Tools**: TypeScript, Concurrently
- **Package Management**: npm workspaces

## Getting Started
1. Review the generated folder structure
2. Copy `.env.example` to `.env` and configure
3. Run `npm install` in root directory
4. Run `npm run dev` to start both client and server concurrently