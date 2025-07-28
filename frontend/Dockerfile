# Use an official Node.js runtime as the base image
FROM node:24-alpine

ENV DD_SERVICE="notes-frontend"
ENV DD_ENV="dev"
ENV DD_VERSION="0.1.0"
# environment variables
ENV NEXT_PUBLIC_HOST="localhost"
ENV NEXT_PUBLIC_PORT="5000"

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