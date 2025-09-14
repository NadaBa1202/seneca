# 📡 API Documentation

## League of Legends Gaming Analytics Platform API

### Base URL
- **Development**: `http://localhost:3001`
- **Production**: `https://your-domain.com`

## 🔗 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-14T10:30:00.000Z",
  "uptime": 3600,
  "version": "1.0.0"
}
```

### League of Legends API

#### Get Player Account
```http
GET /api/account/:gameName/:tagLine
```

**Parameters:**
- `gameName` (string): Player's game name
- `tagLine` (string): Player's tag line (e.g., "EUW", "NA1")

**Example:**
```http
GET /api/account/MinouLion/EUW
```

**Response:**
```json
{
  "puuid": "player-uuid-here",
  "gameName": "MinouLion",
  "tagLine": "EUW"
}
```

**Error Responses:**
- `404`: Player not found
- `429`: Rate limit exceeded
- `500`: Internal server error

#### Get Match History
```http
GET /api/matches/:puuid/:region
```

**Parameters:**
- `puuid` (string): Player's PUUID
- `region` (string): Region code (americas, europe, asia)

**Query Parameters:**
- `start` (number, optional): Start index (default: 0)
- `count` (number, optional): Number of matches (default: 20, max: 100)

**Example:**
```http
GET /api/matches/player-uuid-here/europe?start=0&count=10
```

**Response:**
```json
[
  "match-id-1",
  "match-id-2",
  "match-id-3"
]
```

#### Get Match Details
```http
GET /api/match/:matchId/:region
```

**Parameters:**
- `matchId` (string): Match ID
- `region` (string): Region code

**Example:**
```http
GET /api/match/EUW1_6234567890/europe
```

**Response:**
```json
{
  "metadata": {
    "matchId": "EUW1_6234567890",
    "participants": ["puuid1", "puuid2", ...],
    "gameCreation": 1693123456789,
    "gameDuration": 1847,
    "gameEndTimestamp": 1693125303789
  },
  "info": {
    "gameMode": "CLASSIC",
    "gameType": "MATCHED_GAME",
    "mapId": 11,
    "participants": [
      {
        "puuid": "player-uuid",
        "championName": "Jinx",
        "championId": 222,
        "kills": 8,
        "deaths": 3,
        "assists": 12,
        "totalDamageDealtToChampions": 24567,
        "goldEarned": 15234,
        "items": [1055, 1001, 3006, 3031, 3094, 3139],
        "win": true
      }
    ]
  }
}
```

## 🌐 Regional Routing

The API automatically routes requests to the correct regional endpoint based on the region parameter:

### Region Mappings
- **americas**: br1, la1, la2, na1, oc1
- **europe**: eun1, euw1, tr1, ru
- **asia**: jp1, kr, ph2, sg2, th2, tw2, vn2

### Platform Routing
```javascript
const platformRouting = {
  'euw': 'euw1',
  'eune': 'eun1',
  'na': 'na1',
  'kr': 'kr',
  'jp': 'jp1',
  'br': 'br1',
  'lan': 'la1',
  'las': 'la2',
  'oce': 'oc1',
  'tr': 'tr1',
  'ru': 'ru'
};
```

## 🔐 Authentication

### API Key Configuration
The server requires a valid Riot Games API key configured in `proxy-server.js`:

```javascript
const API_KEY = 'RGAPI-your-api-key-here';
```

### Rate Limiting
The proxy server implements rate limiting to comply with Riot API limits:
- **Personal API Key**: 100 requests every 2 minutes
- **Production API Key**: Custom limits based on approval

## 📊 Twitch Integration

### Chat Monitoring
The platform integrates with Twitch chat for real-time sentiment analysis:

#### Connect to Channel
```javascript
// Frontend implementation
const connectToChannel = async (channelName) => {
  const response = await fetch(`/api/twitch/connect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ channel: channelName })
  });
  return response.json();
};
```

#### Real-time Data
- WebSocket connection for live chat messages
- Sentiment analysis processing
- Message categorization (positive, neutral, toxic)

## 🤖 AI Assistant Integration

### Champion Recommendations
```http
POST /api/ai/champion-recommendation
```

**Request Body:**
```json
{
  "role": "ADC",
  "teamComposition": ["Garen", "Graves", "Yasuo", "Thresh"],
  "enemyTeam": ["Darius", "Hecarim", "Zed", "Jinx", "Leona"]
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "champion": "Kai'Sa",
      "reason": "Great synergy with Thresh, can handle Zed threat",
      "confidence": 0.85
    },
    {
      "champion": "Ezreal",
      "reason": "Safe pick against enemy team composition",
      "confidence": 0.78
    }
  ]
}
```

## 📈 Data Structures

### Champion Data
```json
{
  "id": "Jinx",
  "key": "222",
  "name": "Jinx",
  "title": "the Loose Cannon",
  "tags": ["Marksman"],
  "stats": {
    "hp": 610,
    "hpperlevel": 86,
    "mp": 245,
    "mpperlevel": 45,
    "movespeed": 325,
    "armor": 26,
    "armorperlevel": 3.5,
    "spellblock": 30,
    "spellblockperlevel": 0.5,
    "attackrange": 525,
    "hpregen": 3.75,
    "hpregenperlevel": 0.5,
    "mpregen": 6.7,
    "mpregenperlevel": 1,
    "crit": 0,
    "critperlevel": 0,
    "attackdamage": 59,
    "attackdamageperlevel": 2.4,
    "attackspeedperlevel": 1,
    "attackspeed": 0.625
  }
}
```

### Match Participant Data
```json
{
  "puuid": "player-uuid",
  "championId": 222,
  "championName": "Jinx",
  "summonerName": "PlayerName",
  "kills": 8,
  "deaths": 3,
  "assists": 12,
  "totalDamageDealtToChampions": 24567,
  "totalDamageTaken": 18234,
  "goldEarned": 15234,
  "totalMinionsKilled": 156,
  "neutralMinionsKilled": 12,
  "visionScore": 23,
  "items": [1055, 1001, 3006, 3031, 3094, 3139],
  "perks": {
    "statPerks": {
      "defense": 5002,
      "flex": 5008,
      "offense": 5005
    },
    "styles": [
      {
        "description": "primaryStyle",
        "selections": [
          {
            "perk": 8128,
            "var1": 2847,
            "var2": 5,
            "var3": 0
          }
        ],
        "style": 8100
      }
    ]
  },
  "win": true
}
```

## 🔄 WebSocket Events

### Chat Monitoring Events
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:3001/chat');

// Message events
ws.on('chat-message', (data) => {
  console.log(data);
  // {
  //   username: 'viewer123',
  //   message: 'Great play!',
  //   sentiment: 'positive',
  //   timestamp: 1693123456789
  // }
});

ws.on('sentiment-update', (data) => {
  console.log(data);
  // {
  //   positive: 45,
  //   neutral: 32,
  //   toxic: 23,
  //   total: 100
  // }
});
```

## ⚠️ Error Handling

### Standard Error Format
```json
{
  "error": {
    "code": "PLAYER_NOT_FOUND",
    "message": "Player with the specified name and tag was not found",
    "details": {
      "gameName": "InvalidPlayer",
      "tagLine": "EUW"
    },
    "timestamp": "2025-09-14T10:30:00.000Z"
  }
}
```

### Common Error Codes
- `PLAYER_NOT_FOUND`: Player does not exist
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `INVALID_REGION`: Invalid region specified
- `MATCH_NOT_FOUND`: Match ID not found
- `API_KEY_INVALID`: Invalid or expired API key
- `SERVER_ERROR`: Internal server error

## 📝 Example Usage

### JavaScript/Node.js
```javascript
const API_BASE = 'http://localhost:3001';

// Get player information
async function getPlayer(gameName, tagLine) {
  try {
    const response = await fetch(`${API_BASE}/api/account/${gameName}/${tagLine}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching player:', error);
  }
}

// Get recent matches
async function getMatches(puuid, region) {
  try {
    const response = await fetch(`${API_BASE}/api/matches/${puuid}/${region}?count=10`);
    const matchIds = await response.json();
    
    // Get detailed match data
    const matches = await Promise.all(
      matchIds.map(matchId => 
        fetch(`${API_BASE}/api/match/${matchId}/${region}`)
          .then(res => res.json())
      )
    );
    
    return matches;
  } catch (error) {
    console.error('Error fetching matches:', error);
  }
}
```

### React/Frontend
```jsx
import { useState, useEffect } from 'react';

function PlayerLookup() {
  const [playerData, setPlayerData] = useState(null);
  const [loading, setLoading] = useState(false);

  const searchPlayer = async (gameName, tagLine) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/account/${gameName}/${tagLine}`);
      const data = await response.json();
      setPlayerData(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {playerData && (
        <div>
          <h3>{playerData.gameName}#{playerData.tagLine}</h3>
          <p>PUUID: {playerData.puuid}</p>
        </div>
      )}
    </div>
  );
}
```

## 🧪 Testing

### API Testing with curl
```bash
# Health check
curl http://localhost:3001/health

# Player lookup
curl http://localhost:3001/api/account/MinouLion/EUW

# Match history
curl "http://localhost:3001/api/matches/PUUID-HERE/europe?count=5"
```

### Postman Collection
Import the following collection for comprehensive API testing:

```json
{
  "info": {
    "name": "League Analytics API",
    "description": "Complete API collection for testing"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/health"
      }
    },
    {
      "name": "Player Lookup",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/api/account/{{gameName}}/{{tagLine}}"
      }
    }
  ]
}
```

---

**For additional API support or feature requests, please refer to the GitHub repository or contact the development team.**