import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  // Proxy FinSight X API calls to the Python FastAPI backend (port 8000).
  // LOCAL DEV: requests stay same-origin (/api/fs/...) and are proxied here to
  // 127.0.0.1:8000. Override with FS_API_ORIGIN if the backend runs elsewhere.
  // PRODUCTION (Vercel): the frontend calls the backend directly via
  // NEXT_PUBLIC_API_BASE_URL (see src/lib/finsight/api.ts), so this rewrite
  // is not involved — no localhost dependency remains in production.
  async rewrites() {
    const apiOrigin = (process.env.FS_API_ORIGIN ?? "http://127.0.0.1:8000").replace(/\/+$/, "");
    return [
      {
        source: "/api/fs/:path*",
        destination: `${apiOrigin}/api/fs/:path*`,
      },
    ];
  },
};

export default nextConfig;
