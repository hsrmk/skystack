import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "substackcdn.com",
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;