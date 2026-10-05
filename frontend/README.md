This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy to Vercel

Connect the repository to Vercel and set **Root Directory** to `frontend`. Vercel will detect Next.js; no environment variable is required for the built-in `/api` routes. Set `NEXT_PUBLIC_API_URL` only if you have separately deployed the FastAPI backend and intend to use it instead.

The photo OCR runs in the visitor's browser, so Vercel function time and upload limits do not apply to OCR processing. Tesseract downloads its worker and Indonesian/English language data from jsDelivr on first use; the visitor needs an internet connection, and the browser can cache those files afterward.

The `backend/` FastAPI application is a separate service and is not deployed when Vercel's root directory is `frontend`. The frontend includes its own Next.js API routes. Admin data in those demo routes is currently in memory or mock data, so edits are not durable across Vercel function instances; persistent administration requires a database-backed API.

See the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
