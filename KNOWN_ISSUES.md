# Known Issues & Solutions

## ✅ FIXED ISSUES

### 1. AI Service Key Mismatch (FIXED)
**Problem:** AI service returned `risk_score` but frontend expected `overall_risk_score`
**Solution:** Updated AI service to return correct keys matching frontend
**Status:** ✅ Fixed

## ⚠️ POTENTIAL ISSUES TO WATCH

### 1. Rate Limiting on Free APIs
**Issue:** ip-api.com has 45 requests/minute limit
**Impact:** If you scan many domains quickly, geolocation lookups may fail
**Solution:** 
- Cache is enabled (5 min TTL) to reduce API calls
- Consider upgrading to paid tier if needed
**Mitigation:** Built-in caching already handles this

### 2. WHOIS Queries Can Be Slow
**Issue:** Some WHOIS servers are slow or rate-limit
**Impact:** Scans may take longer for certain domains
**Solution:** 
- Cache is already enabled
- Async execution prevents blocking
**Mitigation:** Already handled

### 3. SQLite Database Concurrency
**Issue:** SQLite has limited concurrent write support
**Impact:** If many users scan simultaneously, may get "database locked" errors
**Solution:** For production, migrate to PostgreSQL or MySQL
**For Development:** This is fine

### 4. DNS Timeout Errors
**Issue:** Some domains may have slow DNS servers
**Impact:** DNS queries timeout after 5 seconds
**Solution:** This is expected behavior, handled gracefully
**Mitigation:** Errors are logged and returned to user

### 5. SSL Certificate Verification
**Issue:** Some domains may have invalid/expired certificates
**Impact:** SSL check will fail (intentional)
**Solution:** This is a feature, not a bug - we detect bad SSL
**Mitigation:** Error handling already in place

## 🚫 THINGS THAT WILL FAIL (BY DESIGN)

### 1. Internal IPs (SSRF Protection)
**Expected Behavior:** Scanning 127.0.0.1, 192.168.x.x, 10.x.x.x will be BLOCKED
**Why:** Security feature to prevent Server-Side Request Forgery
**Error Message:** "Target resolves to an internal/private IP address"

### 2. Invalid Domains
**Expected Behavior:** Invalid domain names will be rejected
**Why:** Input validation
**Error Message:** "Invalid target format"

### 3. Rate Limit Exceeded
**Expected Behavior:** After 10 scans/minute, requests will be blocked
**Why:** Rate limiting to prevent abuse
**Error Message:** "Rate limit exceeded"

## 🔧 MAINTENANCE RECOMMENDATIONS

### 1. Database Cleanup
The SQLite database will grow over time. To clean old scans:
```python
# Add this as a scheduled task or admin endpoint
from src.models.database import SessionLocal, ScanRecord
from datetime import datetime, timedelta

db = SessionLocal()
cutoff = datetime.utcnow() - timedelta(days=30)
db.query(ScanRecord).filter(ScanRecord.created_at < cutoff).delete()
db.commit()
```

### 2. Log Rotation
Logs will accumulate in console. For production:
- Use log file rotation (add RotatingFileHandler)
- Or send logs to external service (Sentry, CloudWatch, etc.)

### 3. Cache Tuning
Current cache: 128 items, 5-minute TTL
- Increase maxsize if you have memory
- Adjust TTL based on your needs

## 📊 MONITORING RECOMMENDATIONS

Watch for:
1. High error rates in logs
2. Slow response times (> 5 seconds)
3. Database file size growth
4. Rate limit hits

## 🎯 PRODUCTION READINESS CHECKLIST

Before deploying to production:
- [ ] Replace SQLite with PostgreSQL/MySQL
- [ ] Set up proper CORS origins in .env
- [ ] Add API authentication/API keys
- [ ] Set up log aggregation (ELK, Splunk, etc.)
- [ ] Add monitoring (Prometheus, New Relic, etc.)
- [ ] Set up SSL certificate for the server
- [ ] Add rate limiting per IP (not just global)
- [ ] Set up automated database backups
- [ ] Add health check monitoring
- [ ] Review and restrict CORS_ORIGINS
- [ ] Add environment-based configuration
- [ ] Set up CI/CD pipeline
- [ ] Add automated tests

## 💡 TIPS

1. **Testing SSRF Protection:**
   ```bash
   curl -X POST http://localhost:8000/api/scan \
     -H "Content-Type: application/json" \
     -d '{"target": "127.0.0.1", "scan_type": "quick"}'
   # Should return error about internal IP
   ```

2. **Viewing Logs:**
   - Logs are printed to console
   - Level: INFO for normal operations, ERROR for failures

3. **Database Location:**
   - File: `exposechain.db` in project root
   - View with: `sqlite3 exposechain.db`

## ✅ WHAT'S ALREADY PROTECTED

✅ SSRF attacks (internal IP blocking)
✅ Rate limiting (prevents abuse)
✅ Input validation (prevents injection)
✅ Error message sanitization (no internal details leaked)
✅ CORS restrictions (only approved origins)
✅ Caching (reduces external API calls)
✅ Async execution (prevents blocking)
✅ Logging (tracks all operations)
✅ Database persistence (scan history)

