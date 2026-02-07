# PillGuide - Local Setup Guide

## 🏠 Running PillGuide Locally on Your Desktop

### Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** and npm/yarn installed
3. **MongoDB** installed and running
4. **Google Gemini API Key** (get from https://aistudio.google.com/app/apikey)

---

## 📋 Step-by-Step Setup

### 1. Get Your Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (starts with `AIza...`)

⚠️ **Important**: Keep this key secure and never commit it to version control!

---

### 2. Install MongoDB

#### On macOS:
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

#### On Ubuntu/Debian:
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### On Windows:
1. Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Install and start MongoDB service

#### Verify MongoDB is running:
```bash
mongosh
# Should connect successfully
```

---

### 3. Backend Setup

```bash
# Navigate to backend directory
cd /app/backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Create `.env` file** in `/app/backend/`:
```bash
# /app/backend/.env
MONGO_URL=mongodb://localhost:27017
DB_NAME=pillguide_local
CORS_ORIGINS=http://localhost:3000
GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY_HERE
```

**Replace `YOUR_GOOGLE_GEMINI_API_KEY_HERE` with your actual API key!**

**Start Backend Server:**
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

✅ Backend should be running at: http://localhost:8001

---

### 4. Frontend Setup

**Open a new terminal window:**

```bash
# Navigate to frontend directory
cd /app/frontend

# Install dependencies
yarn install
# or if you prefer npm:
npm install
```

**Update `.env` file** in `/app/frontend/`:
```bash
# /app/frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=0
```

**Start Frontend Server:**
```bash
yarn start
# or with npm:
npm start
```

✅ Frontend should be running at: http://localhost:3000

---

## 🧪 Testing the Application

### 1. Test Backend API

Open browser or use curl:
```bash
curl http://localhost:8001/api/
```

Expected response:
```json
{"message": "PillGuide API - Multi-Language Prescription System"}
```

### 2. Test Frontend

Open browser: http://localhost:3000

You should see the PillGuide homepage!

### 3. Test Prescription Upload

1. Click "Upload Prescription"
2. Select a prescription image
3. Choose your preferred language
4. Click "Analyze Prescription"
5. View extracted medications with explanations

---

## 📁 Project Structure

```
Your Local Directory/
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── .env              # Backend environment variables
│   └── venv/             # Python virtual environment
│
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── pages/
    │   └── components/
    ├── package.json
    ├── .env              # Frontend environment variables
    └── node_modules/
```

---

## 🔧 Troubleshooting

### Issue: "GEMINI_API_KEY not found"

**Solution**: Make sure you:
1. Created `/app/backend/.env` file
2. Added `GEMINI_API_KEY=YOUR_KEY_HERE`
3. Replaced `YOUR_KEY_HERE` with actual API key
4. Restarted backend server

### Issue: "MongoDB connection failed"

**Solution**: 
```bash
# Check if MongoDB is running
mongosh

# If not running, start it:
# macOS:
brew services start mongodb-community
# Ubuntu:
sudo systemctl start mongodb
# Windows:
net start MongoDB
```

### Issue: "Module not found" errors

**Solution**:
```bash
# Backend:
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend:
cd frontend
rm -rf node_modules
yarn install
```

### Issue: "CORS errors" in browser

**Solution**: Make sure backend `.env` has:
```
CORS_ORIGINS=http://localhost:3000
```

### Issue: "Port already in use"

**Solution**:
```bash
# Find process on port 8001:
lsof -ti:8001 | xargs kill -9

# Find process on port 3000:
lsof -ti:3000 | xargs kill -9
```

---

## 🚀 Development Workflow

### Making Changes

**Backend changes:**
- Edit `server.py`
- Server auto-reloads (with `--reload` flag)
- Check terminal for errors

**Frontend changes:**
- Edit files in `src/`
- Browser auto-refreshes
- Check browser console for errors

### Viewing Logs

**Backend logs:**
- Check terminal where you ran `uvicorn`

**Frontend logs:**
- Check terminal where you ran `yarn start`
- Check browser DevTools console (F12)

---

## 📊 Database Access

### View MongoDB Data

```bash
# Connect to MongoDB
mongosh

# Switch to database
use pillguide_local

# View collections
show collections

# View prescriptions
db.prescriptions.find().pretty()

# View medications
db.medications.find().pretty()

# Clear all data (if needed)
db.prescriptions.deleteMany({})
db.medications.deleteMany({})
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** to Git
2. **Add to `.gitignore`:**
   ```
   .env
   venv/
   node_modules/
   ```
3. **Keep API keys secure**
4. **Use environment variables** for sensitive data

---

## 📦 Building for Production

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

### Frontend
```bash
cd frontend
yarn build
# Deploy the 'build' folder to your hosting service
```

---

## 🆘 Getting Help

### Common Commands Reference

**Start Everything:**
```bash
# Terminal 1 - MongoDB
mongosh  # Just to verify it's running

# Terminal 2 - Backend
cd backend
source venv/bin/activate
uvicorn server:app --reload --port 8001

# Terminal 3 - Frontend  
cd frontend
yarn start
```

**Stop Everything:**
```bash
# Press Ctrl+C in each terminal
```

---

## ✅ Verification Checklist

- [ ] MongoDB installed and running
- [ ] Google Gemini API key obtained
- [ ] Backend `.env` file created with `GEMINI_API_KEY`
- [ ] Python dependencies installed
- [ ] Backend server running on port 8001
- [ ] Frontend `.env` file created
- [ ] Node dependencies installed
- [ ] Frontend server running on port 3000
- [ ] Can access http://localhost:3000 in browser
- [ ] Can upload and analyze prescription images

---

## 🎉 Success!

If you can see the PillGuide homepage and upload prescriptions, you're all set!

**Next Steps:**
- Upload a prescription image
- Try different languages
- Add medications manually
- Check drug interactions

Enjoy using PillGuide locally! 🏥💊
