#!/bin/bash

# ValuAdis E2E Test Runner
# Usage: ./test-runner.sh [phase] [test-type]

set -e

PHASE=${1:-"phase1"}
TEST_TYPE=${2:-"all"}

echo "🚀 Running ValuAdis E2E Tests - Phase: $PHASE, Type: $TEST_TYPE"

# Check if services are running
echo "📋 Checking services..."

FRONTEND_URL="${E2E_BASE_URL:-http://127.0.0.1:${E2E_FRONTEND_PORT:-3020}}"
BACKEND_URL="${NUXT_PUBLIC_API_BASE_URL:-http://127.0.0.1:8020}"

check_service() {
  local url="$1"
  local name="$2"
  if ! curl -fsS "$url" > /dev/null; then
    echo "❌ $name is not available at $url"
    return 1
  fi
  echo "✅ $name is available at $url"
}

if [[ "${E2E_SKIP_FRONTEND_CHECK:-0}" != "1" ]]; then
  if ! check_service "$FRONTEND_URL" "Frontend"; then
    echo "Please start the frontend with: npm run dev"
    exit 1
  fi
fi

if [[ "${E2E_SKIP_BACKEND_CHECK:-0}" != "1" ]]; then
  if ! check_service "${BACKEND_URL}/health" "Backend"; then
    echo "Please start the backend with: docker-compose up backend"
    exit 1
  fi
fi
echo "✅ Services check completed"

# Run tests based on phase and type
case $PHASE in
    "phase1")
        echo "🔧 Running Phase 1: Foundation & Core Authentication Tests"
        
        case $TEST_TYPE in
            "auth")
                echo "🔐 Running Authentication Tests"
                npx playwright test tests/e2e/pages/auth.spec.ts --reporter=list
                ;;
            "navigation")
                echo "🧭 Running Navigation Tests"
                npx playwright test tests/e2e/pages/navigation.spec.ts --reporter=list
                ;;
            "responsive")
                echo "📱 Running Responsive Design Tests"
                npx playwright test tests/e2e/pages/responsive.spec.ts --reporter=list
                ;;
            "all")
                echo "🎯 Running All Phase 1 Tests"
                npx playwright test tests/e2e/pages/auth.spec.ts tests/e2e/pages/navigation.spec.ts tests/e2e/pages/responsive.spec.ts --reporter=list
                ;;
            *)
                echo "❌ Unknown test type: $TEST_TYPE"
                echo "Available types: auth, navigation, responsive, all"
                exit 1
                ;;
        esac
        ;;
    "phase2")
        echo "🔧 Running Phase 2: Core CRUD Operations Tests"
        
        case $TEST_TYPE in
            "properties")
                echo "🏠 Running Properties CRUD Tests"
                npx playwright test tests/e2e/pages/properties-crud.spec.ts --reporter=list
                ;;
            "valuations")
                echo "💰 Running Valuations CRUD Tests"
                npx playwright test tests/e2e/pages/valuations-crud.spec.ts --reporter=list
                ;;
            "users")
                echo "👥 Running Users CRUD Tests"
                npx playwright test tests/e2e/pages/users-crud.spec.ts --reporter=list
                ;;
            "all")
                echo "🎯 Running All Phase 2 Tests"
                npx playwright test tests/e2e/pages/properties-crud.spec.ts tests/e2e/pages/valuations-crud.spec.ts tests/e2e/pages/users-crud.spec.ts --reporter=list
                ;;
            *)
                echo "❌ Unknown test type: $TEST_TYPE"
                echo "Available types: properties, valuations, users, all"
                exit 1
                ;;
        esac
        ;;
    "phase3")
        echo "🔧 Phase 3: Ethiopian Compliance - Not implemented yet"
        ;;
    "phase4")
        echo "🔧 Phase 4: Advanced Workflows - Not implemented yet"
        ;;
    "phase5")
        echo "🔧 Phase 5: Cross-Browser & Mobile - Not implemented yet"
        ;;
    *)
        echo "❌ Unknown phase: $PHASE"
        echo "Available phases: phase1, phase2, phase3, phase4, phase5"
        exit 1
        ;;
esac

echo "📊 Test Results:"
echo "View detailed report: npx playwright show-report"
echo "View HTML report: open playwright-report/index.html"
