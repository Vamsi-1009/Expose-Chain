# 🚀 Deploy ExposeChain to Vercel - Complete Guide

## Why Vercel is Perfect for This Project

✅ **Supports Python** - Your FastAPI backend works out of the box
✅ **No Database Needed** - We removed it for simplicity
✅ **Free Tier** - 100GB bandwidth, unlimited functions
✅ **Global CDN** - Fast worldwide delivery
✅ **Auto HTTPS** - Secure by default
✅ **2-Minute Setup** - Already configured!

---

## Prerequisites

- ✅ GitHub account
- ✅ Code pushed to GitHub (already done!)
- ✅ Vercel account (free - we'll create it)

---

## Deployment Steps

### Step 1: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub

**Time: 1 minute** ⏱️

---

### Step 2: Import Your Project

1. Once logged in, click **"Add New..."** → **"Project"**
2. You'll see your GitHub repositories
3. Find **"Expose-Chain"** repository
4. Click **"Import"**

**Time: 30 seconds** ⏱️

---

### Step 3: Configure Project

Vercel will auto-detect your project settings:

✅ **Framework Preset**: Other (auto-detected)
✅ **Root Directory**: `./` (leave as is)
✅ **Build Command**: Auto-detected from `vercel.json`
✅ **Output Directory**: Auto-detected

**No changes needed - it's already configured!**

---

### Step 4: Add Environment Variables

Click **"Environment Variables"** section and add:

| Name | Value |
|------|-------|
| `CORS_ORIGINS` | `*` (or your specific domain later) |

**Optional variables** (can skip for now):
- `RATE_LIMIT_ENABLED`: `true`
- `ENVIRONMENT`: `production`

Click **"Add"** for each variable.

**Time: 30 seconds** ⏱️

---

### Step 5: Deploy!

1. Click the big **"Deploy"** button
2. Wait while Vercel:
   - Clones your repository
   - Installs Python dependencies
   - Builds your project
   - Deploys to global CDN

**Build time: 2-3 minutes** ⏱️

You'll see:
```
Building...  ████████████ 100%
✓ Build completed
✓ Deploying to production
```

---

### Step 6: Success! 🎉

Once deployed, you'll see:

```
🎉 Congratulations!
Your project is live at:
https://expose-chain-abc123.vercel.app
```

**Click the URL to open your deployed app!**

---

## Testing Your Deployment

### Test 1: Homepage
Visit: `https://your-app.vercel.app`

You should see the ExposeChain interface.

### Test 2: Health Check
Visit: `https://your-app.vercel.app/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "service": "ExposeChain"
}
```

### Test 3: API Documentation
Visit: `https://your-app.vercel.app/docs`

You'll see interactive FastAPI documentation.

### Test 4: Run a Scan
1. Go to your homepage
2. Enter: `example.com`
3. Click **"Start Scan"**
4. Wait for results

You should see:
- ✅ DNS records
- ✅ WHOIS information
- ✅ SSL certificate details
- ✅ Geolocation data
- ✅ AI risk prediction

---

## Update CORS (Important!)

After first deployment, update CORS for security:

1. Go to Vercel Dashboard
2. Click your project → **Settings** → **Environment Variables**
3. Edit `CORS_ORIGINS`
4. Change from `*` to your actual URL:
   ```
   https://expose-chain-abc123.vercel.app
   ```
5. Click **Save**
6. Go to **Deployments** tab
7. Click **"Redeploy"** on latest deployment

---

## Custom Domain (Optional)

Want your own domain? (e.g., `exposechain.com`)

1. Buy a domain (Namecheap, GoDaddy, etc.)
2. In Vercel: Settings → **Domains**
3. Click **"Add"**
4. Enter your domain
5. Follow DNS configuration instructions
6. Wait for DNS propagation (5-30 minutes)

**Then update CORS_ORIGINS to your custom domain!**

---

## Troubleshooting

### Build Failed

**Check the build logs:**
1. Deployments tab → Click failed deployment
2. Click **"Building"** to see logs
3. Look for error messages

**Common issues:**
- Missing dependency → Check `requirements.txt`
- Python version issue → We use 3.11 (configured in `vercel.json`)
- Import error → Check all files committed to GitHub

### Runtime Error (500)

**Check function logs:**
1. Deployments → Latest deployment
2. Click **"Functions"** tab
3. Find the failing function
4. Click **"View Logs"**

**Common issues:**
- Missing environment variable
- Import error at runtime
- CORS configuration issue

### CORS Errors in Browser

**Symptoms:** Console shows:
```
Access to fetch at '...' has been blocked by CORS policy
```

**Fix:**
1. Verify `CORS_ORIGINS` includes your frontend URL
2. Format must be: `https://your-app.vercel.app` (no trailing slash)
3. Redeploy after changing environment variables

### Scan Not Working

**Check:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try a scan
4. Look for failed requests (red)
5. Click on failed request → Preview tab for error

---

## Monitoring & Maintenance

### View Analytics
1. Vercel Dashboard → Your Project
2. Click **"Analytics"** tab
3. See:
   - Page views
   - Function invocations
   - Bandwidth usage
   - Response times

### View Logs
1. Click **"Deployments"**
2. Click latest deployment
3. Click **"Functions"** → **"View Logs"**
4. See real-time function execution logs

### Update Code
```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push

# Vercel auto-deploys on push!
```

---

## Cost & Limits

### Free Tier Includes:
- ✅ 100GB bandwidth/month
- ✅ 100 hours serverless function execution
- ✅ Unlimited deployments
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments

### When to Upgrade:
- **Pro ($20/month)** if you exceed:
  - 100GB bandwidth
  - Need team collaboration
  - Want custom analytics

**For personal/learning projects, free tier is plenty!**

---

## Post-Deployment Checklist

- [ ] Deployment successful
- [ ] Homepage loads correctly
- [ ] `/health` endpoint returns healthy
- [ ] `/docs` shows API documentation
- [ ] Test scan works (try `example.com`)
- [ ] DNS results appear
- [ ] WHOIS data appears
- [ ] SSL certificate shows
- [ ] AI analysis displays
- [ ] Updated CORS_ORIGINS to actual URL
- [ ] Redeployed after CORS update
- [ ] Saved deployment URL

---

## Your Deployment URL

After deployment, save this:

```
Production: https://expose-chain-abc123.vercel.app
Dashboard: https://vercel.com/[your-username]/expose-chain
```

---

## Next Steps

1. ✅ **Share your deployment** - Send the URL to friends/colleagues
2. ✅ **Test thoroughly** - Try different domains (google.com, github.com, etc.)
3. ✅ **Monitor usage** - Check Vercel analytics
4. ⭐ **Star the repo** - If you like it!
5. 🎨 **Customize** - Update UI colors, add features

---

## Support

**Issues during deployment?**
- Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
- View build logs for errors
- Check this file for troubleshooting tips

**App working but need features?**
- All core features are working (DNS, WHOIS, SSL, AI)
- No database means always fresh scans
- Rate limiting protects from abuse

---

## Summary

✅ **Total deployment time: ~5 minutes**
✅ **Cost: $0**
✅ **Maintenance: Automatic**
✅ **Scaling: Automatic**
✅ **HTTPS: Automatic**

**Your ExposeChain is now live and globally accessible!** 🚀

Enjoy your deployed threat intelligence platform! 🎉
