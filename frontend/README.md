# Scrum Ceremony Platform - Frontend

Real-time collaborative Scrum ceremony management platform built with Next.js 15, React 19, TypeScript, TailwindCSS, Radix UI, Yjs, and XState.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: TailwindCSS with custom design system
- **UI Components**: Radix UI primitives
- **State Management**: Zustand + XState
- **Real-time**: Yjs + y-protocols + y-websocket
- **Data Fetching**: TanStack React Query v5
- **Authentication**: Clerk
- **Icons**: Lucide React
- **Testing**: Playwright (E2E)
- **Linting/Formatting**: Biome

## Getting Started

### Prerequisites

- Node.js >= 20.0.0
- npm >= 10.0.0

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Update .env.local with your actual values
# - Get your Clerk keys from https://dashboard.clerk.com
# - Set your API URL and WebSocket URL

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`.

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run Biome linter |
| `npm run lint:fix` | Fix lint issues automatically |
| `npm run format` | Format code with Biome |
| `npm run typecheck` | Run TypeScript type checking |
| `npm run test:e2e` | Run Playwright E2E tests |
| `npm run test:e2e:ui` | Run Playwright with UI mode |

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (app)/              # Authenticated route group
│   │   │   ├── dashboard/      # Dashboard page
│   │   │   └── layout.tsx      # App layout with sidebar
│   │   ├── globals.css         # Global styles + CSS variables
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Landing page
│   ├── components/
│   │   └── ui/                 # Reusable UI components
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       └── card.tsx
│   ├── lib/
│   │   ├── api.ts              # API client with typed endpoints
│   │   ├── utils.ts            # Utility functions
│   │   └── yjs.ts              # Yjs document & WebSocket setup
│   └── stores/
│       └── ceremony-store.ts   # Zustand store for ceremony state
├── e2e/                        # Playwright E2E tests
├── public/                     # Static assets
├── .env.example                # Environment variable template
├── biome.json                  # Biome configuration
├── Dockerfile                  # Multi-stage Docker build
├── next.config.mjs             # Next.js configuration
├── package.json
├── tailwind.config.ts          # TailwindCSS configuration
├── tsconfig.json               # TypeScript configuration
└── playwright.config.ts        # Playwright configuration
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key | Yes |
| `CLERK_SECRET_KEY` | Clerk secret key | Yes (server) |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_WS_URL` | WebSocket server URL | Yes |
| `NEXT_PUBLIC_APP_URL` | Public app URL | No |
| `NEXT_PUBLIC_APP_NAME` | App name | No |

## Docker

```bash
# Build the image
docker build \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx \
  --build-arg NEXT_PUBLIC_API_URL=http://api:8000 \
  --build-arg NEXT_PUBLIC_WS_URL=ws://api:8000/ws \
  -t scrum-frontend .

# Run the container
docker run -p 3000:3000 scrum-frontend
```

## License

MIT