# Use an official Node.js runtime as the base image
FROM node:24-alpine AS build

ENV DD_SERVICE="notes-frontend"
ENV DD_ENV="dev"
ENV DD_VERSION="0.1.0"

# references the backend container name
ENV NEXT_PUBLIC_HOST="backend-service"
ENV NEXT_PUBLIC_PORT="5000"
ENV NEXT_PUBLIC_BASE_URL="http://35.190.120.223/api"

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy the project files to the container
COPY . .

# Build the Next.js application
RUN npm run build

# Expose the Next.js application port
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "start"]

# ====== Nginx stage ======
# FROM nginx:alpine

# Remove default Nginx static contents
# RUN rm -rf /usr/share/nginx/html/*

# Copy static site from Next.js build
# COPY --from=build /app/out /usr/share/nginx/html

# Optional: Copy custom nginx.conf (e.g., for 404 fallback)
# COPY nginx.conf /etc/nginx/nginx.conf

# EXPOSE 80

#CMD ["nginx", "-g", "daemon off;"]