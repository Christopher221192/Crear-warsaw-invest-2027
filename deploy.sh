#!/bin/bash
# =============================================================================
# 🚀 Poland House Hunter - One-Click Deployment Script
# =============================================================================
# Run this ONCE after configuring your GitHub credentials.
# Prerequisites: git auth configured (SSH key or HTTPS token)
# =============================================================================

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🇵🇱 Poland House Hunter — Cloud Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ------- CONFIG -------
GITHUB_USER="Christopher221192"
FRONTEND_REPO="warsaw-invest-2027"
SCRAPER_REPO="warsaw-scraper-pipeline"

FRONTEND_DIR="$(dirname "$0")"
SCRAPER_DIR="$(dirname "$0")/../AppPolandHouse"

# ------- STEP 1: Push Frontend -------
echo ""
echo "📦 Step 1: Pushing Frontend (Next.js) to GitHub..."
cd "$FRONTEND_DIR"

if ! git remote get-url origin &>/dev/null; then
  git remote add origin "https://github.com/${GITHUB_USER}/${FRONTEND_REPO}.git"
  echo "   ✅ Remote added: ${FRONTEND_REPO}"
else
  echo "   ⏭️  Remote already exists, skipping."
fi

git branch -M main
git push -u origin main 2>&1 && echo "   ✅ Frontend pushed!" || echo "   ⚠️  Push failed — create the repo on GitHub first: https://github.com/new"

# ------- STEP 2: Push Scraper -------
echo ""
echo "🔍 Step 2: Pushing Scraper Pipeline to GitHub..."
cd "$SCRAPER_DIR"

if ! git remote get-url origin &>/dev/null; then
  git remote add origin "https://github.com/${GITHUB_USER}/${SCRAPER_REPO}.git"
  echo "   ✅ Remote added: ${SCRAPER_REPO}"
else
  echo "   ⏭️  Remote already exists, skipping."
fi

git branch -M main
git push -u origin main 2>&1 && echo "   ✅ Scraper pushed!" || echo "   ⚠️  Push failed — create the repo on GitHub first: https://github.com/new"

# ------- STEP 3: Remind Vercel setup -------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NEXT STEPS (Manual on Vercel Dashboard):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Go to https://vercel.com/new"
echo "2. Import repo: ${GITHUB_USER}/${FRONTEND_REPO}"
echo "3. Framework: Next.js (auto-detected)"
echo "4. Add Environment Variables from .env.example:"
echo "   • POSTGRES_URL (from Vercel Storage > Postgres)"
echo "   • TELEGRAM_BOT_TOKEN"
echo "   • ALLOWED_CHAT_ID"
echo "   • GITHUB_TOKEN"
echo "   • GITHUB_REPO_OWNER = ${GITHUB_USER}"
echo "   • GITHUB_REPO_NAME = ${SCRAPER_REPO}"
echo ""
echo "5. On GitHub repo '${SCRAPER_REPO}' → Settings → Secrets:"
echo "   • POSTGRES_URL (same as Vercel)"
echo "   • TELEGRAM_BOT_TOKEN"
echo "   • ALLOWED_CHAT_ID"
echo "   • VERCEL_APP_URL = https://your-app.vercel.app"
echo ""
echo "6. Set Telegram Webhook:"
echo "   curl https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-app.vercel.app/api/telegram-webhook"
echo ""
echo "7. Initialize Postgres (run SQL in Vercel's query console):"
echo "   → Copy contents of setup_postgres.sql"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Done! Once configured, send /scrape to your Telegram bot."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
