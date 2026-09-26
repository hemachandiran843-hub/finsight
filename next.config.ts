import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  // Proxy FinSight X API calls to the Python FastAPI backend (port 8000).
  // This covers direct :3000 access in dev; the Caddy gateway also routes
  // these requests via ?XTransformPort=8000.
  async rewrites() {
    return [
      {
        source: "/api/fs/:path*",
        destination: "http://127.0.0.1:8000/api/fs/:path*",
      },
    ];
  },
};

export default nextConfig;
