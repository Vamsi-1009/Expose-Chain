# 🚀 Simple Deployment Guide - Vercel Only

## Why This Is Simple Now

✅ **NO Database Setup** - No Supabase, no PostgreSQL, nothing!
✅ **Just Vercel** - One platform, one deployment
✅ **2 Minutes** - Fastest deployment possible
✅ **Always Fresh** - Every scan gets real-time data

---

## Deploy to Vercel (2 Minutes)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Remove database - simplified deployment"
git push
```

### Step 2: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. **Environment Variables** - Add just ONE:
   ```
   CORS_ORIGINS = *
   ```
   (Or use your specific domain later)

5. Click **"Deploy"**
6. Wait ~2 minutes
7. **Done!** 🎉

### Step 3: Test Your Deployment

Visit: `https://your-app.vercel.app`

Try scanning: `example.com`

---

## That's It!

No database setup, no migration scripts, no connection strings!

### What You Get:

✅ **Full threat intelligence scanning**
- DNS analysis
- WHOIS lookup
- SSL certificate check
- Geolocation tracking
- AI risk prediction

✅ **Always fresh data** - Every scan is real-time

✅ **Global CDN** - Fast worldwide

✅ **Auto-scaling** - Handles traffic spikes

✅ **Free tier** - 100GB bandwidth/month

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run
uvicorn src.main:app --reload

# Open
http://localhost:8000
```

---

## Environment Variables (Optional)

For production, you can set:

```bash
CORS_ORIGINS=https://your-domain.com
RATE_LIMIT_ENABLED=true
ENVIRONMENT=production
DEBUG=False
```

But even without these, it works fine with defaults!

---

## Cost

**$0/month** on Vercel free tier

Covers:
- 100GB bandwidth
- Unlimited deployments
- Automatic HTTPS
- Global CDN

---

## Troubleshooting

### Issue: CORS errors
**Fix**: Set `CORS_ORIGINS=*` in Vercel env variables

### Issue: Rate limit errors
**Fix**: Set `RATE_LIMIT_ENABLED=false` for testing

### Issue: Build fails
**Fix**: Check Vercel function logs for errors

---

## Comparison: Before vs After

### Before (With Database):
1. Create Supabase account
2. Create database project
3. Run migration SQL
4. Copy connection string
5. Add to Vercel env vars
6. Deploy
7. Debug connection issues
8. Monitor database usage

**Total Time: 15-20 minutes**

### After (No Database):
1. Deploy to Vercel
2. Done

**Total Time: 2 minutes**

---

## Future: Want to Add Database Later?

If you later want scan history, you can easily add:
- SQLite (for local storage)
- Supabase (for cloud storage)
- MongoDB (for document storage)

But for now, enjoy the simplicity! 🎉
