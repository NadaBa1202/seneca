# League of Legends Companion - Real Data Integration

This system integrates your React Vite app with **real League of Legends data** from:
- **Dragontail** champion database (existing in your project)
- **Riot Games API** (when configured)
- Your existing Python backend services

## 🚀 Quick Start

### 1. Start the API Server
```bash
cd "d:\Seneca Hacks\League of legends helper\seneca\api-server"
npm install
npm start
```

### 2. Start the React App
```bash
cd "d:\Seneca Hacks\League of legends helper\seneca\react-vite-app"
npm run dev
```

### 3. Access the Application
- React App: http://localhost:5173
- API Server: http://localhost:3001
- Health Check: http://localhost:3001/api/health

## 📁 Real Data Sources

### Dragontail Champion Database
- **Location**: `d:\Seneca Hacks\League of legends helper\seneca\15.18.1\`
- **Contains**: Complete champion data, abilities, stats, images
- **Status**: ✅ Already available in your project
- **Integration**: Automatically loaded by API server

### Riot Games API
- **Purpose**: Live player data, match history, current games
- **Status**: 🔧 Requires API key configuration
- **Setup**: Add your Riot API key to connect live data

## 🔄 How It Works

### Current Implementation
1. **RealLeagueService.js** replaces mock AdvancedLeagueService
2. **API Server** serves real dragontail data at http://localhost:3001
3. **React Components** automatically use real champion data
4. **Fallback System** provides enhanced mock data when real APIs unavailable

### Data Flow
```
React App → RealLeagueService → API Server → Dragontail Files
                             → Riot API (when configured)
                             → Python Backend (future integration)
```

## 🏆 Features Using Real Data

### ✅ Currently Working
- **Champion Browser**: Real champion data from dragontail
- **Champion Analysis**: Actual abilities, stats, lore from Riot's database
- **Build Recommendations**: Based on real champion roles and stats
- **AI Assistant**: Enhanced responses using real champion information

### 🔧 Enhanced with API Key
- **Player Lookup**: Real summoner profiles, ranks, match history
- **Live Matches**: Current high-elo games spectator data
- **Pro Scene**: Tournament matches and player statistics
- **Real-time Analytics**: Live game data and performance metrics

## 🛠️ Configuration

### Adding Riot API Key
1. Get your API key from https://developer.riotgames.com/
2. Update `RealLeagueService.js`:
   ```javascript
   this.apiKey = 'YOUR_RIOT_API_KEY_HERE'
   ```
3. The service will automatically switch to real API calls

### Connecting Python Backend
Your existing Python services can be integrated:
- **dragontail.py**: DragontailDataManager
- **riot_client.py**: BaseRiotClient  
- **app.py**: AI assistant with real data

Update API server endpoints to proxy to Python backend:
```javascript
// In server.js
app.get('/api/player/:name', async (req, res) => {
  // Call your Python backend
  const response = await fetch(`http://localhost:8000/player/${req.params.name}`)
  res.json(await response.json())
})
```

## 📊 Data Examples

### Real Champion Data (from Dragontail)
```json
{
  "Ahri": {
    "id": "Ahri",
    "name": "Ahri", 
    "title": "the Nine-Tailed Fox",
    "lore": "Innately connected to the latent power of Runeterra...",
    "spells": [
      {
        "id": "AhriOrb",
        "name": "Orb of Deception",
        "description": "Ahri sends out an orb...",
        "cooldown": [7, 7, 7, 7, 7],
        "cost": [65, 70, 75, 80, 85]
      }
    ],
    "stats": {
      "hp": 526,
      "movespeed": 330,
      "attackdamage": 53
    }
  }
}
```

### Real Player Data (with API key)
```json
{
  "name": "Faker",
  "level": 542,
  "rank": {
    "tier": "Challenger",
    "lp": 1337,
    "winRate": "73.2%"
  },
  "currentMatch": {
    "gameMode": "Ranked Solo/Duo",
    "championName": "Azir",
    "gameLength": 1205
  }
}
```

## 🔍 Testing Real Data Integration

### 1. Verify API Server
```bash
curl http://localhost:3001/api/health
```
Should return dragontail availability status.

### 2. Test Champion Data
```bash
curl http://localhost:3001/api/champions
```
Should return real champion data from dragontail.

### 3. Check React Integration
1. Open http://localhost:5173
2. Go to League Companion tab
3. Browse Champions - should show real champion data
4. Try AI Assistant with "Analyze Ahri in detail"

## 🚨 Troubleshooting

### API Server Issues
- **Port 3001 in use**: Change PORT in server.js
- **CORS errors**: Verify React app is on localhost:5173
- **Dragontail not found**: Check 15.18.1 folder location

### React App Issues  
- **Service errors**: Check browser console for API connectivity
- **Mock data showing**: Verify API server is running
- **Component errors**: Check for proper RealLeagueService import

### Data Loading Issues
- **No champions**: Check dragontail file permissions
- **Slow loading**: Normal for initial load, cached afterwards
- **Missing details**: Some champions may have limited data

## 🎯 Next Steps

1. **Add Riot API Key**: For live player and match data
2. **Connect Python Backend**: Integrate existing AI assistant
3. **Real-time Features**: Live match tracking and notifications
4. **Pro Scene Integration**: Tournament data and professional matches
5. **Advanced Analytics**: Team composition analysis and meta tracking

## 📞 Support

If you encounter issues:
1. Check API server health endpoint
2. Verify all file paths in your system
3. Ensure React dev server is running
4. Check browser console for errors

The system gracefully falls back to enhanced mock data if real data sources are unavailable, so the app will always function.