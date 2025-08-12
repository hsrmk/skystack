## Next.js App (Vercel)

SkyStack’s frontend is a Next.js App Router project styled with Tailwind CSS and some shadcn/ui primitives.

### Scripts

From `app/`:

```bash
npm run dev     # start dev server (http://localhost:3000)
npm run build   # production build
npm run start   # start production server
npm run lint    # lint
```

Node 20+ is recommended. Install dependencies with `npm install`.

### Local development

```bash
cd app
npm install
npm run dev
```

Open http://localhost:3000.

### Project structure

- `src/app/` — App Router pages (`layout.tsx`, `page.tsx`)
- `src/sections/` — page sections (`Hero`, `Browse`, `WhatIsThis`, dialogs)
- `src/components/` — UI components (buttons, tooltips, grid, etc.)
- `src/lib/` — utilities and static data used by the UI

Key flows:

- `SearchCommand` opens a command palette to browse existing mocked accounts or accept a user-provided Substack URL.
- `MirrorNewsletterDialog` shows a progress UI (currently simulated by `ProcessingSubstack`) representing the backend `/createNewsletter` stream.

### Styling

- Tailwind CSS v4, configured in `tailwind.config.js` (dark mode via `class`).
- Global CSS under `src/app/globals.css` defines theme tokens and animations.
- shadcn/ui style primitives live under `src/components/ui/*` (button, dialog, command, tooltip) and use `@/lib/utils` `cn()` helper.

### Images

`next.config.ts` allows remote images from `https://substackcdn.com/**` via `remotePatterns`.

### Connecting to the backend

The current UI uses mocked data and a simulated event stream. To connect to the Flask service:

1. Expose a base URL (e.g., `NEXT_PUBLIC_API_BASE`) and use it for fetch calls in the app.
2. Replace the dummy events in `src/sections/ProcessingSubstack.tsx` with an EventSource or fetch+NDJSON parser to consume the `/createNewsletter` streaming response:

```ts
// outline
const res = await fetch(
	`${process.env.NEXT_PUBLIC_API_BASE}/createNewsletter`,
	{
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ url }),
	}
);
// Read stream line-by-line and set events state
```

3. If the backend is on a different origin in dev, enable CORS on Flask.

### Deployment (Vercel)

1. In Vercel, import the `app/` directory as a separate project.
2. Set any runtime env vars (e.g., `NEXT_PUBLIC_API_BASE`).
3. Build & deploy. The site is static + SSR as configured by Next.js.

### Notes

- The home page merges partial static data from `src/lib/browseSectionPartialData` with a remote gist (if available) to render the Browse grid.
- The hero grid is responsive and calculated dynamically in `src/components/HeroGrid.tsx`.
