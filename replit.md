# Gemini Q&A

An interactive Streamlit app that sends user questions to Google Gemini and displays generated answers.

## Run & Operate

- `streamlit run app.py --server.port 8000 --server.headless true --browser.gatherUsageStats false` — run the app
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required secret: `GEMINI_API_KEY` — Google Gemini API key

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Python, Streamlit, Google GenAI SDK
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `app.py` — Streamlit interface and Gemini request flow
- `requirements.txt` — Python dependencies

## Architecture decisions

- Gemini access stays server-side through the `GEMINI_API_KEY` secret; the key is never embedded in source code.
- The current `google-genai` SDK is used instead of the deprecated `google-generativeai` package.

## Product

- Users can submit a free-form question and receive an AI-generated answer from Gemini.
- Empty submissions and API/configuration errors are surfaced inline.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
