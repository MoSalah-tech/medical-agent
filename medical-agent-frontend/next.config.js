/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,   // skip TS errors during build
  },
  eslint: {
    ignoreDuringBuilds: true,  // skip ESLint errors during build
  },
};

module.exports = nextConfig;