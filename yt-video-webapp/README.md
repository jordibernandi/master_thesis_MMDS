## Getting Started - Run Web App with Docker
> **Prerequisite:** Ensure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/get-started).

### Step 1: Download the SQL Dump File

First, download the SQL dump file `ytvideodumpfile.sql` from this [Google Drive link](https://drive.google.com/drive/u/0/folders/1XUdTm7G_VdfUSoqqwNO_ETWjfjj97jzQ).

### Step 2: Initial Setup (Run these commands only once)

Run the following commands in your terminal to set up the web app and database for the first time, make sure you are inside the **yt-video-webapp** folder:

```bash
# Step 2.1: Build and run the Docker containers
# This will set up the production Next.js app and PostgreSQL database.
docker compose up --build
```

Wait for the containers to start running. Open a new terminal inside **yt-video-webapp** folder, and run the codes below.

```bash
# Step 2.2: Create the database inside the running PostgreSQL container
docker exec -it yt-video-webapp-db-1 psql -U postgres -c "CREATE DATABASE \"yt-video-db\";"
```

```bash
# Step 2.3: Import the SQL dump into the database
docker exec -i yt-video-webapp-db-1 psql -U postgres -d yt-video-db < <PATH_TO_SQL_DUMP>/ytvideodumpfile.sql
```
> **Note:** Replace `<PATH_TO_SQL_DUMP>` with the actual path where you downloaded the `ytvideodumpfile.sql`.

If everything works well, the webapp can be accessed via **http://localhost:3000/**

---
### Post-Setup Commands

After the initial setup, you can use these commands to manage your Docker containers:

```bash
# Stop the containers without removing them:
docker compose stop
```

```bash
# Start the containers again without rebuilding:
docker compose up
```
---
For easier management, consider installing Docker Desktop.





    

<!-- This is a [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/basic-features/font-optimization) to automatically optimize and load Inter, a custom Google Font.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details. -->
