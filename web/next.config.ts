import type { NextConfig } from "next";

const apiUrl = process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL;
let apiOrigin = "";

if (apiUrl) {
  try {
    apiOrigin = new URL(apiUrl).origin;
  } catch {
    throw new Error(`Invalid API_INTERNAL_URL/NEXT_PUBLIC_API_URL: ${apiUrl}`);
  }
}

const connectSrc = [
  "'self'",
  "https://www.google-analytics.com",
  "https://analytics.google.com",
].filter(Boolean).join(" ");

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    if (!apiOrigin) return [];
    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin}/api/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), payment=()",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains",
          },
          {
            key: "Content-Security-Policy",
            value:
              `default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data: https:; font-src 'self' data:; connect-src ${connectSrc}; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline';`,
          },
        ],
      },
    ];
  },
};

export default nextConfig;
