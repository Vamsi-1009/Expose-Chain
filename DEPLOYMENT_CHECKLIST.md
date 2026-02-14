# ExposeChain Deployment Checklist

Use this checklist to ensure a smooth deployment to Supabase + Vercel.

## Pre-Deployment Checklist

- [ ] Code committed and pushed to GitHub
- [ ] All dependencies in `requirements.txt` are correct
- [ ] `.env.example` reviewed and understood

---

## Supabase Setup (15 minutes)

### Account & Project
- [ ] Created Supabase account at https://supabase.com
- [ ] Created new project named "exposechain"
- [ ] Saved database password securely
- [ ] Project provisioned successfully

### Database Migration
- [ ] Opened SQL Editor in Supabase dashboard
- [ ] Copied contents of `migrations/supabase_migration.sql`
- [ ] Ran migration successfully (no errors)
- [ ] Verified `scan_records` table exists in Table Editor

### Connection String
- [ ] Navigated to Settings → Database
- [ ] Copied PostgreSQL connection string (URI format)
- [ ] Replaced `[YOUR-PASSWORD]` with actual password
- [ ] Saved connection string (you'll need it for Vercel)

**Your Connection String Format:**
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

---

## Vercel Deployment (10 minutes)

### Account & Project Import
- [ ] Created Vercel account at https://vercel.com
- [ ] Connected GitHub account
- [ ] Imported ExposeChain repository
- [ ] Vercel detected Python project

### Environment Variables Setup
Add these in Vercel project settings → Environment Variables:

- [ ] `DATABASE_URL` = Your Supabase connection string
- [ ] `CORS_ORIGINS` = `https://your-app.vercel.app` (temporary, will update)
- [ ] `ENVIRONMENT` = `production`
- [ ] `RATE_LIMIT_ENABLED` = `true`

### Initial Deployment
- [ ] Clicked "Deploy" button
- [ ] Deployment completed successfully
- [ ] Received Vercel deployment URL
- [ ] Copied deployment URL (e.g., `https://exposechain-abc123.vercel.app`)

### Update CORS Settings
- [ ] Went back to Vercel → Settings → Environment Variables
- [ ] Updated `CORS_ORIGINS` with actual Vercel URL
- [ ] Saved changes
- [ ] Redeployed (Vercel → Deployments → Redeploy)

---

## Testing Checklist (5 minutes)

### API Health
- [ ] Visited `https://your-app.vercel.app/health`
- [ ] Received `{"status": "healthy"}` response
- [ ] Visited `https://your-app.vercel.app/api`
- [ ] Received API documentation

### Frontend
- [ ] Visited `https://your-app.vercel.app/`
- [ ] Frontend loaded correctly
- [ ] No console errors in browser DevTools

### Scan Functionality
- [ ] Entered test domain (e.g., `example.com`)
- [ ] Clicked "Start Scan" button
- [ ] Scan completed successfully
- [ ] Results displayed correctly
- [ ] AI analysis section shows risk score

### Database Verification
- [ ] Opened Supabase → Table Editor → scan_records
- [ ] Verified scan record was saved
- [ ] Checked all JSON columns populated correctly

---

## Post-Deployment (Optional)

### Custom Domain
- [ ] Purchased domain name
- [ ] Added domain in Vercel → Settings → Domains
- [ ] Updated DNS records as instructed
- [ ] Updated `CORS_ORIGINS` with custom domain
- [ ] Redeployed

### Monitoring Setup
- [ ] Bookmarked Vercel dashboard
- [ ] Bookmarked Supabase dashboard
- [ ] Checked Vercel Analytics
- [ ] Checked Supabase Reports

### Documentation
- [ ] Updated README.md with deployment URL
- [ ] Documented any custom configurations
- [ ] Shared deployment URL with team

---

## Troubleshooting Reference

### Common Issues:

**Issue**: Module not found errors during Vercel build
- **Fix**: Ensure all packages in `requirements.txt`

**Issue**: Database connection timeout
- **Fix**: Verify `DATABASE_URL` is correct, check Supabase project not paused

**Issue**: CORS errors in browser
- **Fix**: Ensure `CORS_ORIGINS` matches Vercel URL exactly (with `https://`, no trailing slash)

**Issue**: Scans not saving to database
- **Fix**: Check Vercel function logs, verify migration ran in Supabase

**Issue**: 500 Internal Server Error
- **Fix**: Check Vercel → Deployments → View Function Logs for detailed errors

---

## Quick Links

Once deployed, bookmark these:

- **Frontend**: `https://your-app.vercel.app`
- **API Docs**: `https://your-app.vercel.app/api`
- **Health Check**: `https://your-app.vercel.app/health`
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Supabase Dashboard**: https://supabase.com/dashboard/projects

---

## Success Criteria ✅

Your deployment is successful when:

- ✅ Health endpoint returns 200 OK
- ✅ Frontend loads without errors
- ✅ Test scan completes successfully
- ✅ Scan appears in Supabase database
- ✅ AI analysis displays risk scores
- ✅ No CORS errors in browser console

---

**Deployment Complete!** 🎉

Your ExposeChain platform is now live with:
- Supabase PostgreSQL database
- Vercel serverless deployment
- Global CDN
- Automatic HTTPS
- Auto-scaling infrastructure

For detailed instructions, see: `DEPLOYMENT_GUIDE.md`
