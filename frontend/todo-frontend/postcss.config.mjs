// postcss.config.mjs
// SỬA LẠI CHO v3: Dùng "tailwindcss" thay vì "@tailwindcss/postcss"

const config = {
  plugins: {
    tailwindcss: {}, // SỬA Ở ĐÂY
    autoprefixer: {},
  },
};

export default config;