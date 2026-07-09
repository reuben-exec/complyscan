import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  basePath: "/app",
  output: "export",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
