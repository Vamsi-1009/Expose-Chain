# ExposeChain Deployment Guide
## Supabase + Vercel Architecture

This guide walks you through deploying ExposeChain with:
- **Database**: Supabase (PostgreSQL)
- **Full Stack**: Vercel (Frontend + Backend as serverless functions)

---

## Architecture Overview

```
┌─────────────────┐
│   Vercel        │
│  (Frontend +    │ ──────► Supabase PostgreSQL
│   Backend API)  │         (Database)
└─────────────────┘
```

---

## Part 1: Setting Up Supabase Database

### Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click **"New Project"**
4. Fill in:
   - **Name**: `exposechain`
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier is fine to start

5. Wait for project to provision (~2 minutes)

### Step 2: Run Database Migration

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **"New Query"**
3. Copy the entire contents of `migrations/supabase_migration.sql` from this repo
4. Paste into the SQL editor
5. Click **"Run"** (bottom right)
6. You should see success messages for all tables created

### Step 3: Get Database Connection String

1. In Supabase dashboard, go to **Settings** → **Database**
2. Scroll to **Connection String** section
3. Select **URI** tab
4. Copy the connection string that looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the password you set in Step 1
6. **Save this connection string** - you'll need it for Vercel

### Step 4: Verify Tables Created

1. Go to **Table Editor** in Supabase dashboard
2. You should see `scan_records` table
3. Click on it to verify the schema matches

---

## Part 2: Deploying to Vercel

### Step 1: Prepare Your Repository

1. Make sure all changes are committed:
   ```bash
   git add .
   git commit -m "Prepare for Supabase + Vercel deployment"
   git push
   ```

### Step 2: Deploy to Vercel

1. Go to [https://vercel.com](https://vercel.com)
2. Sign up or log in (use GitHub authentication for easier integration)
3. Click **"Add New Project"**
4. Import your GitHub repository containing ExposeChain
5. Vercel will auto-detect it's a Python project

### Step 3: Configure Environment Variables

In the Vercel project settings, add these environment variables:

| Name | Value | Description |
|------|-------|-------------|
| `DATABASE_URL` | `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres` | Your Supabase connection string from Part 1 |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Your Vercel deployment URL (update after first deploy) |
| `ENVIRONMENT` | `production` | Production environment flag |
| `RATE_LIMIT_ENABLED` | `true` | Enable API rate limiting |

**Important**: After first deployment, you'll get your Vercel URL. Come back and update `CORS_ORIGINS` with the actual URL.

### Step 4: Deploy Settings

Configure these settings in Vercel:

- **Framework Preset**: Other
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: Leave blank
- **Install Command**: `pip install -r requirements.txt`
- **Development Command**: Leave default

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for deployment to complete (~2-3 minutes)
3. You'll get a URL like `https://exposechain-abc123.vercel.app`

### Step 6: Update CORS Settings

1. Go back to Vercel project settings
2. Navigate to **Environment Variables**
3. Update `CORS_ORIGINS` with your actual Vercel URL:
   ```
   https://exposechain-abc123.vercel.app
   ```
4. Click **Save**
5. Redeploy for changes to take effect

---

## Part 3: Testing Your Deployment

### Test the API

1. Visit: `https://your-app.vercel.app/health`
   - Should return: `{"status": "healthy", ...}`

2. Visit: `https://your-app.vercel.app/api`
   - Should show API documentation

3. Visit: `https://your-app.vercel.app/`
   - Should show the ExposeChain frontend

### Test a Scan

1. Go to your deployed frontend
2. Enter a domain (e.g., `example.com`)
3. Click **"Start Scan"**
4. Verify results appear
5. Check Supabase dashboard → Table Editor → `scan_records`
6. You should see the scan record saved

---

## Part 4: Optional Configurations

### Custom Domain

1. In Vercel, go to **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed
4. Update `CORS_ORIGINS` environment variable with new domain

### Rate Limiting Adjustments

Edit `src/utils/rate_limiter.py` to adjust rate limits:
```python
@limiter.limit("10/minute")  # Change to "20/minute" for more requests
```

### Database Connection Pooling

For high traffic, consider using Supabase's connection pooling:
1. In Supabase dashboard → Settings → Database
2. Copy **Connection Pooling** URL (uses port 6543)
3. Update `DATABASE_URL` in Vercel to use pooling URL

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure all dependencies are in `requirements.txt`
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Issue: Database connection timeout

**Solution**:
1. Verify `DATABASE_URL` is correct in Vercel environment variables
2. Check Supabase project is not paused (free tier auto-pauses after 7 days inactivity)
3. Verify password doesn't contain special characters that need URL encoding

### Issue: CORS errors in browser

**Solution**:
1. Ensure `CORS_ORIGINS` includes your Vercel URL
2. Must start with `https://` (not `http://`)
3. No trailing slash
4. Redeploy after changing environment variables

### Issue: Scan not saving to database

**Solution**:
1. Check Vercel function logs (Vercel dashboard → Deployments → View Function Logs)
2. Verify database migration ran successfully in Supabase
3. Check table name is `scan_records` (not `scan_history`)

---

## Environment Variables Reference

Complete list of environment variables:

```bash
# Required
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
CORS_ORIGINS=https://your-app.vercel.app

# Optional
ENVIRONMENT=production
DEBUG=False
RATE_LIMIT_ENABLED=true
GEOIP_DB_PATH=./data/GeoLite2-City.mmdb
```

---

## Monitoring & Maintenance

### Monitor Database Usage

1. Supabase dashboard → Reports
2. Check database size (free tier: 500MB)
3. Check row count in `scan_records`

### Monitor API Usage

1. Vercel dashboard → Analytics
2. Check function invocations
3. Check bandwidth usage
4. Free tier: 100GB bandwidth/month

### Clean Old Scans

To keep database small, periodically delete old scans:

```sql
-- Delete scans older than 30 days
DELETE FROM scan_records
WHERE created_at < NOW() - INTERVAL '30 days';
```

Run this in Supabase SQL Editor monthly.

---

## Scaling Considerations

### When you need to upgrade:

**Supabase Free Tier Limits:**
- 500MB database size
- 2GB bandwidth/month
- 50,000 monthly active users

**Vercel Free Tier Limits:**
- 100GB bandwidth/month
- 100 hours of serverless function execution/month

**Solutions:**
1. **Supabase Pro** ($25/month) - 8GB database, unlimited bandwidth
2. **Vercel Pro** ($20/month) - 1TB bandwidth, unlimited functions
3. **Self-hosted** - Use Render.com for backend + separate database

---

## Success! 🎉

Your ExposeChain platform is now deployed with:
- ✅ Supabase PostgreSQL database
- ✅ Vercel serverless functions (backend)
- ✅ Vercel static hosting (frontend)
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Auto-scaling

**Next Steps:**
- Share your deployment URL
- Monitor usage in Vercel and Supabase dashboards
- Consider setting up custom domain
- Add monitoring/alerting for errors

For issues or questions, check:
- Vercel function logs
- Supabase logs
- Browser developer console
