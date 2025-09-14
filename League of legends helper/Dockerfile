# Multi-stage build for League of Legends Assistant
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY seneca/react-vite-app/package*.json ./seneca/react-vite-app/

# Install dependencies
RUN npm install
RUN cd seneca/react-vite-app && npm install

# Copy source code
COPY . .

# Build React app
WORKDIR /app/seneca/react-vite-app
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Copy package files and install production dependencies
COPY package*.json ./
RUN npm install --only=production

# Copy built React app and server files
COPY --from=builder /app/seneca/react-vite-app/dist ./seneca/react-vite-app/dist
COPY proxy-server.js ./
COPY *.json ./

# Create a simple static file server for the React app
RUN npm install express --save

# Create startup script
RUN echo '#!/bin/sh\n\
echo "Starting League of Legends Assistant..."\n\
echo "Environment: $NODE_ENV"\n\
echo "Riot API Key present: $([ -n "$RIOT_API_KEY" ] && echo "Yes" || echo "No")"\n\
\n\
# Start proxy server in background\n\
node proxy-server.js &\n\
PROXY_PID=$!\n\
\n\
# Start static file server for React app\n\
node -e "\n\
const express = require(\"express\");\n\
const path = require(\"path\");\n\
const app = express();\n\
const PORT = process.env.PORT || 3000;\n\
\n\
app.use(express.static(path.join(__dirname, \"seneca/react-vite-app/dist\")));\n\
\n\
app.get(\"*\", (req, res) => {\n\
  res.sendFile(path.join(__dirname, \"seneca/react-vite-app/dist/index.html\"));\n\
});\n\
\n\
app.listen(PORT, () => {\n\
  console.log(\`React app serving on port \${PORT}\`);\n\
});\n\
" &\n\
REACT_PID=$!\n\
\n\
# Wait for any process to exit\n\
wait\n\
' > start.sh && chmod +x start.sh

# Expose ports
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Start the application
CMD ["./start.sh"]