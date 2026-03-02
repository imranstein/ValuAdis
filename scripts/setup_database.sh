#!/bin/bash

# ValuAdis Database Setup Script
# Ethiopian Property Valuation Platform

set -e

echo "🇪🇹 Setting up ValuAdis Ethiopian Property Valuation Database..."

# Database configuration
DB_NAME="valuadis"
DB_USER="valuadis_user"
DB_PASSWORD="valuadis_2025"
DB_HOST="localhost"
DB_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Database Configuration:${NC}"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not running. Starting PostgreSQL...${NC}"
    
    # Try to start PostgreSQL (macOS with Homebrew)
    if command -v brew >/dev/null 2>&1; then
        brew services start postgresql@17 || brew services start postgresql
    else
        echo -e "${RED}❌ Please start PostgreSQL manually and run this script again.${NC}"
        exit 1
    fi
    
    # Wait for PostgreSQL to start
    echo -e "${YELLOW}⏳ Waiting for PostgreSQL to start...${NC}"
    sleep 5
    
    if ! pg_isready -h $DB_HOST -p $DB_PORT >/dev/null 2>&1; then
        echo -e "${RED}❌ Failed to start PostgreSQL. Please start it manually.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ PostgreSQL is running${NC}"

# Create database user if it doesn't exist
echo -e "${BLUE}👤 Creating database user...${NC}"
if ! psql -h $DB_HOST -p $DB_PORT -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    psql -h $DB_HOST -p $DB_PORT -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    echo -e "${GREEN}✅ User '$DB_USER' created${NC}"
else
    echo -e "${YELLOW}⚠️  User '$DB_USER' already exists${NC}"
fi

# Create database if it doesn't exist
echo -e "${BLUE}🗄️  Creating database...${NC}"
if ! psql -h $DB_HOST -p $DB_PORT -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    psql -h $DB_HOST -p $DB_PORT -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    echo -e "${GREEN}✅ Database '$DB_NAME' created${NC}"
else
    echo -e "${YELLOW}⚠️  Database '$DB_NAME' already exists${NC}"
fi

# Grant privileges
psql -h $DB_HOST -p $DB_PORT -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Enable PostGIS extension for geospatial data
echo -e "${BLUE}🗺️  Enabling PostGIS extension...${NC}"
psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;" || {
    echo -e "${YELLOW}⚠️  PostGIS not available. Install with: brew install postgis${NC}"
}

# Create Ethiopian-specific schema
echo -e "${BLUE}🇪🇹 Creating Ethiopian property schema...${NC}"
psql -h $DB_HOST -p $DB_PORT -d $DB_NAME << 'EOF'

-- Ethiopian Municipalities table
CREATE TABLE IF NOT EXISTS ethiopian_municipalities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(50) NOT NULL,
    base_rate DECIMAL(10,2) NOT NULL, -- ETB per square meter
    property_type_multiplier DECIMAL(3,2) DEFAULT 1.0,
    coordinates POINT, -- Geographic center
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property types table
CREATE TABLE IF NOT EXISTS property_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    base_multiplier DECIMAL(3,2) NOT NULL,
    description TEXT,
    ethiopian_code VARCHAR(10), -- Ethiopian property classification code
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties table with Ethiopian compliance
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    property_type_id INTEGER REFERENCES property_types(id),
    municipality_id INTEGER REFERENCES ethiopian_municipalities(id),
    area_sqm DECIMAL(10,2) NOT NULL,
    street_address TEXT,
    kebele VARCHAR(50), -- Ethiopian administrative unit
    sub_city VARCHAR(50),
    coordinates POINT, -- GPS coordinates
    land_registry_number VARCHAR(50), -- Ethiopian land registry ID
    tax_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    market_value DECIMAL(15,2),
    taxable_value DECIMAL(15,2),
    last_valuation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'pending', 'under_review'))
);

-- Valuations table with Proclamation 1365/2025 compliance
CREATE TABLE IF NOT EXISTS valuations (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    valuation_date DATE NOT NULL,
    market_value DECIMAL(15,2) NOT NULL,
    taxable_value DECIMAL(15,2) NOT NULL,
    base_rate DECIMAL(10,2) NOT NULL, -- ETB per square meter
    multiplier DECIMAL(3,2) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    municipality VARCHAR(100) NOT NULL,
    area_sqm DECIMAL(10,2) NOT NULL,
    valuation_method VARCHAR(50) DEFAULT 'market_comparison',
    compliance_status VARCHAR(20) DEFAULT 'compliant',
    proclamation_reference VARCHAR(20) DEFAULT '1365/2025',
    approved_by INTEGER,
    approved_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    CONSTRAINT valid_compliance CHECK (compliance_status IN ('compliant', 'non_compliant', 'under_review', 'exempt'))
);

-- Users table for Ethiopian system
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    organization VARCHAR(200),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    ethiopian_id VARCHAR(20), -- National ID for Ethiopian citizens
    professional_license VARCHAR(50), -- For valuers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT valid_role CHECK (role IN ('admin', 'valuator', 'user', 'viewer'))
);

-- Audit trail for compliance
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id INTEGER REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE', 'VIEW'))
);

-- Ethiopian compliance reports
CREATE TABLE IF NOT EXISTS compliance_reports (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    valuation_id INTEGER REFERENCES valuations(id),
    report_type VARCHAR(50) NOT NULL,
    proclamation_section VARCHAR(20),
    compliance_score DECIMAL(5,2),
    issues JSONB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by INTEGER REFERENCES users(id),
    file_path VARCHAR(500)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_properties_municipality ON properties(municipality_id);
CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type_id);
CREATE INDEX IF NOT EXISTS idx_properties_coordinates ON properties USING GIST(coordinates);
CREATE INDEX IF NOT EXISTS idx_valuations_property ON valuations(property_id);
CREATE INDEX IF NOT EXISTS idx_valuations_date ON valuations(valuation_date);
CREATE INDEX IF NOT EXISTS idx_municipalities_region ON ethiopian_municipalities(region);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Insert Ethiopian municipalities with official rates
INSERT INTO ethiopian_municipalities (name, region, base_rate, property_type_multiplier) VALUES
('Addis Ababa', 'Addis Ababa', 1000.00, 1.0),
('Dire Dawa', 'Dire Dawa', 800.00, 0.9),
('Mekelle', 'Tigray', 600.00, 0.8),
('Bahir Dar', 'Amhara', 550.00, 0.8),
('Adama', 'Oromia', 500.00, 0.7),
('Hawassa', 'Sidama', 450.00, 0.7),
('Gonder', 'Amhara', 400.00, 0.6),
('Jimma', 'Oromia', 350.00, 0.6),
('Jijiga', 'Somali', 320.00, 0.5),
('Harar', 'Harari', 480.00, 0.7)
ON CONFLICT (name) DO NOTHING;

-- Insert property types
INSERT INTO property_types (name, base_multiplier, description, ethiopian_code) VALUES
('Residential', 1.0, 'Residential properties including houses and apartments', 'RES'),
('Commercial', 1.2, 'Commercial properties including offices and retail', 'COM'),
('Agricultural', 0.6, 'Agricultural land and farm properties', 'AGR'),
('Industrial', 1.5, 'Industrial and manufacturing facilities', 'IND'),
('Mixed Use', 1.1, 'Properties with mixed residential and commercial use', 'MIX')
ON CONFLICT (name) DO NOTHING;

-- Create trigger for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_valuations_updated_at BEFORE UPDATE ON valuations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

EOF

echo -e "${GREEN}✅ Database schema created successfully${NC}"

# Create .env file for the application
echo -e "${BLUE}📝 Creating environment configuration...${NC}"
cat > /Users/imranabdul/Dev/Personal/ValuAdis/backend/.env << EOF
# ValuAdis Backend Environment Configuration
# Ethiopian Property Valuation Platform

# Database Configuration
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Application Configuration
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=true
ENVIRONMENT=development
API_V1_STR=/api/v1

# Ethiopian Compliance
COMPLIANCE_PROCLAMATION=1365/2025
TAXABLE_VALUE_PERCENTAGE=25.0
DEFAULT_CURRENCY=ETB

# CORS Settings
ALLOWED_HOSTS=localhost,127.0.0.1,http://localhost:3003
CORS_ORIGINS=http://localhost:3003,http://127.0.0.1:3003

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=valuadis@ethiopia.gov.et
SMTP_PASSWORD=your_smtp_password

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# Redis Configuration (Optional for caching)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/valuadis.log

# Ethiopian Government Integration
LAND_REGISTRY_API_URL=https://api.landregistry.gov.et
GIS_API_URL=https://gis.ethiopia.gov.et/api
EOF

echo -e "${GREEN}✅ Environment configuration created${NC}"

# Test database connection
echo -e "${BLUE}🔗 Testing database connection...${NC}"
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -c "SELECT version();" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 ValuAdis database setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Start the backend: cd backend && python3 -m uvicorn app.main:app --reload"
echo "2. Start the frontend: cd frontend/app && npm run dev"
echo "3. Access the application: http://localhost:3003"
echo "4. Login with demo credentials: demo@valuadis.et / demo123"
echo ""
echo -e "${BLUE}🗄️  Database Connection Info:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo -e "${YELLOW}⚠️  Save these credentials securely for future reference!${NC}"
