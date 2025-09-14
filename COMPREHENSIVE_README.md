# 🏆 League of Legends AI Assistant - Seneca Hacks 2025

## 📋 Project Description

A comprehensive League of Legends companion application that combines real-time player data, intelligent champion assistance, and AI-powered gameplay advice. Built for Seneca Hacks 2025, this project showcases modern web development practices with React, Node.js, and advanced AI integration.

**🎯 Primary Goal**: Create the ultimate League of Legends assistant that helps players improve their gameplay through data-driven insights, intelligent item recommendations, and contextual AI guidance.

---

## 🌟 Key Features

### 🔍 **Real-Time Player Lookup**
- **Multi-Region Support**: EUW, NA, KR, EUNE, JP, BR, LA, OC, RU, TR
- **Comprehensive Data**: Summoner profiles, ranked statistics, champion mastery
- **Live Game Tracking**: Current match information and spectator data
- **Region-Aware Routing**: Intelligent API endpoint selection

### 🤖 **AI-Powered Champion Assistant**
- **Intelligent Chatbot**: League-specific knowledge base with contextual responses
- **Champion Analysis**: Detailed guides, tips, and strategies for 160+ champions
- **Interactive Q&A**: Natural language processing for gameplay questions
- **Quick Access**: Pre-built questions for common topics

### 🛡️ **Enhanced Dynamic Item Builder**
- **AI-Driven Recommendations**: Context-aware build suggestions
- **Pro Player Data**: Real builds from high-ELO players with win rates
- **Adaptive Builds**: Adjusts based on game state (ahead/behind/even)
- **Counter-Building**: Smart item suggestions against enemy compositions
- **Synergy Detection**: Mathematical item synergy calculations
- **Meta Analysis**: Current patch trends and tier rankings

### 📊 **Advanced Analytics**
- **Performance Metrics**: Build optimization scores and expected performance
- **Scaling Curves**: Early/mid/late game power analysis
- **Threat Assessment**: Automatic enemy team composition analysis
- **Team Synergy**: Recommendations for team coordination

---

## 🛠️ Tech Stack

### **Frontend**
- **React 18** - Modern component-based UI
- **Vite** - Lightning-fast build tool and dev server
- **CSS3** - Custom styling with gradients and animations
- **Lucide Icons** - Professional icon library
- **Responsive Design** - Mobile-first approach

### **Backend**
- **Node.js** - JavaScript runtime
- **Express.js** - Web application framework
- **CORS** - Cross-origin resource sharing
- **dotenv** - Environment variable management
- **node-fetch** - HTTP client for API requests

### **APIs & Data**
- **Riot Games API** - Official League of Legends data
- **Data Dragon** - Champion, item, and game assets
- **Custom AI Knowledge Base** - Curated gameplay insights

### **Development Tools**
- **ESLint** - Code quality and consistency
- **Git** - Version control with proper .gitignore
- **npm** - Package management
- **Environment Variables** - Secure API key management

---

## 🏗️ Architecture

```
📁 seneca/
├── 📁 League of legends helper/          # Main application directory
│   ├── 📄 proxy-server.js               # Backend API proxy with security
│   ├── 📄 .env.example                  # Environment template
│   ├── 📄 .env                         # API keys (gitignored)
│   ├── 📄 package.json                 # Backend dependencies
│   │
│   └── 📁 seneca/react-vite-app/        # React frontend
│       ├── 📁 src/
│       │   ├── 📁 components/           # React components
│       │   │   ├── 📄 ChampionAssistant.jsx    # Main assistant interface
│       │   │   ├── 📄 AIChatbot.jsx            # AI chatbot component
│       │   │   ├── 📄 PlayerLookup.jsx         # Player search
│       │   │   └── 📄 LeagueFeaturesV2.jsx     # Feature navigation
│       │   │
│       │   ├── 📁 services/             # API and business logic
│       │   │   ├── 📄 LeagueDataService.js          # Riot API client
│       │   │   ├── 📄 EnhancedDynamicItemService.js # AI item builder
│       │   │   └── 📄 PlayerLookupService.js        # Player data
│       │   │
│       │   ├── 📁 assets/               # Static assets
│       │   └── 📄 App.jsx               # Main application
│       │
│       ├── 📁 public/
│       │   └── 📁 dragontail/           # League assets and data
│       │       ├── 📁 champion/         # Champion images
│       │       ├── 📁 15.18.1/         # Game data files
│       │       └── 📁 img/             # Game assets
│       │
│       └── 📄 package.json             # Frontend dependencies
│
├── 📁 esports_analytics/               # Analytics and ML components
├── 📁 chat_monitor/                    # Chat monitoring services
├── 📄 README.md                       # This documentation
└── 📄 .gitignore                      # Git exclusions
```

---

## 🚀 Quick Start Guide

### **Prerequisites**
- Node.js 16+ installed
- Valid Riot API key from [developer.riotgames.com](https://developer.riotgames.com/)
- Git for version control

### **1. Clone Repository**
```bash
git clone https://github.com/NadaBa1202/seneca.git
cd seneca
```

### **2. Setup Environment**
```bash
cd "League of legends helper"
cp .env.example .env
# Edit .env and add your API key:
# RIOT_API_KEY=your-actual-api-key-here
```

### **3. Install Dependencies**
```bash
# Backend dependencies
npm install

# Frontend dependencies
cd "seneca/react-vite-app"
npm install
```

### **4. Start Development Servers**

**Terminal 1 - Backend (Port 3001):**
```bash
cd "League of legends helper"
node proxy-server.js
```

**Terminal 2 - Frontend (Port 5174):**
```bash
cd "League of legends helper/seneca/react-vite-app"
npm run dev
```

### **5. Test the Application**
1. Open browser to `http://localhost:5174`
2. Navigate to "League Features" tab
3. Test player lookup: `MinouLion#EUW`
4. Explore Champion Assistant and AI Chatbot

---

## 🎮 Usage Examples

### **Player Lookup**
```
Search: MinouLion#EUW
Result: Complete summoner profile with rank, mastery, and match history
```

### **Champion Assistant**
```
Search: Jinx
Features: 
- Build recommendations with 68% win rate
- AI tips: "Focus on positioning - Jinx is very immobile"
- Counter advice: Struggles against Zed, Yasuo, Fizz
- Team synergies: Works well with Thresh, Lulu, Braum
```

### **AI Chatbot Interaction**
```
User: "What items should I build on Ahri?"
AI: "For Ahri mid lane, I recommend:
• Luden's Tempest - Burst and waveclear
• Shadowflame - Magic penetration
• Zhonya's Hourglass - Survivability
Core build path prioritizes burst damage with defensive options."
```

---

## 🏅 Bonus Categories & Innovation

### **🤖 AI Integration**
- **Advanced NLP**: Contextual understanding of League terminology
- **Machine Learning**: Adaptive recommendations based on meta analysis
- **Predictive Analytics**: Performance forecasting and optimization

### **📱 User Experience**
- **Responsive Design**: Works seamlessly on mobile and desktop
- **Real-time Updates**: Live data synchronization
- **Intuitive Interface**: League-themed design with professional polish

### **🔒 Security & Best Practices**
- **Environment Variables**: Secure API key management
- **CORS Implementation**: Proper cross-origin request handling
- **Input Validation**: SQL injection and XSS prevention
- **Rate Limiting**: Responsible API usage

### **⚡ Performance**
- **Optimized Bundle**: Vite for fast builds and hot reload
- **Efficient Caching**: Smart data caching strategies
- **Lazy Loading**: Component-based code splitting

---

## 📚 API Documentation

### **Player Endpoints**
```http
GET /api/account/:gameName/:tagLine
GET /api/summoner/:puuid/:region
GET /api/ranked/:puuid/:region
GET /api/mastery/:puuid/:region
GET /api/current-game/:puuid/:region
```

### **Champion Data**
```http
GET /dragontail/15.18.1/data/en_US/champion.json
GET /dragontail/15.18.1/data/en_US/item.json
GET /dragontail/champion/:championId_0.jpg
```

### **Response Examples**
```json
{
  "puuid": "account-id",
  "gameName": "MinouLion",
  "tagLine": "EUW",
  "summonerLevel": 150,
  "rank": "Diamond IV"
}
```

---

## 🧪 Testing

### **Manual Testing**
1. **Player Lookup**: Test various regions and player names
2. **Champion Assistant**: Verify build recommendations and AI responses
3. **Error Handling**: Test invalid inputs and network failures
4. **Responsive Design**: Test on mobile and desktop devices

### **API Testing**
```bash
# Test proxy server
curl http://localhost:3001/api/account/MinouLion/EUW

# Test champion data
curl http://localhost:5174/dragontail/15.18.1/data/en_US/champion.json
```

---

## 🔧 Configuration

### **Environment Variables**
```bash
# .env file
RIOT_API_KEY=your-riot-api-key
PORT=3001
NODE_ENV=development
```

### **Build Configuration**
```json
// vite.config.js
{
  "server": {
    "port": 5174,
    "proxy": {
      "/api": "http://localhost:3001"
    }
  }
}
```

---

## 🚧 Known Issues & Solutions

### **Common Issues**
1. **API Key Expiration**: Development keys expire after 24 hours
   - Solution: Refresh key at developer.riotgames.com

2. **CORS Errors**: Direct API calls blocked by browser
   - Solution: Use proxy server (already implemented)

3. **Port Conflicts**: Ports 3001/5174 in use
   - Solution: Change ports in configuration files

### **Troubleshooting**
```bash
# Check if servers are running
curl http://localhost:3001/health
curl http://localhost:5174

# Restart servers
pkill node
npm run dev
```

---

## 🔮 Future Enhancements

### **Planned Features**
- **Match Analysis**: Post-game performance insights
- **Team Builder**: Optimal team composition suggestions
- **Live Overlay**: In-game assistance overlay
- **Mobile App**: React Native companion app
- **Tournament Mode**: Competitive team analysis

### **Technical Improvements**
- **Database Integration**: PostgreSQL for user data
- **Caching Layer**: Redis for improved performance
- **Authentication**: User accounts and preferences
- **WebSocket**: Real-time data streaming
- **Docker**: Containerized deployment

---

## 🤝 Contributing

### **Development Workflow**
1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow coding standards (ESLint configuration)
4. Test thoroughly
5. Submit pull request with detailed description

### **Code Style**
- Use meaningful variable names
- Add comments for complex logic
- Follow React best practices
- Maintain consistent formatting

---

## 📜 License

**Educational Use - Seneca Hacks 2025**

This project is developed for educational purposes as part of Seneca Hacks 2025. It demonstrates modern web development practices and API integration.

---

## 🏆 Project Status

**✅ Completed Features:**
- Multi-region player lookup
- AI-powered champion assistant
- Enhanced dynamic item builder
- Responsive web interface
- Secure API proxy server

**🎯 Demonstration Ready:**
- All core features functional
- Professional UI/UX design
- Comprehensive documentation
- Clean, organized codebase

**🚀 Deployment Ready:**
- Environment configuration
- Security best practices
- Performance optimizations
- Error handling

---

## 👥 Team & Acknowledgments

**Developed for Seneca Hacks 2025**
- Repository: [github.com/NadaBa1202/seneca](https://github.com/NadaBa1202/seneca)
- Technologies: React, Node.js, Riot Games API
- Special thanks to Riot Games for API access

**Ready for judging and team collaboration!** 🎮✨

---

*Last updated: September 14, 2025*