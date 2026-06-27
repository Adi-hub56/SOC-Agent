# Asta SOC Agent 🔐

**AI-Powered Security Operations Center (SOC) Platform** - A full-stack application for intelligent security monitoring, threat analysis, and incident management.

> Built during a **46-day sprint** | Production-ready codebase | Interview portfolio project

---

## 🚀 Features Implemented

### **Phase 1: Core Platform**
- ✅ AI Chatbot Integration (Groq LLM)
- ✅ Incident Management Dashboard
- ✅ SIEM-style Alert System
- ✅ Real-time Statistics & Analytics

### **Phase 2: Security Features**
- ✅ **User Authentication** (JWT-based login/signup)
- ✅ **API Key Management** (generate, revoke, toggle)
- ✅ **Two-Factor Authentication (2FA)** (TOTP via Google Authenticator)
- ✅ **Session Management** (multi-device logout, active session tracking)
- ✅ **Alert Rules** (custom severity thresholds, event filtering)
- ✅ **Password Management** (secure change password)
- ✅ **Notification Settings** (email + Slack integration)

---

## 🛠️ Tech Stack

**Frontend:**
- Next.js 16.2.6 (React 19)
- TypeScript
- Tailwind CSS
- Axios for API calls

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite Database
- Groq API (LLM Integration)
- JWT Authentication
- TOTP 2FA

**Deployment:**
- Backend: Render (FastAPI)
- Frontend: Vercel (Next.js)
- Local: ngrok for API exposure

---

## 📸 Quick Demo

### Dashboard
- Real-time incident alerts
- AI-powered threat analysis
- Customizable incident filtering

### Settings Page
- Profile management
- 2FA setup & backup codes
- API key generation
- Active session tracking
- Alert rules configuration

---

## 🏗️ Project Structure
SOC-Agent/

├── backend/

│   ├── app/

│   │   ├── models/          (User, APIKey, 2FA, Session, AlertRule)

│   │   ├── routes/          (Auth, API Keys, 2FA, Sessions, Alerts)

│   │   ├── schemas/         (Pydantic validation)

│   │   ├── utils/           (Auth helpers, JWT, hashing)

│   │   └── main.py          (FastAPI app)

│   └── requirements.txt

├── frontend/

│   ├── app/

│   │   ├── page.tsx         (Dashboard)

│   │   ├── auth/            (Login/Signup)

│   │   ├── settings/        (Settings page)

│   │   └── layout.tsx       (Auth wrapper)

│   ├── context/             (AuthContext)

│   └── components/          (Reusable UI)

└── README.md
---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- npm or yarn

### **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:3000`

---

## 🔑 Key Features Explained

### **2FA Implementation**
- TOTP-based (Time-based One-Time Password)
- QR code generation for authenticator apps
- Backup codes for account recovery
- Seamless verification flow

### **API Key Management**
- Secure key generation with `sk_` prefix
- Key masking in UI
- Active/inactive toggle
- Last used timestamp tracking

### **Alert Rules**
- Custom severity thresholds (low/medium/high/critical)
- Event type filtering
- Multi-channel notifications (email + Slack)
- Enable/disable rules

### **Session Management**
- Track active sessions across devices
- Logout from specific devices
- Logout from all sessions
- IP & user-agent tracking

---

## 🎯 Learning Outcomes

This project demonstrates:
- Full-stack development (Next.js + FastAPI)
- Security best practices (JWT, 2FA, password hashing)
- Database design & ORM usage
- REST API design & error handling
- Authentication & authorization flows
- State management & context API
- UI/UX for security features

---

## 📊 Development Timeline

| Phase | Days | Focus |
|-------|------|-------|
| Phase 1 | 1-7 | Core platform, chatbot, dashboard |
| Phase 2 | 8-11 | Security features, 2FA, API keys, sessions |
| Deployment | 11+ | Production readiness, documentation |

---

## 🎓 Interview-Ready Highlights

✅ **Demonstrates**:
- Understanding of security concepts (2FA, JWT, password hashing)
- Full-stack development capabilities
- Database design & relationships
- REST API best practices
- Production-ready code structure
- Git workflow & commit history

✅ **Great for discussing**:
- How 2FA works under the hood
- Why certain security decisions were made
- Scalability considerations
- Testing strategies (unit, integration)
- Performance optimizations

---

## 🤝 Connect

- **GitHub**: [github.com/Adi-hub56](https://github.com/Adi-hub56)
- **LinkedIn**: [linkedin.com/in/aditya-kadam-644996320](https://linkedin.com/in/aditya-kadam-644996320)
- **Email**: kadamaditya457@gmail.com

---

## 📝 License

MIT License - Feel free to fork and use!

---

**Built by:** Aditya Rajendra Kadam (Cyrus)  
**Last Updated:** June 27, 2026
