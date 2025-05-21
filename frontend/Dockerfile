# Use Node.js to build React
FROM node:20

# Set working directory
WORKDIR /app

# Copy and install
COPY . .
RUN npm install && npm run build

# Install serve to host the app
RUN npm install -g serve

EXPOSE 5173

CMD ["serve", "-s", "dist", "-l", "5173"]
