# SuperStatsFootball ⚽

> High-performance football statistics and prediction platform - A production-ready clone of [www.superstatsfootball.com](https://www.superstatsfootball.com)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

SuperStatsFootball is a comprehensive football statistics and prediction platform featuring:

- **Real-time Match Data**: Live stats updated every second during matches
- **Advanced Predictions**: Multiple statistical models (Poisson, Dixon-Coles, Elo, Logistic Regression)
- **ML Models**: Random Forest and XGBoost for admin users
- **Tiered Access**: 5 subscription levels with progressive feature unlocking
- **100+ Leagues**: Coverage of major football leagues worldwide
- **RESTful API**: High-performance FastAPI backend
- **Modern Frontend**: React + Tailwind CSS (coming soon)

## 📚 Documentation

For the complete build guide, see [tutorial-SuperStatsFootball.txt](tutorial-SuperStatsFootball.txt)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│          React Frontend (Tailwind)          │
│  Fixtures | Stats | Settings | Admin Panel │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          FastAPI Backend (Python)           │
│  Auth | Predictions | API-Football Sync    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│      Supabase (PostgreSQL + Realtime)      │
│  Users | Leagues | Teams | Fixtures | Stats│
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         API-Football (Data Source)          │
│  Historical | Live Stats | Fixtures         │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Supabase account (or PostgreSQL)
- API-Football API key

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/SuperStatsFootball.git
cd SuperStatsFootball
```

2. **Set up environment variables**
```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize database**
```bash
python -m app.db.init_db
# Choose option 1 to create tables
# Choose option 2 to seed initial data
```

5. **Run the development server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Using the PHP frontend locally

The PHP app in `../SuperStatsFootballw` can talk to your local FastAPI server by pointing it to the correct base URL:

1. Start the backend (`uvicorn app.main:app --reload`).
2. In the shell where you run PHP or your local web server, set `BACKEND_API_URL`:
   ```bash
   export BACKEND_API_URL=http://127.0.0.1:8000
   ```
3. Load the PHP site. The updated `config.php` reads `BACKEND_API_URL` and will call your local API instead of the remote Railway deployment.

If Supabase/Postgres isn’t reachable, the backend now falls back to a local SQLite database and automatically seeds demo fixtures so the statistics pages still render useful data.

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## 📊 Features

### Subscription Tiers

| Tier | Price | Leagues | Models | Features |
|------|-------|---------|--------|----------|
| Free | $0 | 3 | Poisson | Basic stats, next round only |
| Starter | $9.99 | 10 | Poisson, Dixon-Coles | Live stats, 2 seasons history |
| Pro | $19.99 | 25 | + Elo | 5 seasons, advanced filters |
| Premium | $39.99 | 50+ | + Logistic | 10 seasons, API access |
| Ultimate | $99.99 | 100+ | + ML models | All features, admin panel |

### Statistical Models

- **Poisson Distribution**: Classic goal prediction model
- **Dixon-Coles**: Enhanced Poisson with low-score correlation
- **Elo Rating**: Chess-inspired team strength system
- **Logistic Regression**: Multi-factor match outcome prediction
- **Random Forest**: ML ensemble for complex patterns (Admin)
- **XGBoost**: Gradient boosting for highest accuracy (Admin)

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance async API framework
- **SQLAlchemy**: ORM with async support
- **Pydantic**: Data validation
- **JWT**: Authentication
- **Stripe**: Payment processing
- **Redis**: Caching layer

### Data Science
- **NumPy & SciPy**: Numerical computing
- **Pandas**: Data manipulation
- **Scikit-learn**: ML models
- **XGBoost**: Gradient boosting

### Database
- **Supabase**: Managed PostgreSQL + Realtime
- **Row Level Security**: User data protection

### External APIs
- **API-Football**: Match data source
- **Stripe**: Subscription management

## 📡 API Endpoints

### Authentication
```
POST /api/v1/auth/register      # Create account
POST /api/v1/auth/login         # Login
POST /api/v1/auth/refresh       # Refresh token
```

### Fixtures
```
GET  /api/v1/fixtures           # List fixtures
GET  /api/v1/fixtures/upcoming  # Upcoming matches
GET  /api/v1/fixtures/{id}      # Fixture details
GET  /api/v1/fixtures/{id}/stats # Match statistics
```

### Predictions
```
POST /api/v1/predictions/calculate  # Generate prediction
GET  /api/v1/predictions/{id}       # Get predictions
GET  /api/v1/predictions/user/history # User history
```

### Admin
```
GET  /api/v1/admin/debug        # System stats
GET  /api/v1/admin/users        # User management
PUT  /api/v1/admin/users/{id}/tier # Update tier
POST /api/v1/admin/sync/fixtures   # Trigger sync
```

See [API Documentation](http://localhost:8000/docs) for complete reference.

## 🗂️ Project Structure

```
SuperStatsFootball/
├── backend/
│   ├── app/
│   │   ├── core/              # Config, security, dependencies
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── ml/                # Prediction models
│   │   │   ├── statistical/   # Poisson, Elo, Dixon-Coles
│   │   │   └── machine_learning/ # RF, XGBoost
│   │   ├── db/                # Database setup
│   │   └── utils/             # Helpers
│   ├── tests/                 # Unit tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/                  # React app (coming soon)
├── docker-compose.yml
├── tutorial-SuperStatsFootball.txt
└── README.md
```

## 🔐 Environment Variables

Key environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=sqlite:///./superstats.db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# API Keys
APIFOOTBALL_API_KEY=your-api-football-key
STRIPE_SECRET_KEY=sk_test_...

# Security
SECRET_KEY=your-secret-key-here
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## 📈 Database Schema

Main tables:
- **users**: User accounts and subscriptions
- **leagues**: Football leagues (Premier League, La Liga, etc.)
- **teams**: Team information
- **fixtures**: Match schedule and status
- **fixture_stats**: Live match statistics
- **fixture_scores**: Match scores
- **predictions**: Model predictions
- **team_ratings**: Elo and strength ratings

See [tutorial](tutorial-SuperStatsFootball.txt) for complete schema.

## 🚢 Deployment

### Docker Production Build
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### GreenGeeks Deployment
See [tutorial section 11](tutorial-SuperStatsFootball.txt#part-11-docker--deployment) for detailed deployment guide.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [API-Football](https://www.api-football.com/) for match data
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework
- [Supabase](https://supabase.com/) for database infrastructure
- Original inspiration from [SuperStatsFootball.com](https://www.superstatsfootball.com)

## 📞 Support

- Documentation: [tutorial-SuperStatsFootball.txt](tutorial-SuperStatsFootball.txt)
- Issues: [GitHub Issues](https://github.com/yourusername/SuperStatsFootball/issues)
- Email: support@superstatsfootball.com

---

**Built with ❤️ for football analytics enthusiasts**
