import { NextConfig } from "next";

const nextConfig = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  images: {
    remotePatterns: [],
  },
} satisfies NextConfig;

export default nextConfig;
