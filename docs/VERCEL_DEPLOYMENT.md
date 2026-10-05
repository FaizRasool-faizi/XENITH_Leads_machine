# Deploying XENITH Solutions Lead Generator to Vercel

The modern Next.js SaaS frontend is located in the `frontend/` directory and is built for seamless 1-click deployment on [Vercel](https://vercel.com).

---

## Method 1: Deploy with Vercel CLI (Fastest)

1. Open your terminal in the `frontend/` folder:
   ```bash
   cd frontend
   ```

2. Run the Vercel deployment command:
   ```bash
   npx vercel
   ```
   *(Or install globally: `npm i -g vercel && vercel`)*

3. Follow the quick terminal prompts:
   - **Set up and deploy?** -> `Y`
   - **Which scope?** -> Select your Vercel account
   - **Link to existing project?** -> `N`
   - **Project name?** -> `xenith-lead-generator`
   - **In which directory is your code located?** -> `./`
   - **Want to modify build settings?** -> `N` (Next.js is auto-detected!)

4. To deploy to production:
   ```bash
   npx vercel --prod
   ```

---

## Method 2: Deploy via GitHub (Recommended for CI/CD)

1. Push this project to your GitHub repository (e.g., `xenith-lead-generator`).
2. Go to **[vercel.com/new](https://vercel.com/new)**.
3. Import your GitHub repository.
4. In the **Root Directory** setting, select **`frontend`**.
5. Framework Preset will automatically be detected as **Next.js**.
6. Click **Deploy**.
7. In ~60 seconds, your application will be live at `https://xenith-lead-generator.vercel.app`!

---

## Features Live on Vercel
- **Zero Cold Starts**: Lightning-fast edge & serverless API routes (`/api/leads`, `/api/analyze`).
- **Dark Mode SaaS Aesthetics**: TailwindCSS, glassmorphic panels, and smooth micro-animations.
- **SSRF Protected URL Scanner**: Safe website inspection with loopback / private IP filtering.
- **Dynamic Lead Scoring**: Instant priority computation and lead breakdown.
- **Multi-Channel Cold Outreach**: Personalized Email, LinkedIn InMail, and Cold Call script generator.
- **Suppression / DNC Registry**: Safeguard domains and phone numbers from accidental outreach.
- **Direct CSV Export**: Download high-priority leads with one click.
