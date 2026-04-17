FROM node:22-alpine AS build
WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm install
COPY src/ src/
COPY config/ config/
RUN npx tsc -p tsconfig.json

FROM node:22-alpine
WORKDIR /app
COPY --from=build /app/dist/ dist/
COPY --from=build /app/node_modules/ node_modules/
COPY config/ config/
COPY package.json ./

ENV TRANSPORT=http
ENV PORT=3100
ENV MCP_PATH=/mcp
EXPOSE 3100

CMD ["node", "--enable-source-maps", "dist/index.js"]
