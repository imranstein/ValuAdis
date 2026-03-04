# ValuAdis Web Application

Ethiopian Property Valuation Platform - Built with Vue.js 3 + Nuxt.js

## 🇪🇹 Features

- **Ethiopian Compliance**: Proclamation 1365/2025 compliant (25% taxable value)
- **Bilingual Support**: English and Amharic (አማርኛ)
- **Property Management**: Full CRUD operations with GPS boundary drawing
- **Valuation System**: Automated calculations with Ethiopian municipality rates
- **Analytics Dashboard**: Market insights and ML predictions
- **Audit & Compliance**: Real-time compliance monitoring
- **Responsive Design**: Mobile-first, accessible (WCAG AA)

## 🚀 Quick Start

### Prerequisites

- Node.js 20.17.0 or higher
- npm 10.8.2 or higher
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install --legacy-peer-deps

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at http://localhost:3000

## 📁 Project Structure

```
app/
├── assets/          # CSS, images, fonts
├── components/      # Vue components
│   ├── common/      # Shared components
│   ├── property/    # Property-related components
│   ├── map/         # Leaflet map components
│   ├── valuation/   # Valuation components
│   └── analytics/   # Analytics components
├── layouts/         # Application layouts
├── pages/           # Route pages
├── stores/          # Pinia state management
├── services/        # API services
├── middleware/      # Route middleware
├── types/           # TypeScript types
├── locales/         # i18n translations
└── utils/           # Utility functions
```

## 🎨 Ethiopian Design System

### Color Palette

- **Ethiopian Green**: `#078160` (Primary)
- **Addis Ababa Blue**: `#1E3A8A` (Secondary)
- **Dire Dawa Orange**: `#EA580C` (Accent)
- **Mekelle Teal**: `#0F766E` (Supporting)

### Typography

- **Font Family**: Inter (supports Ge'ez script)
- **Letter Spacing**: 0.05em for Amharic text

## 🌍 Ethiopian Municipalities

- Addis Ababa (አዲስ አበባ)
- Bahir Dar (ባህር ዳር)
- Mekelle (መቐለ)
- Hawassa (ሐዋሳ)
- Dire Dawa (ድሬ ዳዋ)
- Gondar (ጎንደር)
- Jimma (ጅማ)
- Adama (አዳማ)

## 📱 Available Scripts

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run preview          # Preview production build

# Testing
npm run test             # Run unit tests
npm run test:e2e         # Run E2E tests
npm run test:coverage    # Generate coverage report

# Code Quality
npm run lint             # Lint code
npm run lint:fix         # Fix linting issues
npm run typecheck        # TypeScript type checking
```

## 🔐 Authentication

Default test credentials:
- Email: `admin@valuadis.com`
- Password: `password123`

## 🗺️ Map Integration

- **Library**: Leaflet.js with Leaflet Draw
- **Default Center**: Addis Ababa (9.0320°N, 38.7578°E)
- **Features**: GPS boundary drawing, area calculation, property clustering

## 📊 API Integration

Backend API endpoints:
- **Base URL**: http://localhost:8000
- **Health**: `/api/v1/health/*`
- **Auth**: `/api/v1/auth/*`
- **Properties**: `/api/v1/properties/*`
- **Valuations**: `/api/v1/valuations/*`
- **Analytics**: `/api/v1/analytics/*`
- **Audit**: `/api/v1/audit/*`

## 🧪 Testing

### Unit Tests (Vitest)
```bash
npm run test
```

### E2E Tests (Playwright)
```bash
npm run test:e2e
```

### Coverage Target
- Frontend: 70%+

## 🌐 Internationalization

Supported languages:
- **English** (en)
- **Amharic** (am) - አማርኛ

Change language in the application header dropdown.

## 📦 Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t valuadis-web .

# Run container
docker run -p 3000:3000 valuadis-web
```

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NUXT_PUBLIC_API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `NUXT_PUBLIC_MAP_DEFAULT_LAT` | Map default latitude | `9.0320` |
| `NUXT_PUBLIC_MAP_DEFAULT_LNG` | Map default longitude | `38.7578` |
| `NUXT_PUBLIC_DEFAULT_LANGUAGE` | Default language | `en` |

## 📄 License

Proprietary - ValuAdis Platform

## 🤝 Support

For support, contact: support@valuadis.et
