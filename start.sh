#!/bin/bash

# Ethiopian Property & Vehicle Valuation Platform - Quick Start Script
# This script starts both frontend and backend servers

echo "🇪🇹 Starting Ethiopian Property & Vehicle Valuation Platform..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ Node.js/npm is required but not installed.${NC}"
    exit 1
fi

if ! command_exists uvicorn; then
    echo -e "${YELLOW}⚠️  Installing uvicorn...${NC}"
    pip3 install uvicorn
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Check if ports are available
if port_in_use 8020; then
    echo -e "${YELLOW}⚠️  Port 8020 (backend) is already in use. Please stop the existing service.${NC}"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 (frontend) is already in use. Please stop the existing service.${NC}"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Backend Server
echo -e "${BLUE}Starting Backend Server...${NC}"
echo "Backend will be available at: http://localhost:8020"
echo "API Documentation: http://localhost:8020/docs"
echo ""

# Start backend in background
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8020 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
    exit 1
fi

# Start Frontend Server
echo ""
echo -e "${BLUE}Starting Frontend Server...${NC}"
echo "Frontend will be available at: http://localhost:3000"
echo ""

# Start frontend in background
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}❌ Frontend server failed to start${NC}"
    # Kill backend if frontend failed
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Display success message
echo ""
echo -e "${GREEN}🎉 Ethiopian Property & Vehicle Valuation Platform is now running!${NC}"
echo ""
echo -e "${BLUE}📱 Access the platform:${NC}"
echo -e "   • Main Dashboard: ${YELLOW}http://localhost:3000${NC}"
echo -e "   • Vehicle Valuations: ${YELLOW}http://localhost:3000/vehicles${NC}"
echo -e "   • Property Map: ${YELLOW}http://localhost:3000/map${NC}"
echo -e "   • API Documentation: ${YELLOW}http://localhost:8020/docs${NC}"
echo ""
echo -e "${BLUE}🧪 Test the system:${NC}"
echo -e "   • Try VIN decoding with: ${YELLOW}1HGBH41JXMN109186${NC}"
echo -e "   • Explore Ethiopian property map"
echo -e "   • Create a vehicle valuation with Ethiopian market factors"
echo ""
echo -e "${BLUE}🛑 Stop the servers:${NC}"
echo -e "   • Press ${YELLOW}Ctrl+C${NC} in this terminal"
echo -e "   • Or run: ${YELLOW}./stop.sh${NC}"
echo ""

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Ethiopian Property & Vehicle Valuation Platform..."

# Kill processes by port
echo "Stopping backend server (port 8020)..."
lsof -ti:8020 | xargs kill -9 2>/dev/null

echo "Stopping frontend server (port 3000)..."
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ All servers stopped"
EOF

chmod +x stop.sh

echo -e "${GREEN}✅ Stop script created: ./stop.sh${NC}"
echo ""

# Wait for user to stop
echo -e "${BLUE}Press Ctrl+C to stop all servers, or run ./stop.sh in another terminal${NC}"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    
    # Kill the background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Also kill by port to be sure
    lsof -ti:8020 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    
    echo -e "${GREEN}✅ All servers stopped${NC}"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Keep script running
while true; do
    sleep 1
done
