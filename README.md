# 🏆 League of Legends AI Assistant - Seneca Hacks 2025

## 🎮 Project Overview
A comprehensive League of Legends companion app featuring real-time player lookup, AI-powered champion assistance, and intelligent item recommendations. Built with React, Node.js, and the Riot Games API for Seneca Hacks 2025.

## ✨ Key Features
- **🔍 Multi-Region Player Lookup**: Search players across all regions (EUW, NA, KR, etc.)
- **🤖 AI Champion Assistant**: Intelligent chatbot with League-specific knowledge
- **🛡️ Enhanced Dynamic Item Builder**: AI-driven recommendations with pro builds
- **📊 Real-Time Analytics**: Live game tracking and performance metrics
- **🎨 Professional UI**: Responsive League of Legends themed interface

## 🛠️ Tech Stack
- **Frontend**: React 18, Vite, CSS3, Responsive Design
- **Backend**: Node.js, Express, CORS, Environment Security
- **APIs**: Riot Games API, Data Dragon, Custom AI Knowledge Base
- **Tools**: ESLint, Git, npm, Professional Development Practices

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Riot API key from [developer.riotgames.com](https://developer.riotgames.com/)

### Setup Instructions

1. **Clone and setup environment**:
   ```bash
   git clone https://github.com/NadaBa1202/seneca.git
   cd seneca/League\ of\ legends\ helper
   cp .env.example .env
   # Edit .env and add: RIOT_API_KEY=your-api-key-here
   ```

2. **Install dependencies**:
   ```bash
   npm install
   cd seneca/react-vite-app
   npm install
   ```

3. **Start servers** (2 terminals):
   ```bash
   # Terminal 1 - Backend (Port 3001)
   cd "League of legends helper"
   node proxy-server.js

   # Terminal 2 - Frontend (Port 5174)  
   cd "League of legends helper/seneca/react-vite-app"
   npm run dev
   ```

4. **Test application**:
   - Open `http://localhost:5174`
   - Navigate to "League Features" tab
   - Test player lookup: `MinouLion#EUW`
   - Explore Champion Assistant and AI Chatbot

## 🏗️ Architecture

```
📁 seneca/
├── 📁 League of legends helper/          # Main application
│   ├── 📄 proxy-server.js               # Backend API proxy
│   ├── 📄 .env                         # API keys (gitignored)
│   └── 📁 seneca/react-vite-app/        # React frontend
│       ├── 📁 src/components/           # UI components
│       ├── 📁 src/services/            # Business logic
│       └── 📁 public/dragontail/       # Game assets
├── 📄 COMPREHENSIVE_README.md           # Detailed documentation
├── 📄 TECHNICAL_DOCS.md                # Developer documentation
└── 📄 GITHUB_DESCRIPTION.md            # Repository description
```

## ✅ What's Working

### **Core Features Tested**
- ✅ **EUW Player Lookup**: `MinouLion#EUW` successfully retrieves data
- ✅ **Region Detection**: Automatic routing to correct API endpoints
- ✅ **Champion Assistant**: Interactive interface with 160+ champions
- ✅ **AI Chatbot**: League-specific knowledge base with contextual responses
- ✅ **Dynamic Item Builder**: Pro builds with win rates and meta analysis
- ✅ **Responsive Design**: Works on mobile and desktop

### **API Endpoints**
```http
GET /api/account/:gameName/:tagLine     # Account lookup
GET /api/summoner/:puuid/:region        # Summoner data  
GET /api/ranked/:puuid/:region          # Ranked statistics
GET /api/mastery/:puuid/:region         # Champion mastery
GET /api/current-game/:puuid/:region    # Live game data
```

## 🎯 Demo Instructions

### **Player Lookup Demo**
1. Go to "League Features" → "Player Lookup"
2. Enter: `MinouLion` / `EUW`
3. View complete profile with rank and statistics

### **Champion Assistant Demo**
1. Go to "League Features" → "Champion Assistant" 
2. Search: `Jinx`, `Ahri`, or `Thresh`
3. View enhanced builds with AI insights
4. Click "💬 AI Help" for interactive assistance

### **AI Chatbot Demo**
```
Try asking:
- "What items should I build on Jinx?"
- "How do I play against Yasuo?"
- "What's the current meta for ADC?"
- "Give me tips for team fighting"
```

## 🔒 Security & Configuration

### **Environment Variables**
```bash
# .env file (create from .env.example)
RIOT_API_KEY=your-riot-api-key-here
PORT=3001
NODE_ENV=development
```

### **Important Security Notes**
- ✅ API keys stored in environment variables
- ✅ .env file properly gitignored  
- ✅ CORS properly configured
- ✅ Input validation implemented
- ✅ No sensitive data in repository

## 🏅 Competition Features

### **Innovation Highlights**
- **AI-Powered Recommendations**: Context-aware item builds
- **Real-Time Data Integration**: Live player statistics
- **Professional UX**: League of Legends themed interface
- **Comprehensive Knowledge Base**: 160+ champions analyzed

### **Technical Excellence**
- **Clean Architecture**: Modular, maintainable code
- **Performance Optimized**: Caching and lazy loading
- **Error Handling**: Graceful degradation and user feedback
- **Documentation**: Comprehensive setup and usage guides

## 🚧 Development Status

### **Completed ✅**
- Multi-region player lookup with EUW testing
- AI chatbot with League-specific knowledge
- Enhanced dynamic item builder with pro builds
- Professional responsive interface
- Secure API proxy with environment configuration
- Comprehensive documentation

### **Ready for Demonstration ✅**
- All core features functional
- Clean, organized codebase
- Professional documentation
- Security best practices implemented

## 📚 Documentation

- **Quick Start**: This README
- **Comprehensive Guide**: [COMPREHENSIVE_README.md](./COMPREHENSIVE_README.md)
- **Technical Details**: [TECHNICAL_DOCS.md](./TECHNICAL_DOCS.md)
- **GitHub Info**: [GITHUB_DESCRIPTION.md](./GITHUB_DESCRIPTION.md)

## 🔧 Troubleshooting

### **Common Issues**
```bash
# If ports are in use
pkill node
npm run dev

# If API key expired
# Get new key from developer.riotgames.com
# Update .env file

# If dependencies missing
npm install
cd seneca/react-vite-app && npm install
```

### **Test API Connection**
```bash
curl http://localhost:3001/api/account/MinouLion/EUW
```

## 🤝 Contributing & Team Collaboration

**Ready for team expansion!** This project has:
- Clean, documented codebase
- Modular architecture for easy development
- Comprehensive setup instructions
- Professional development practices

## � Seneca Hacks 2025 Submission

**Categories**: Best Use of API, Best AI Implementation, Best UX, Most Innovative

**Repository**: [github.com/NadaBa1202/seneca](https://github.com/NadaBa1202/seneca)

---

**🎮 Ready for judging and continued development!** ✨

*Last updated: September 14, 2025*
├── League of legends helper/
│   ├── proxy-server.js           # Backend API proxy with region support
│   ├── seneca/react-vite-app/    # React frontend application
│   │   ├── src/components/       # React components
│   │   ├── src/services/         # API services
│   │   └── package.json
│   └── package.json
├── esports_analytics/            # Analytics and ML components
├── chat_monitor/                 # Chat monitoring services
└── .gitignore                   # Excludes large files and dependencies
```

## 🔧 Key Features

### Region Support
- **Fixed**: EUW player lookup now works correctly
- **Regions**: NA1, EUW, EUNE, KR, JP, BR1, LA1, LA2, OC1, RU, TR1
- **API Endpoints**: Region-aware routing to correct Riot API servers

### API Endpoints
- `GET /api/account/:gameName/:tagLine` - Account lookup
- `GET /api/summoner/:puuid/:region` - Summoner data
- `GET /api/ranked/:puuid/:region` - Ranked information
- `GET /api/mastery/:puuid/:region` - Champion mastery
- `GET /api/current-game/:puuid/:region` - Live game data

### Frontend Components
- **PlayerLookup**: Real-time player data retrieval
- **ChampionAssistant**: Interactive champion guidance
- **Chatbot**: Integrated AI assistant
- **LeagueFeaturesV2**: Main interface with tabs

## 🛠️ Areas for Development

### Immediate Tasks
1. **Dynamic Item Builds**: Make item recommendations more interactive
2. **Frontend Polish**: Improve UI/UX design
3. **Error Handling**: Better error messages and loading states
4. **Testing**: Add comprehensive test coverage

### Features to Add
- Match history analysis
- Champion build recommendations
- Real-time game overlay
- Multi-language support
- Advanced analytics dashboard

## 📝 Configuration

### ⚠️ IMPORTANT: API Key Security
**DO NOT** commit API keys to git! Follow these steps:

1. **Copy the environment template**:
   ```bash
   cd "League of legends helper"
   cp .env.example .env
   ```

2. **Add your API key to .env**:
   ```bash
   RIOT_API_KEY=your-actual-api-key-here
   PORT=3001
   ```

3. **Verify .env is in .gitignore** (it is!)

### Riot API Key
Get your API key from [Riot Developer Portal](https://developer.riotgames.com/)
- Development keys expire after 24 hours
- Never commit keys to version control
- Use environment variables for production

## 🐛 Known Issues
- Some large files excluded via .gitignore (models, datasets)
- Node-fetch dependency required for proxy server
- CORS handling implemented in proxy server

## 🤝 Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit pull request

## 📄 License
This project is for educational purposes (Seneca Hacks).

## 🔗 API Documentation
- [Riot Developer Portal](https://developer.riotgames.com/)
- [League of Legends API](https://developer.riotgames.com/apis#league-of-legends-v4)

---
**Ready for team collaboration!** 🚀