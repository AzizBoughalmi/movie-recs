# 🎬 Deploy to Heroku via Web Dashboard (UI Method)

> **No CLI, no Docker locally** — All done through the Heroku website! ✨

This guide walks you through deploying your movie-recs app directly using Heroku's web dashboard.

---

## Prerequisites ✅

- Heroku account (free at https://www.heroku.com/)
- GitHub account with your movie-recs repository
- API keys ready:
  - TMDB_API_KEY from https://www.themoviedb.org/settings/api
  - GEMINI_API_KEY from https://makersuite.google.com/app/apikey
  - LANGSEARCH_API_KEY from your provider

---

## Step-by-Step Guide

### Step 1️⃣: Create a Heroku App

1. Go to https://dashboard.heroku.com/apps
2. Click **New** button (top right)
3. Select **Create new app**
4. Enter app name: `movie-recs-app` (or your chosen name)
5. Select region: **United States** or **Europe** (your preference)
6. Click **Create app**

✅ You now have a Heroku app!

---

### Step 2️⃣: Connect Your GitHub Repository

1. In your new app dashboard, go to **Deploy** tab (top menu)
2. Under "Deployment method", select **GitHub**
3. Click **Connect to GitHub**
   - Authorize Heroku to access your GitHub
   - Select your GitHub account
4. Search for repository: **movie-recs**
5. Click **Connect** next to the repo

✅ Your GitHub repo is now connected!

---

### Step 3️⃣: Enable Automatic Deployments (Optional)

Still in the **Deploy** tab:

1. Scroll down to "Automatic deploys"
2. Click **Enable Automatic Deploys**
3. Choose branch: **main**
4. Check **Wait for CI to pass before deploy** (optional, for safety)

✅ Now your app auto-deploys when you push to GitHub!

---

### Step 4️⃣: Set Environment Variables

**IMPORTANT:** Go to **Settings** tab (top menu):

1. Scroll to "Config Vars" section
2. Click **Reveal Config Vars**
3. Add these variables one by one:

| Key | Value | Where to Get |
|-----|-------|--------------|
| `TMDB_API_KEY` | your_tmdb_key | https://www.themoviedb.org/settings/api |
| `GEMINI_API_KEY` | your_gemini_key | https://makersuite.google.com/app/apikey |
| `LANGSEARCH_API_KEY` | your_langsearch_key | Your provider |
| `SECRET_KEY` | random_secure_string | Generate: see below |
| `LOG_LEVEL` | `DEBUG` | Default value |

**How to generate SECRET_KEY:**

Option 1 (Online generator):
- Go to https://www.random.org/bytes/
- Copy a random string of 32+ characters

Option 2 (Command line):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**For each variable:**
1. Click "Add"
2. Enter key (e.g., `TMDB_API_KEY`)
3. Enter value
4. Press Enter
5. Repeat for all variables

✅ All secrets configured!

---

### Step 5️⃣: Deploy Your App

**Option A: Manual Deploy** (test first)
1. Go back to **Deploy** tab
2. Scroll to "Manual deploy" section
3. Select branch: **main**
4. Click **Deploy Branch**
5. Wait for build to complete (5-10 minutes)
6. Watch the logs scroll by

**Option B: Automatic Deploy** (if enabled in Step 3)
1. Just push your code to GitHub:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push origin main
   ```
2. Heroku automatically builds and deploys!

✅ Deployment started!

---

### Step 6️⃣: Monitor Deployment

While deploying:

1. Find and click **View logs** button (during deployment)
2. Watch for messages:
   - ✅ `Building application`
   - ✅ `Slug compiled`
   - ✅ `Launching dyno`
   - ✅ `App started`

If you see errors:
- Check the red error messages
- Most common: Missing API key → Go back to Step 4 and add it
- Then re-deploy

---

### Step 7️⃣: View Your Deployed App

Once deployment is complete:

1. Click **Open app** button (top right)
2. Your app opens in browser at `https://your-app-name.herokuapp.com/`
3. You should see your React frontend load! 🎉

---

## ✅ Verification Checklist

After your app is live:

- [ ] Frontend loads (you see the React UI)
- [ ] Search bar works (try searching for a movie)
- [ ] API responds (check browser console for no CORS errors)
- [ ] Profile creation works (create a profile, see no errors)
- [ ] Logs show no errors (View logs → should be clean)

---

## 🔍 View Logs Anytime

To check your app's logs:

1. Go to your app dashboard
2. Click **More** button (top right) → **View logs**
3. Or click the **View logs** link in the activity section

Useful for debugging if something goes wrong.

---

## 🔄 Update Your App

Every time you make code changes and want to deploy:

```bash
# Local changes
git add .
git commit -m "Your changes"
git push origin main
```

If automatic deploys are enabled, Heroku automatically builds and deploys! 🚀

If not, manually deploy:
1. Go to **Deploy** tab
2. Click **Deploy Branch** under Manual Deploy

---

## 🆘 Common Issues & Fixes

### App crashes immediately

**Solution:**
1. Go to **Settings** → **Reveal Config Vars**
2. Verify all 4 keys are set (TMDB_API_KEY, GEMINI_API_KEY, LANGSEARCH_API_KEY, SECRET_KEY)
3. If any are missing, add them and app will restart
4. Check logs for the actual error message

### Frontend loads but API calls fail

**Solution:**
1. Open browser DevTools (F12)
2. Check Console tab for CORS errors
3. If you see CORS errors, the environment variables might not be set correctly
4. Verify all API keys in **Settings** → **Config Vars**

### Build fails

**Solution:**
1. Check the logs carefully for error messages
2. Most common: Dockerfile syntax error or missing files
3. Contact support with error message if unsure

### Can't find the "View logs" button

**Solution:**
1. Go to your app dashboard
2. Click **More** menu (⋯ top right)
3. Select **View logs**

---

## 📊 Monitor App Health

In your app dashboard:

- **Resources** tab: See your dyno type and memory usage
- **Logs** tab: Check recent activity
- **Metrics** (if paid): See performance data
- **Settings** → **Config Vars**: See/edit environment variables

---

## 🎯 Next Steps (After Deployment)

### Add Custom Domain (Paid accounts only)
1. **Settings** tab
2. Scroll to **Domains**
3. Add your custom domain

### Scale Your App
1. **Resources** tab
2. Change dyno type if needed (more memory/CPU)

### Connect Database (Optional)
1. **Resources** tab
2. Search "Heroku Postgres"
3. Add premium database

### Enable Monitoring
1. **Resources** tab
2. Add monitoring add-ons (New Relic, etc.)

---

## 🔐 Security Reminders

✅ **Correct:**
- API keys in Heroku Config Vars (encrypted)
- `.env` files NOT in GitHub (add to `.gitignore`)

❌ **Wrong:**
- Hardcoding keys in your code
- Committing `.env` to GitHub
- Sharing Config Vars publicly

---

## 💡 Pro Tips

1. **Always check logs before contacting support** — They often reveal the exact problem
2. **Use automatic deploys** — Easier than manual redeploys
3. **Keep main branch stable** — Only merge tested changes
4. **Monitor logs regularly** — Catch issues early
5. **Use meaningful commit messages** — Helps track what was deployed

---

## 📚 Heroku Resources

- **Heroku Dashboard:** https://dashboard.heroku.com/
- **Heroku Docs:** https://devcenter.heroku.com/
- **Container Deploy Docs:** https://devcenter.heroku.com/articles/container-registry-and-runtime
- **Troubleshooting:** https://devcenter.heroku.com/articles/troubleshooting-common-problems

---

## 🎉 Success!

Once verified:

```
✅ Frontend loads at https://your-app-name.herokuapp.com/
✅ API responds to requests
✅ Movie search works
✅ Profile creation works
✅ Logs show no errors
```

**Congratulations! Your movie recommendations app is live!** 🚀🎬

---

## Quick Reference

| Action | Steps |
|--------|-------|
| Create app | Dashboard → New → Create new app |
| Connect GitHub | Deploy tab → GitHub → Connect |
| Set API keys | Settings → Config Vars → Add |
| Deploy | Deploy tab → Deploy Branch |
| View logs | More menu → View logs |
| View live app | Open app button |
| Update code | Push to GitHub (if auto-deploy on) |

---

**Ready?** Start with Step 1 above. You've got this! 🚀
