# ValuAdis - Ethiopian Property Valuation Platform

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)
[![Flutter](https://img.shields.io/badge/flutter-3.x-blue.svg)](https://flutter.dev/)

**ValuAdis** is a B2G (Business-to-Government) GovTech SaaS platform enabling licensed property valuers in Ethiopia to conduct digital property assessments compliant with **Proclamation 1365/2025**.

---

## 🌟 Features

- 🗺️ **GIS Boundary Mapping**: GPS-based property boundary capture with automatic area calculation
- 📊 **Automated Valuation**: Market value calculation with 25% taxable value computation
- 📄 **Compliance Certificates**: Proclamation 1365/2025 compliant PDF generation with QR verification
- 📱 **Offline-First Mobile**: 7-day offline capability for field work in low-connectivity areas
- 💳 **Flexible Pricing**: 5,000 ETB/month SaaS + 50 ETB per certificate (1-month free demo)
- 🇪🇹 **Data Sovereignty**: 100% Ethiopian hosting (Raxio Tier III data center)

---

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 + PostGIS 3.3
- **Caching**: Redis 7.x
- **Geospatial**: Shapely, GeoPandas
- **PDF Generation**: ReportLab
- **Containerization**: Docker + Docker Compose

### Frontend (Web)
- **Framework**: Vue.js 3 (Composition API)
- **Meta-framework**: Nuxt.js 3 (SSR/SSG)
- **State Management**: Pinia
- **UI Components**: PrimeVue
- **Maps**: Leaflet.js + OpenStreetMap

### Mobile
- **Framework**: Flutter 3.x (cross-platform)
- **Local Storage**: SQLite + Hive
- **State Management**: BLoC pattern
- **Maps**: flutter_map + OpenStreetMap

### DevOps
- **Hosting**: Yegara.com (Standard VPS) → Raxio Tier III (scale)
- **Architecture**: Modular Monolith → Microservices (when needed)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry + UptimeRobot
- **Deployment**: Docker Compose + Nginx

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Flutter 3.x (for mobile development)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/ValuAdis.git
cd ValuAdis

# Start all services with Docker Compose
docker-compose up -d

# Services will be available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - API Documentation: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Production Deployment

For production deployment on Yegara.com, see the [Deployment Guide](./DEPLOYMENT_README.md).

```bash
# Quick production deployment
git clone https://github.com/yourusername/ValuAdis.git
cd ValuAdis
cp .env.production .env
# Edit .env with production values
./scripts/deploy.sh
```

### Backend Setup (Without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (Without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

### Mobile Setup

```bash
cd mobile

# Get Flutter dependencies
flutter pub get

# Run on emulator/device
flutter run

# Run tests
flutter test
```

---

## 📁 Project Structure

```
ValuAdis/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── services/    # Business logic
│   │   ├── repositories/# Data access
│   │   └── core/        # Security, config
│   ├── tests/           # Backend tests
│   └── requirements.txt
│
├── frontend/            # Vue.js + Nuxt.js web app
│   ├── components/      # Vue components
│   ├── pages/           # Nuxt pages
│   ├── stores/          # Pinia stores
│   ├── composables/     # Vue composables
│   └── package.json
│
├── mobile/              # Flutter mobile app
│   ├── lib/
│   │   ├── presentation/# Screens & widgets
│   │   ├── data/        # Models & repositories
│   │   ├── services/    # Business logic
│   │   └── core/        # Constants & utils
│   ├── test/            # Mobile tests
│   └── pubspec.yaml
│
├── Docs/                # Comprehensive documentation
│   ├── SRS/             # Software requirements
│   ├── Architecture/    # System architecture
│   ├── Guidelines/      # Development guidelines
│   ├── Timeline/        # Project timeline
│   └── Memory-Bank/     # Project context
│
└── docker-compose.yml   # Docker orchestration
```

---

## 📚 Documentation

### Core Documentation
- [Master SRS](Docs/SRS/01_MASTER_SRS.md) - Complete system requirements
- [Backend Guidelines](Docs/SRS/02_BACKEND_SRS.md) - FastAPI development guide
- [Frontend Guidelines](Docs/SRS/03_FRONTEND_SRS.md) - Vue.js development guide
- [Mobile Guidelines](Docs/SRS/04_MOBILE_SRS.md) - Flutter development guide
- [Database Schema](Docs/SRS/05_DATABASE_SRS.md) - PostgreSQL + PostGIS design
- [Testing Strategy](Docs/SRS/06_TESTING_GUIDELINES.md) - TDD approach

### Architecture
- [System Architecture](Docs/Architecture/SYSTEM_ARCHITECTURE.md) - High-level design
- [Project Timeline](Docs/Timeline/PROJECT_TIMELINE.md) - 33-day development plan

### API Documentation
- Interactive API Docs: http://localhost:8000/docs (Swagger UI)
- Alternative API Docs: http://localhost:8000/redoc (ReDoc)

---

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_spatial_service.py

# View coverage report
open htmlcov/index.html
```

### Frontend Tests
```bash
cd frontend

# Run unit tests
npm run test:unit

# Run with coverage
npm run test:unit -- --coverage

# Run E2E tests
npm run test:e2e
```

### Mobile Tests
```bash
cd mobile

# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run integration tests
flutter test integration_test/
```

---

## 🔐 Security

- **Authentication**: JWT tokens (24h access, 30d refresh)
- **Password Hashing**: bcrypt (cost factor 12)
- **Data Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Rate Limiting**: 100 requests/minute per user
- **Data Sovereignty**: All data hosted in Ethiopia
- **Compliance**: Proclamation 1365/2025 adherence

---

## 🌍 Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/valuadis
REDIS_URL=redis://:password@localhost:6379/0
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# M-Pesa Configuration
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@valuadis.et
SMTP_PASSWORD=your-password
```

### Frontend (.env)
```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

---

## 🚢 Deployment

### Production Deployment (cPanel)

```bash
# Build Docker images
docker-compose -f docker-compose.prod.yml build

# Deploy to cPanel
# (Follow cPanel Docker deployment guide)

# Run database migrations
docker-compose exec backend alembic upgrade head

# Verify deployment
curl https://valuadis.et/api/v1/health
```

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U valuadis_user valuadis > backup.sql

# Restore database
docker-compose exec -T db psql -U valuadis_user valuadis < backup.sql
```

---

## 📊 Project Timeline

**Start Date**: February 25, 2026  
**Launch Date**: March 30, 2026  
**Duration**: 33 days

### Milestones
- ✅ Week 1 (Feb 25 - Mar 3): Foundation & Documentation
- ⏳ Week 2 (Mar 4 - Mar 10): Backend Core Development
- ⏳ Week 3 (Mar 11 - Mar 17): Frontend Development
- ⏳ Week 4 (Mar 18 - Mar 24): Mobile Development
- ⏳ Week 5 (Mar 25 - Mar 30): Integration, Testing & Launch

---

## 🤝 Contributing

This is a proprietary project. Contributions are limited to authorized team members.

### Development Workflow
1. Create feature branch from `main`
2. Follow coding standards (see Guidelines)
3. Write tests (TDD approach)
4. Submit pull request
5. Pass code review
6. Merge to `main`

### Code Style
- **Backend**: Black, isort, mypy
- **Frontend**: ESLint, Prettier
- **Mobile**: Dart analyzer, effective_dart

---

## 📝 License

Proprietary - All Rights Reserved

Copyright © 2026 ValuAdis. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 📞 Contact

**Support**: support@valuadis.et  
**Sales**: sales@valuadis.et  
**Technical**: tech@valuadis.et

---

## 🙏 Acknowledgments

- **Proclamation 1365/2025**: Ethiopian Property Tax Law
- **OpenStreetMap**: Map data and tiles
- **PostGIS**: Geospatial database extension
- **FastAPI**: Modern Python web framework
- **Vue.js**: Progressive JavaScript framework
- **Flutter**: Cross-platform mobile framework

---

**Built with ❤️ in Ethiopia for Ethiopian Property Valuers**
