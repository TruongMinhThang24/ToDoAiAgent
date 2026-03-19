# ==========================================
# STAGE 1: DEPENDENCIES
# ==========================================
FROM node:18-alpine AS deps
# Alpine cần libc6-compat cho một số thư viện native
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy các file quản lý package (hỗ trợ npm, yarn, pnpm)
COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# ==========================================
# STAGE 2: BUILDER
# ==========================================
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Tắt Next.js Telemetry để build nhanh hơn và bảo mật dữ liệu
ENV NEXT_TELEMETRY_DISABLED 1

# Tiến hành Build Next.js
RUN npm run build

# ==========================================
# STAGE 3: RUNNER
# ==========================================
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Tạo user non-root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy thư mục public
COPY --from=builder /app/public ./public

# Tự động tạo thư mục cache cho Next.js và cấp quyền
RUN mkdir .next
RUN chown nextjs:nodejs .next

# COPY bản build dạng standalone (Rất nhẹ)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Chuyển user
USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Chạy server Nodejs mặc định của bản standalone (Không chạy qua npm nữa)
CMD ["node", "server.js"]