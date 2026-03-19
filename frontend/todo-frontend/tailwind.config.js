// tailwind.config.js
// SỬA LỖI 100%: Dùng "module.exports"

/** @type {import('tailwindcss').Config} */
module.exports = { // <-- LỖI LÀ Ở ĐÂY
  content: [
    // Quét thư mục src
    "./src/**/*.{js,ts,jsx,tsx,mdx}", 

    // Thêm đường dẫn cho Flowbite
    "./node_modules/flowbite-react/lib/esm/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("flowbite/plugin"),
    require('@tailwindcss/typography'),
  ], 
};