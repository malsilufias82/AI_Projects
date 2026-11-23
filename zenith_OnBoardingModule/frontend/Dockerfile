FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY pnpm-lock.yaml ./


# Copy source code first (needed for quasar prepare)
COPY . .

# Install dependencies (quasar prepare will run as postinstall)
RUN npm install

# Expose port
EXPOSE 8101

# Run dev server
CMD ["npm", "run", "dev"]
