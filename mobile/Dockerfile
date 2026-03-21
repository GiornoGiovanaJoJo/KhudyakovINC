# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# Serve stage — lightweight static server
FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve

COPY --from=builder /app/dist ./dist

ENV PORT=5174
EXPOSE 5174

CMD ["serve", "-s", "dist", "-l", "5174"]
