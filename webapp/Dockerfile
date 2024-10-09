# Stage 1: Build the application
FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

# Copy only package.json and yarn.lock first for better caching
COPY package.json yarn.lock ./

# Install dependencies (this will cache dependencies if they haven't changed)
RUN yarn install --frozen-lockfile

# Copy the Prisma schema
COPY prisma ./prisma/

# Generate the Prisma client
RUN npx prisma generate

# Copy the rest of the app files
COPY . .

# Build the Next.js application for production
RUN yarn build

# Stage 2: Production image
FROM node:18-alpine AS production

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app/package.json /app/yarn.lock ./
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/prisma ./prisma

# Set the environment to production
ENV NODE_ENV=production

# Expose port 3000 for the Next.js app
EXPOSE 3000

# Set Prisma environment variable (optional, but recommended)
ENV PRISMA_CLIENT_ENGINE_TYPE=library

# Start the application in production mode
CMD ["yarn", "start"]

# FROM node:18-alpine

# # Set the working directory
# WORKDIR /app

# # Copy only package.json and package-lock.json (or yarn.lock) first for better caching
# COPY package*.json ./

# # Install dependencies
# RUN yarn install

# # Copy the prisma folder (this should come before the prisma generate step)
# COPY prisma ./prisma/

# # Generate Prisma client
# RUN npx prisma generate

# # Copy the rest of the app files
# COPY . .

# # Expose port 3000
# EXPOSE 3000

# # Start the application
# CMD ["yarn", "run", "dev"]




# FROM node:18-alpine

# WORKDIR /app
# COPY package*.json ./
# RUN yarn add

# COPY . .
# EXPOSE 3000
# CMD yarn run dev