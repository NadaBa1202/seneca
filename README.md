# League of Legends Helper - Seneca Hacks Project

## 🎮 Project Overview
A comprehensive League of Legends companion app that provides real-time player data, champion assistance, and interactive features for EUW and other regions.

## ✅ What's Working
- **EUW Player Lookup**: Successfully looks up players like `MinouLion#EUW`
- **Region Detection**: Automatically detects and routes to correct regional endpoints
- **Champion Assistant**: Interactive interface with integrated chatbot
- **Proxy Server**: Node.js backend handling Riot API requests with CORS
- **React Frontend**: Modern React + Vite application

## 🚀 Quick Start

### Prerequisites
- Node.js (v14+)
- Valid Riot API key (update in `proxy-server.js`)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/NadaBa1202/seneca.git
   cd seneca
   ```

2. **Start the proxy server**:
   ```bash
   cd "League of legends helper"
   npm install
   node proxy-server.js
   ```
   Server runs on: `http://localhost:3001`

3. **Start the React frontend**:
   ```bash
   cd "League of legends helper/seneca/react-vite-app"
   npm install
   npm run dev
   ```
   Frontend runs on: `http://localhost:5176`

4. **Test EUW Player Lookup**:
   - Navigate to Player Lookup tab
   - Enter: `MinouLion` / `EUW`
   - Should successfully retrieve player data

## 🏗️ Architecture

```
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

### Riot API Key
Update the API key in `League of legends helper/proxy-server.js`:
```javascript
const API_KEY = 'RGAPI-your-api-key-here';
```

### Environment Variables
Create `.env` files for configuration:
```bash
RIOT_API_KEY=your_api_key
PORT=3001
```

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