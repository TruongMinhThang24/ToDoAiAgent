// next.config.mjs

/** @type {import('next').NextConfig} */
const nextConfig = {
  // --- THÊM PHẦN NÀY ĐỂ SỬA LỖI ---
  turbopack: {
    // Chỉ định rõ thư mục gốc của dự án là thư mục hiện tại ('.')
    root: ".",
  },
  // ---------------------------------

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'mdbcdn.b-cdn.net',
        port: '',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;