# BhashaEngine Frontend

Next.js (App Router) + TypeScript + Tailwind CSS + Framer Motion.

## Run

```bash
cd frontend
npm install   # if not done
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). You should see the BhashaEngine Pro landing (no blank page).

## Backend

Start the FastAPI backend from `BhashaEngine`:

```bash
cd ../BhashaEngine
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --reload-exclude '.venv'
```

Or use `./run_api.sh` (after `chmod +x run_api.sh`).

## Stack

- **Next.js 14** (App Router)
- **Tailwind CSS**
- **Framer Motion** (animations)
- **Lucide React** (icons)
- **clsx + tailwind-merge** (for shadcn-style `cn()` in `lib/utils.ts`)

To add shadcn/ui components later: `npx shadcn@latest init` then `npx shadcn@latest add button`, etc.
