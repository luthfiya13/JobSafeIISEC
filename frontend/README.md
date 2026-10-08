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

Deploy the FastAPI backend as a separate service. Set **Root Directory** to `frontend` in Vercel and configure `NEXT_PUBLIC_API_URL` to the backend API base, for example `https://api.example.com/api`. There is no local analysis or admin demo fallback: analysis, authentication, history, settings, and reports require this backend.

The photo OCR runs in the visitor's browser. Tesseract downloads its worker and Indonesian/English language data from jsDelivr on first use; the visitor needs an internet connection, and the browser can cache those files afterward.

The backend imports the versioned model from `Model/` and serves its hybrid rule+ML result. Configure `SECRET_KEY` (at least 32 random characters), `ADMIN_EMAIL`, and `ADMIN_PASSWORD` in the backend environment. CORS must allow the deployed frontend origin. The admin portal has no demo credentials or mock-data routes.

See the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
