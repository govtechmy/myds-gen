/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    proxyTimeout: 1000 * 120,
  },
};

module.exports = nextConfig;
