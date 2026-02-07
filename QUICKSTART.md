# PillGuide - Run Locally on Your Desktop 🏥💻

Complete guide for running PillGuide on your local machine with Google Gemini AI.

---

## ⚡ Quick Start (5 Minutes)

### What You Need

1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **MongoDB** - [Install Guide Below](#install-mongodb)
4. **Google Gemini API Key** - [Get Free Key](https://aistudio.google.com/app/apikey)

---

## 🔑 Step 1: Get Google Gemini API Key (2 minutes)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click **"Create API Key"**
4. Copy the key (looks like: `AIzaSy...`)

💰 **It's FREE!** - 60 requests/minute, 1500/day

---

## 💾 Step 2: Install MongoDB

### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

### Ubuntu/Linux
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

### Windows
Download from [mongodb.com](https://www.mongodb.com/try/download/community) and install

**Verify it's running:**
```bash
mongosh
# Should connect successfully
```

---

## 🔧 Step 3: Setup Backend (2 minutes)

```bash
# Go to backend folder
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# venv\\Scripts\\activate  # Windows

# Install packages
pip install -r requirements.txt
```

**Create `.env` file in backend folder:**
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=pillguide_local
CORS_ORIGINS=http://localhost:3000
GEMINI_API_KEY=AIzaSy...YOUR_KEY_HERE
```

⚠️ **Replace `YOUR_KEY_HERE` with your actual API key!**

**Start backend:**
```bash
uvicorn server:app --reload --port 8001
```

✅ Backend running at http://localhost:8001

---

## 🎨 Step 4: Setup Frontend (1 minute)

**Open NEW terminal:**

```bash
# Go to frontend folder
cd frontend

# Install packages
yarn install
# or: npm install
```

**Create `.env` file in frontend folder:**
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=0
```

**Start frontend:**
```bash
yarn start
# or: npm start
```

✅ Frontend running at http://localhost:3000

---

## 🎉 Done! Open http://localhost:3000

You should see PillGuide homepage!

---

## 🧪 Quick Test

1. Click "Upload Prescription"
2. Choose a prescription image
3. Select language
4. Click "Analyze"
5. See AI-extracted medications!

---

## ❌ Troubleshooting

### "GEMINI_API_KEY not found"
- Check `backend/.env` exists
- Verify API key is correct
- No quotes around the key
- Restart backend

### "Can't connect to MongoDB"
```bash
mongosh  # Check if running
brew services start mongodb-community  # macOS
sudo systemctl start mongodb  # Linux
```

### "Port already in use"
```bash
# Kill port 8001
lsof -ti:8001 | xargs kill -9

# Kill port 3000  
lsof -ti:3000 | xargs kill -9
```

### "Module not found"
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && yarn install
```

---

## 📁 Files You Created

```
backend/.env  ← Your API key is here
frontend/.env ← Backend URL is here
```

**Never commit these files to Git!**

---

## 🚀 Features

- ✅ Upload prescriptions in ANY language
- ✅ AI extracts medications automatically
- ✅ Plain language explanations
- ✅ Check drug interactions
- ✅ 10+ languages supported
- ✅ Behavioral science (Nudge Theory)

---

## 🛑 Stop Servers

Press `Ctrl+C` in each terminal

---

## 📚 More Help

- Full docs: `/docs/` folder
- Architecture: `/docs/ARCHITECTURE.md`
- Features: `/docs/FEATURES.md`
- Detailed setup: `LOCAL_SETUP.md`

---

## ✅ Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] MongoDB running
- [ ] Gemini API key obtained
- [ ] `backend/.env` created
- [ ] `frontend/.env` created
- [ ] Backend runs on port 8001
- [ ] Frontend runs on port 3000
- [ ] Can upload prescriptions

---

**Need help?** Check `LOCAL_SETUP.md` for detailed troubleshooting!

**Happy prescribing! 💊**
