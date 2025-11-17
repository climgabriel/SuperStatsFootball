# SuperStatsFootball - Production Deployment Checklist

## 🎯 Pre-Deployment Checklist

### 1. Code Quality ✅
- [x] All 22 ML models integrated into PredictionPipeline
- [x] Statistical models (Poisson, Dixon-Coles, Elo) working
- [x] Feature engineering extracting 70 features
- [x] Tier-based access control implemented
- [ ] All unit tests passing
- [ ] Code reviewed and optimized
- [ ] No debug print statements
- [ ] Proper error handling everywhere

### 2. ML Models 🤖
- [ ] **Train all 22 ML models** (CRITICAL!)
  ```bash
  python backend/scripts/train_ml_models.py --seasons 3
  ```
- [ ] Verify models saved to `backend/models/trained/`
- [ ] Test predictions with trained models
- [ ] Verify tier-based model access
- [ ] Benchmark prediction performance

### 3. Database 🗄️
- [ ] PostgreSQL database provisioned (Supabase/Railway)
- [ ] Database migrations run
- [ ] All tables created
- [ ] Sample data loaded (optional)
- [ ] Database backups configured
- [ ] Connection pooling configured

### 4. Environment Variables 🔐
- [ ] `DATABASE_URL` set (PostgreSQL connection string)
- [ ] `SECRET_KEY` generated (32+ characters)
- [ ] `APIFOOTBALL_API_KEY` set (for data sync)
- [ ] `STRIPE_SECRET_KEY` set (for payments)
- [ ] `SENTRY_DSN` set (for monitoring)
- [ ] `REDIS_URL` set (optional, for caching)
- [ ] `CORS_ORIGINS` set (your frontend URLs)
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`

### 5. Security 🔒
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Rate limiting enabled
- [ ] SQL injection protection verified
- [ ] XSS protection verified
- [ ] JWT tokens using secure keys
- [ ] Passwords hashed with bcrypt
- [ ] Sensitive data encrypted at rest

### 6. Performance ⚡
- [ ] Redis caching enabled (optional)
- [ ] Database queries optimized
- [ ] Indexes created on frequently queried columns
- [ ] API response time < 1s for predictions
- [ ] Connection pooling configured
- [ ] Static files cached
- [ ] Gzip compression enabled

### 7. Monitoring 📊
- [ ] Sentry error tracking configured
- [ ] Log aggregation setup
- [ ] Uptime monitoring (UptimeRobot/Pingdom)
- [ ] Performance monitoring (New Relic/DataDog)
- [ ] Database metrics tracking
- [ ] API endpoint metrics

### 8. Testing 🧪
- [ ] Health endpoint returns 200
- [ ] Registration works
- [ ] Login works
- [ ] Predictions generated successfully
- [ ] All tiers return correct number of models
- [ ] Combined endpoint works
- [ ] Load testing passed (100+ concurrent users)

### 9. Deployment 🚀
- [ ] Code committed to production branch
- [ ] Railway/Render deployment configured
- [ ] Build succeeds
- [ ] Runtime logs show no errors
- [ ] Healthcheck passes
- [ ] API documentation accessible (if enabled)

### 10. Post-Deployment ✅
- [ ] Verify all endpoints work
- [ ] Test user flows
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify database connections stable
- [ ] Monitor resource usage (CPU/Memory)
- [ ] Set up alerts for errors

---

## 🚀 Deployment Commands

### Local Testing
```bash
# 1. Set up environment
cd backend
cp .env.production.example .env
# Edit .env with your values

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train ML models (IMPORTANT!)
python scripts/train_ml_models.py --seasons 3

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Railway Deployment
```bash
# 1. Set environment variables in Railway dashboard
# 2. Push to main branch
git push origin main

# 3. Monitor deployment logs
railway logs

# 4. Verify healthcheck
curl https://your-app.up.railway.app/health
```

### Docker Deployment
```bash
# 1. Build image
docker build -t superstatsfootball .

# 2. Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env.production \
  superstatsfootball

# 3. Check logs
docker logs -f <container-id>
```

---

## 📊 Model Training Status

| Tier | Models | Status | Command to Train |
|------|--------|--------|------------------|
| Free | 4 ML + 3 Statistical = 7 | ⏳ | `python scripts/train_ml_models.py` |
| Starter | 9 ML + 3 Statistical = 12 | ⏳ | `python scripts/train_ml_models.py` |
| Pro | 15 ML + 3 Statistical = 18 | ⏳ | `python scripts/train_ml_models.py` |
| Premium | 20 ML + 3 Statistical = 23 | ⏳ | `python scripts/train_ml_models.py` |
| Ultimate | 22 ML + 3 Statistical = 25 | ⏳ | `python scripts/train_ml_models.py` |

**⚠️ CRITICAL:** Models MUST be trained before production deployment!

Without trained models:
- ✅ Statistical models (Poisson, Dixon-Coles, Elo) will work
- ❌ ML models will be skipped (graceful fallback)

With trained models:
- ✅ ALL 25 models work perfectly
- ✅ Users get tier-appropriate predictions
- ✅ Better accuracy and confidence scores

---

## 🔍 Verification Scripts

### Check ML Models Status
```bash
python -c "
from app.services.ml_prediction_service import MLPredictionService
from app.db.session import SessionLocal

db = SessionLocal()
service = MLPredictionService(db)
status = service.get_training_status()

for model, info in status.items():
    print(f'{model}: {'✅' if info['trained'] else '❌'} {'TRAINED' if info['trained'] else 'NOT TRAINED'}')
"
```

### Test Prediction for All Tiers
```bash
python -c "
from app.services.prediction_pipeline import PredictionPipeline
from app.db.session import SessionLocal

db = SessionLocal()
pipeline = PredictionPipeline(db, use_ml_models=True)

tiers = ['free', 'starter', 'pro', 'premium', 'ultimate']
fixture_id = 1  # Use actual fixture ID

for tier in tiers:
    result = pipeline.generate_prediction(fixture_id, user_tier=tier)
    print(f'{tier.upper()}: {result['total_models']} models ({result['ml_models']} ML + {result['statistical_models']} statistical)')
"
```

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ Healthcheck returns HTTP 200
- ✅ Free tier gets 7 model predictions (3 statistical + 4 ML)
- ✅ Ultimate tier gets 25 model predictions (3 statistical + 22 ML)
- ✅ Predictions return in < 2 seconds
- ✅ No errors in logs
- ✅ Database connections stable
- ✅ Memory usage < 2GB
- ✅ CPU usage < 50% average
- ✅ All authentication flows work
- ✅ Combined endpoint returns fixtures with odds + predictions

---

## 🚨 Common Issues & Solutions

### Issue: ML models not working
**Symptoms:** Only 3 models in predictions (statistical only)

**Solutions:**
1. Check if models are trained:
   ```bash
   ls -la backend/models/trained/
   ```
2. Train models if missing:
   ```bash
   python backend/scripts/train_ml_models.py
   ```
3. Check logs for ML service initialization errors

### Issue: Database connection fails
**Symptoms:** Health check fails, "database connection" errors

**Solutions:**
1. Verify `DATABASE_URL` is correct
2. Check database server is running
3. Verify network connectivity
4. Check database credentials
5. Ensure database accepts connections from your IP

### Issue: Slow predictions
**Symptoms:** Requests taking > 5 seconds

**Solutions:**
1. Enable Redis caching
2. Reduce `LOOKBACK_MATCHES` from 10 to 5
3. Add database indexes
4. Use connection pooling
5. Consider async prediction processing

### Issue: Out of memory
**Symptoms:** Container/process crashes, OOM errors

**Solutions:**
1. Increase memory allocation (min 2GB recommended)
2. Reduce number of ML models in lower tiers
3. Implement lazy loading for models
4. Add pagination to API responses
5. Clear old predictions from database

---

## 📞 Support

If you encounter issues:
1. Check logs first: `railway logs` or `docker logs`
2. Review this checklist
3. Check DEPLOYMENT_GUIDE.md
4. Check TROUBLESHOOTING.md
5. Open GitHub issue with logs

---

**Last Updated:** 2025-11-17
**Version:** 1.0.0 (25 Models Production Ready)
**Status:** Ready for Deployment (after model training)
