# 🚀 New Collaborator Guide

Welcome to **explique.ai**! This guide will help you get up and running with the project, even if you're completely new to the technologies we use.

## 📋 What is explique.ai?

Explique.ai is an AI-powered educational platform that helps students understand subjects by explaining them to an LLM (Large Language Model).

The platform also includes video features where admins can upload lecture videos, process them with AI. This data is then provided to a chatbot as context when students are watching a lecture video.

## 🛠️ Tech Stack Overview

Our project uses a modern full-stack architecture. Here's what you need to know:

### Frontend

- **[Next.js 14](https://nextjs.org/docs)** - React framework for web applications
- **[React 18](https://react.dev/learn)** - JavaScript library for building user interfaces
- **[TypeScript](https://www.typescriptlang.org/docs/)** - Type-safe JavaScript
- **[Tailwind CSS](https://tailwindcss.com/docs)** - Utility-first CSS framework

### Backend & Database

- **[Convex](https://docs.convex.dev/)** - Backend-as-a-Service with real-time database

### AI & External Services

- **[OpenAI API](https://platform.openai.com/docs)** - AI language model for interactive learning conversations
- **[Google Generative AI](https://ai.google.dev/docs)** - Gemini models for content analysis and video processing
- **[Google OAuth](https://developers.google.com/identity/protocols/oauth2)** - Authentication system

### Development Tools

- **[Storybook](https://storybook.js.org/docs)** - Component development environment
- **[Sentry](https://docs.sentry.io/)** - Error monitoring and performance tracking

## 🏁 Quick Start

### Prerequisites

Make sure you have the following installed:

1. **[Node.js](https://nodejs.org/)** (version 18 or higher)
   - Download from the official website or use [nvm](https://github.com/nvm-sh/nvm)
2. **[npm](https://docs.npmjs.com/)** (comes with Node.js)
3. **[Git](https://git-scm.com/downloads)** for version control

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/expliqueai/explique.git
cd explique

# Install dependencies
npm install
```

### 2. Set Up Convex (Backend)

[Convex](https://docs.convex.dev/) is our backend-as-a-service. You need to connect your local development to a Convex project:

```bash
# Start the Convex development server
npm run dev:server
```

When prompted:

- Connect with your **GitHub account**
- Choose any project name you like (e.g., `explique-dev-[your-name]`)
- The tool will create a new Convex project for your development

After setup is complete, stop the server with `Ctrl+C`.

### 3. Configure Environment Variables

#### Open Convex Dashboard

```bash
npx convex dashboard
```

This opens your Convex project dashboard where you'll set environment variables.

#### Required Environment Variables

In the Convex dashboard, go to **Settings** → **Environment Variables** and add:

1. **OpenAI API Key** (`OPENAI_API_KEY`)

   - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Contact a team member if you need access to the project's API key

2. **Google OAuth Setup** (for authentication)

   - Follow [Google's OAuth setup guide](https://support.google.com/cloud/answer/6158849)
   - Create OAuth credentials with redirect URI: `http://localhost:3000/authRedirect`
   - Add these variables:
     - `GOOGLE_CLIENT_ID`: Your OAuth client ID
     - `GOOGLE_CLIENT_SECRET`: Your OAuth client secret

3. **Base URL** (`BASE_URL`)

   - Set to: `http://localhost:3000`

4. **Google AI API Key** (`GOOGLE_AI_API_KEY`)
   - Get one from [Google AI Studio](https://ai.google.dev/)
   - Used for Gemini AI models

### 4. Seed Development Database

Create sample data for development:

```bash
npm run seed
```

**Important**: Before running this command, add your email address to the admin list:

1. Open `convex/internal/seed.ts`
2. Find the admin emails array (around line 106)
3. Add your email address to the list:

```typescript
for (const email of [
  "nicolas.ettlin@epfl.ch",
  "ola.svensson@epfl.ch",
  // ... other emails
  "your.email@example.com", // Add your email here
]) {
```

This ensures you have admin access in the development environment.

### 5. Start Development

```bash
# Start both frontend and backend
npm run dev
```

This command starts:

- Next.js frontend at `http://localhost:3000`
- Convex backend development server

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## 📁 Project Structure

```
explique/
├── src/                   # Next.js frontend code
│   ├── app/               # App router pages and layouts
│   ├── components/        # Reusable React components
│   ├── hooks/             # Custom React hooks
│   └── util/              # Utility functions
├── convex/                # Backend code (Convex)
│   ├── auth/              # Authentication logic
│   ├── admin/             # Admin-specific functions
│   ├── video/             # Video processing and chat
│   └── schema.ts          # Database schema
├── docs/                  # Internal documentation
├── public/                # Static assets
└── k8s/                   # Kubernetes deployment files for EPFL cluster
```

## 🔧 Common Development Tasks

### Running Tests

```bash
# Run the development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Database Management

```bash
# Generate database migration files
npm run generate-migration-files

# Run database migrations
npm run migrate

# Re-seed the database
npm run seed
```

### Storybook (Component Development)

```bash
# Start Storybook for component development
npm run storybook

# Build Storybook for deployment
npm run build-storybook
```

### Convex Commands

```bash
# Open Convex dashboard
npx convex dashboard

# Deploy to production (when ready)
npx convex deploy

# View logs
npx convex logs
```

## 🎯 Key Concepts

### Authentication Flow

- Users log in via Google OAuth
- [Lucia v3](https://lucia-auth.com/) manages authentication sessions
- Admin users can access course management features

### Core Learning Experience

- Students explain concepts to AI to deepen their understanding
- Interactive conversations help identify knowledge gaps
- AI provides feedback and asks clarifying questions
- Based on the pedagogical principle of "learning by teaching"

### Video Processing (Secondary Feature)

- Videos are uploaded and processed using AI
- Content is chunked and analyzed using Gemini AI
- Users can chat about specific video segments

### Real-time Features

- Convex provides real-time database updates
- Chat messages appear instantly across clients
- No need for manual polling or WebSocket setup

## 🐛 Troubleshooting

### Common Issues

1. **"Convex client not configured"**

   - Make sure you ran `npm run dev:server` first
   - Check that `.env.local` contains your Convex URL

2. **Authentication not working**

   - Verify Google OAuth credentials in Convex dashboard
   - Check that redirect URI matches exactly: `http://localhost:3000/authRedirect`

3. **Database errors**

   - Try re-running the seed: `npm run seed`
   - Check Convex dashboard for error logs

4. **AI features not working**
   - Verify API keys are set in Convex dashboard
   - Check API key permissions and billing status

### Getting Help

- Check the [docs/](./docs/) folder for detailed documentation
- Review Convex logs: `npx convex logs`
- Ask team members on Slack/Discord
- Check the [Convex Discord](https://www.convex.dev/community) for framework-specific help

## 📚 Learning Resources

This section provides a structured learning path for new contributors. Follow this order for the most effective learning experience:

### 🎯 Phase 1: Foundation (Start Here!)

**1. TypeScript Fundamentals** ⭐ _Start with this_

- **[TypeScript Handbook](https://www.typescriptlang.org/docs/)** - Essential for understanding our codebase
- **[TypeScript for JavaScript Programmers](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html)** - Quick intro if you know JS
- **[TypeScript Playground](https://www.typescriptlang.org/play)** - Practice TypeScript interactively

**2. React Basics** (if needed)

- **[React Official Tutorial](https://react.dev/learn)** - Modern React with hooks
- **[React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)** - React + TypeScript patterns

**3. Modern JavaScript/ES6+** (if needed)

- **[MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)** - Comprehensive reference
- Focus on: Arrow functions, async/await, destructuring, modules, promises

### 🚀 Phase 2: Core Technologies

**4. Next.js Framework**

- **[Next.js Documentation](https://nextjs.org/docs)** - Start with "Getting Started"
- **[Next.js Learn Course](https://nextjs.org/learn)** - Interactive tutorial
- **[App Router vs Pages Router](https://nextjs.org/docs/app)** - We use App Router (Next.js 13+)

**5. Tailwind CSS**

- **[Tailwind CSS Docs](https://tailwindcss.com/docs)** - For styling components
- **[Tailwind Play](https://play.tailwindcss.com/)** - Practice utility classes

### 🛠️ Phase 3: Backend & Database

**6. Convex Backend**

- **[Convex Documentation](https://docs.convex.dev/)** - Read "Quickstart" and "Database" sections
- **[Convex + Next.js Guide](https://docs.convex.dev/quickstart/nextjs)** - Our exact setup
- **[Convex Functions](https://docs.convex.dev/functions)** - Understanding queries, mutations, and actions

### 🤖 Phase 4: AI Integration

**7. OpenAI API**

- **[OpenAI API Reference](https://platform.openai.com/docs/api-reference)** - For AI integrations
- **[OpenAI Cookbook](https://cookbook.openai.com/)** - Practical examples

**8. Google AI (Gemini)**

- **[Google AI Studio](https://ai.google.dev/docs)** - For video processing features

### 🎨 Phase 5: Advanced Topics

**9. Component Development**

- **[Storybook Documentation](https://storybook.js.org/docs)** - For component development
- **[React Design Patterns](https://react-patterns.com/)** - Best practices

**10. Advanced Next.js**

- **[React Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)** - Next.js 13+ pattern we use
- **[Next.js Performance](https://nextjs.org/docs/app/building-your-application/optimizing)** - Optimization techniques

### 🔐 Phase 6: Authentication & Security

**11. Authentication Systems**

- **[Lucia v3 Documentation](https://lucia-auth.com/)** - Our auth library
- **[OAuth 2.0 Simplified](https://oauth.net/2/)** - Understanding OAuth flow

### ⏱️ Estimated Time Investment

- **Phase 1 (Foundation)**: 1-2 weeks for beginners, 2-3 days for experienced developers
- **Phase 2 (Core Tech)**: 1 week
- **Phase 3 (Backend)**: 3-5 days
- **Phase 4 (AI)**: 2-3 days
- **Phase 5-6 (Advanced)**: Ongoing as needed

### 💡 Learning Tips

1. **Don't try to learn everything at once** - Follow the phases in order
2. **Build small examples** - Try concepts in isolation before diving into our codebase
3. **Use our codebase as reference** - After learning basics, see how we implement patterns
4. **Ask questions early** - Team members are here to help!

### 🎯 Quick Reference Cards

Once you're comfortable with the basics, these are great for quick lookups:

- **[TypeScript Cheat Sheet](https://www.typescriptlang.org/cheatsheets)**
- **[React + TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)**
- **[Tailwind CSS Cheat Sheet](https://tailwindcomponents.com/cheatsheet/)**
- **[Next.js Cheat Sheet](https://nextjs.org/docs)**

## 🌿 Git Workflow & Conventions

We follow strict Git conventions to maintain a clean, readable project history. Please follow these guidelines for all contributions.

### 🚀 Branch Naming Convention

Always create a new branch for your work. Use one of these prefixes:

```bash
# New features
feat/add-user-dashboard
feat/implement-video-chat

# Bug fixes
fix/authentication-redirect
fix/mobile-responsive-layout

# Maintenance and refactoring
chore/update-dependencies
chore/cleanup-unused-imports

# Documentation updates
docs/update-api-documentation
docs/add-setup-instructions

# Performance improvements
perf/optimize-database-queries
perf/reduce-bundle-size

# Styling and UI changes
style/update-button-colors
style/fix-mobile-layout
```

### 📝 Commit Message Convention

We use **[Conventional Commits](https://www.conventionalcommits.org/)** format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types:

- `feat`: New feature for the user
- `fix`: Bug fix for the user
- `docs`: Changes to documentation
- `style`: Formatting, missing semicolons, etc; no production code change
- `refactor`: Refactoring production code, eg. renaming a variable
- `test`: Adding missing tests, refactoring tests; no production code change
- `chore`: Updating grunt tasks etc; no production code change
- `perf`: Performance improvements
- `ci`: Changes to CI configuration files and scripts

#### Examples:

```bash
# Good commit messages
git commit -m "feat(auth): add Google OAuth integration"
git commit -m "fix(chat): resolve message ordering issue"
git commit -m "docs: update API documentation for video endpoints"
git commit -m "chore(deps): update Next.js to v14.2.0"
git commit -m "refactor(components): extract reusable Button component"

# Bad commit messages (avoid these)
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "WIP"
```

## 🚀 Ready to Contribute?

1. **Explore the codebase**: Start by looking at `src/app/page.tsx` and `convex/schema.ts`
2. **Run the app**: Follow the setup steps above
3. **Check issues**: Look for "good first issue" labels in your project management tool
4. **Make changes**: Create feature branches and submit pull requests
5. **Ask questions**: Don't hesitate to reach out to team members

Happy coding! 🎉

---

_For more detailed information about specific features, check the [docs/](./docs/) directory._
