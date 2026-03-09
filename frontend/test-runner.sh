#!/bin/bash

# ValuAdis E2E Test Runner
# Usage: ./test-runner.sh [phase] [test-type]

set -e

PHASE=${1:-"phase1"}
TEST_TYPE=${2:-"all"}

echo "🚀 Running ValuAdis E2E Tests - Phase: $PHASE, Type: $TEST_TYPE"

# Check if services are running
echo "📋 Checking services..."
if ! curl -s http://localhost:3020/ > /dev/null; then
    echo "❌ Frontend is not running on http://localhost:3020"
    echo "Please start the frontend with: npm run dev"
    exit 1
fi

if ! curl -s http://localhost:8020/health > /dev/null; then
    echo "❌ Backend is not running on http://localhost:8020"
    echo "Please start the backend with: docker-compose up backend"
    exit 1
fi

echo "✅ Services are running"

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
