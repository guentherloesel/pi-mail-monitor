# Build Stage
FROM node:23 AS builder
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
RUN npx tsc

# Runtime Stage
FROM node:23-slim
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/dist ./dist
copy --from=builder /usr/src/app/node_modules ./node_modules
CMD ["node", "dist/analyzer.js"]