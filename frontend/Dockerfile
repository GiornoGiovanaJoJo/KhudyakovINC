# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# Runner stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.output ./.output
# We still need package.json for some runtime dependencies in Nuxt 3 if not fully bundled
COPY --from=builder /app/package.json ./package.json

ENV HOST=0.0.0.0
ENV PORT=3000
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
