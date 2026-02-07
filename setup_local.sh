#!/bin/bash

# PillGuide Local Setup Script

echo "🏥 PillGuide Local Setup Script"
echo "================================"
echo ""
echo "This script will help you set up PillGuide locally."
echo ""
echo "Prerequisites:"
echo "- Python 3.11+"
echo "- Node.js 18+"
echo "- MongoDB"
echo "- Google Gemini API Key"
echo ""
read -p "Press Enter to continue..."

# Create backend .env template
cat > backend/.env.example << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=pillguide_local
CORS_ORIGINS=http://localhost:3000
GEMINI_API_KEY=your_google_gemini_api_key_here
EOF

# Create frontend .env template
cat > frontend/.env.example << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=0
EOF

echo "✅ Created .env.example files"
echo ""
echo "Next steps:"
echo "1. Get your Google Gemini API key from: https://aistudio.google.com/app/apikey"
echo "2. Copy backend/.env.example to backend/.env and add your API key"
echo "3. Copy frontend/.env.example to frontend/.env"
echo "4. Follow instructions in LOCAL_SETUP.md"
echo ""
echo "Quick start:"
echo "  cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
echo "  cd frontend && yarn install"
