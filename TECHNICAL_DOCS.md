# 🔧 Technical Documentation - League of Legends AI Assistant

## 📋 Table of Contents
- [System Architecture](#system-architecture)
- [Code Organization](#code-organization)
- [API Reference](#api-reference)
- [Component Documentation](#component-documentation)
- [Service Layer](#service-layer)
- [Data Models](#data-models)
- [Security Implementation](#security-implementation)
- [Performance Optimizations](#performance-optimizations)

---

## 🏗️ System Architecture

### **High-Level Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │    │  Proxy Server   │    │   Riot Games    │
│   (Port 5174)   │◄──►│   (Port 3001)   │◄──►│      API        │
│                 │    │                 │    │                 │
│ • UI Components │    │ • CORS Handling │    │ • Game Data     │
│ • State Mgmt    │    │ • API Security  │    │ • Player Stats  │
│ • AI Chatbot    │    │ • Rate Limiting │    │ • Live Games    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Request Flow**
1. **Client Request**: React component initiates API call
2. **Proxy Layer**: Express server adds authentication headers
3. **API Call**: Forwarded to appropriate Riot Games endpoint
4. **Response Processing**: Data transformation and error handling
5. **Client Update**: UI updates with processed data

---

## 📁 Code Organization

### **Frontend Structure**
```
src/
├── components/                    # React Components
│   ├── ChampionAssistant.jsx     # Main champion interface
│   ├── AIChatbot.jsx             # AI assistant component
│   ├── PlayerLookup.jsx          # Player search functionality
│   ├── LeagueFeaturesV2.jsx      # Feature navigation
│   └── *.css                     # Component styles
│
├── services/                      # Business Logic Layer
│   ├── LeagueDataService.js      # Riot API client
│   ├── EnhancedDynamicItemService.js  # AI item recommendations
│   └── PlayerLookupService.js    # Player data processing
│
├── assets/                        # Static Resources
│   └── images/                    # UI images and icons
│
└── App.jsx                       # Root application component
```

### **Backend Structure**
```
League of legends helper/
├── proxy-server.js               # Express server with API proxy
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Environment template
└── package.json                 # Dependencies and scripts
```

---

## 🔌 API Reference

### **Proxy Server Endpoints**

#### **Account Lookup**
```http
GET /api/account/:gameName/:tagLine
```
**Parameters:**
- `gameName`: Summoner name (e.g., "MinouLion")
- `tagLine`: Region tag (e.g., "EUW")

**Response:**
```json
{
  "puuid": "string",
  "gameName": "string", 
  "tagLine": "string"
}
```

#### **Summoner Data**
```http
GET /api/summoner/:puuid/:region
```
**Parameters:**
- `puuid`: Player UUID from account lookup
- `region`: Server region (euw1, na1, kr, etc.)

**Response:**
```json
{
  "id": "string",
  "puuid": "string",
  "summonerLevel": "number",
  "profileIconId": "number"
}
```

#### **Ranked Information**
```http
GET /api/ranked/:puuid/:region
```
**Response:**
```json
[
  {
    "queueType": "RANKED_SOLO_5x5",
    "tier": "DIAMOND",
    "rank": "IV",
    "leaguePoints": 45,
    "wins": 67,
    "losses": 43
  }
]
```

### **Data Dragon Endpoints**
```http
GET /dragontail/15.18.1/data/en_US/champion.json
GET /dragontail/15.18.1/data/en_US/item.json
GET /dragontail/champion/:championId_0.jpg
```

---

## 🧩 Component Documentation

### **ChampionAssistant.jsx**
**Purpose**: Main interface for champion analysis and recommendations

**Key Features:**
- Champion search with autocomplete
- Dynamic item build recommendations
- AI chatbot integration
- Responsive design with loading states

**State Management:**
```javascript
const [selectedChampion, setSelectedChampion] = useState(null)
const [dynamicBuilds, setDynamicBuilds] = useState(null)
const [buildLoading, setBuildLoading] = useState(false)
const [showChatbot, setShowChatbot] = useState(false)
```

**Key Methods:**
```javascript
// Champion selection and data loading
handleChampionSelect(championId)

// Enhanced build recommendations
loadDynamicBuilds(champion, gameContext)

// UI state management
toggleChatbot()
```

### **AIChatbot.jsx**
**Purpose**: Intelligent League of Legends assistant

**Knowledge Base:**
- Champion-specific tips and strategies
- Item build recommendations
- Meta analysis and tier lists
- Gameplay advice and mechanics

**Message Processing:**
```javascript
generateResponse(userMessage) {
  // Natural language processing
  // Context-aware responses
  // League-specific knowledge lookup
}
```

**Features:**
- Real-time typing indicators
- Markdown-style formatting
- Quick question buttons
- Responsive chat interface

### **PlayerLookup.jsx**
**Purpose**: Multi-region player search and statistics

**Region Support:**
```javascript
const regions = {
  'EUW': 'euw1',
  'NA': 'na1', 
  'KR': 'kr',
  // ... all supported regions
}
```

**Data Flow:**
1. User enters summoner name and region
2. Account lookup via Riot ID API
3. Summoner data retrieval
4. Ranked statistics and mastery data
5. UI update with comprehensive profile

---

## ⚙️ Service Layer

### **LeagueDataService.js**
**Purpose**: Centralized API client for champion and game data

**Methods:**
```javascript
class LeagueDataService {
  async loadChampions()           // Load all champion data
  async getChampion(championId)   // Get specific champion details
  async loadItems()               // Load item database
  async getChampionImage(id)      // Retrieve champion artwork
}
```

### **EnhancedDynamicItemService.js**
**Purpose**: AI-driven item recommendation engine

**Core Features:**
- Pro player build database
- Meta analysis and tier rankings  
- Adaptive recommendations based on game state
- Item synergy calculations
- Counter-build suggestions

**Key Methods:**
```javascript
class EnhancedDynamicItemService {
  // Main recommendation engine
  async getIntelligentBuildRecommendations(champion, gameContext)
  
  // Pro build analysis
  initializeProBuilds()
  
  // Meta item tracking
  initializeMetaItems()
  
  // Threat analysis
  analyzeThreatLevel(enemyTeam)
  
  // Build optimization
  calculateConfidence(proData, categories, gameContext)
}
```

**Game Context Analysis:**
```javascript
const gameContext = {
  gameMode: 'ranked',      // ranked, normal, aram
  role: 'ADC',             // detected or specified role
  gameLength: 'normal',    // early, normal, late
  enemyTeam: [],           // enemy champion analysis
  allyTeam: [],            // team synergy analysis
  gameState: 'even',       // ahead, behind, even
  playerSkill: 'average'   // skill level consideration
}
```

### **PlayerLookupService.js**
**Purpose**: Player data processing and enrichment

**Capabilities:**
- Region-aware API routing
- Data transformation and normalization
- Error handling and retry logic
- Caching for performance optimization

---

## 📊 Data Models

### **Champion Data Structure**
```javascript
{
  id: "Jinx",
  name: "Jinx",
  title: "The Loose Cannon",
  tags: ["Marksman"],
  info: {
    difficulty: 6,
    attack: 9,
    defense: 2,
    magic: 4
  },
  stats: {
    hp: 610,
    hpperlevel: 86,
    mp: 245,
    mpperlevel: 45
  },
  spells: [...]
}
```

### **Pro Build Data Structure**
```javascript
{
  champion: "Jinx",
  core: ["Kraken Slayer", "Phantom Dancer", "Infinity Edge"],
  boots: ["Berserker's Greaves"],
  situational: ["Lord Dominik's Regards", "Guardian Angel"],
  winRate: 0.68,
  pickRate: 0.12,
  role: "ADC",
  gameLength: {
    early: 0.45,
    mid: 0.72, 
    late: 0.68
  }
}
```

### **Player Profile Structure**
```javascript
{
  account: {
    puuid: "string",
    gameName: "MinouLion",
    tagLine: "EUW"
  },
  summoner: {
    id: "string",
    summonerLevel: 150,
    profileIconId: 4568
  },
  ranked: [
    {
      queueType: "RANKED_SOLO_5x5",
      tier: "DIAMOND",
      rank: "IV",
      leaguePoints: 45,
      wins: 67,
      losses: 43
    }
  ]
}
```

---

## 🔒 Security Implementation

### **API Key Management**
```javascript
// Environment variable loading
require('dotenv').config()

// Secure header injection
const headers = {
  'X-Riot-Token': process.env.RIOT_API_KEY
}

// API key validation
if (!process.env.RIOT_API_KEY) {
  throw new Error('RIOT_API_KEY environment variable required')
}
```

### **CORS Configuration**
```javascript
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:5174'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE']
}))
```

### **Input Validation**
```javascript
// Route parameter validation
app.get('/api/account/:gameName/:tagLine', (req, res) => {
  const { gameName, tagLine } = req.params
  
  // Sanitize inputs
  if (!gameName || !tagLine) {
    return res.status(400).json({ error: 'Missing required parameters' })
  }
  
  // Validate format
  if (!/^[a-zA-Z0-9\s]+$/.test(gameName)) {
    return res.status(400).json({ error: 'Invalid game name format' })
  }
})
```

### **Rate Limiting**
```javascript
// Implement rate limiting to respect Riot API limits
const rateLimit = require('express-rate-limit')

const limiter = rateLimit({
  windowMs: 2 * 60 * 1000, // 2 minutes
  max: 100 // limit each IP to 100 requests per windowMs
})

app.use('/api', limiter)
```

---

## ⚡ Performance Optimizations

### **Frontend Optimizations**

#### **Component Optimization**
```javascript
// Memoized components for expensive renders
const ChampionAssistant = React.memo(({ champion }) => {
  // Component logic
})

// Lazy loading for large components
const AIChatbot = React.lazy(() => import('./AIChatbot'))
```

#### **State Management**
```javascript
// Efficient state updates
const [champions, setChampions] = useState([])

// Debounced search to reduce API calls
const debouncedSearch = useCallback(
  debounce((searchTerm) => {
    performSearch(searchTerm)
  }, 300),
  []
)
```

#### **Asset Optimization**
```javascript
// Lazy image loading with error fallbacks
<img 
  src={`/dragontail/champion/${champion.id}_0.jpg`}
  alt={champion.name}
  loading="lazy"
  onError={(e) => {
    e.target.src = `https://fallback-cdn.com/champion/${champion.id}.png`
  }}
/>
```

### **Backend Optimizations**

#### **Caching Strategy**
```javascript
// In-memory caching for frequently accessed data
const cache = new Map()

async function getCachedData(key, fetchFunction) {
  if (cache.has(key)) {
    return cache.get(key)
  }
  
  const data = await fetchFunction()
  cache.set(key, data)
  
  // Auto-expire cache entries
  setTimeout(() => cache.delete(key), 5 * 60 * 1000) // 5 minutes
  
  return data
}
```

#### **Connection Pooling**
```javascript
// HTTP client with connection reuse
const fetch = require('node-fetch')
const agent = new (require('https').Agent)({
  keepAlive: true,
  maxSockets: 10
})

// Reuse connections for better performance
const response = await fetch(url, { agent })
```

### **Database Optimization** (Future Enhancement)
```sql
-- Indexed queries for fast player lookups
CREATE INDEX idx_player_puuid ON players(puuid);
CREATE INDEX idx_player_region ON players(region);

-- Materialized views for aggregated statistics
CREATE MATERIALIZED VIEW champion_winrates AS
SELECT champion_id, AVG(win) as win_rate, COUNT(*) as games
FROM matches
GROUP BY champion_id;
```

---

## 🧪 Testing Strategy

### **Unit Testing**
```javascript
// Service layer testing
describe('LeagueDataService', () => {
  test('should load champion data successfully', async () => {
    const service = new LeagueDataService()
    const champions = await service.loadChampions()
    
    expect(champions).toBeDefined()
    expect(Array.isArray(champions)).toBe(true)
    expect(champions.length).toBeGreaterThan(0)
  })
})
```

### **Integration Testing**
```javascript
// API endpoint testing
describe('Proxy Server', () => {
  test('should handle player lookup correctly', async () => {
    const response = await fetch('/api/account/MinouLion/EUW')
    const data = await response.json()
    
    expect(response.status).toBe(200)
    expect(data.puuid).toBeDefined()
    expect(data.gameName).toBe('MinouLion')
  })
})
```

### **End-to-End Testing**
```javascript
// User workflow testing with Cypress/Playwright
describe('Champion Assistant Workflow', () => {
  test('user can search and view champion details', () => {
    cy.visit('/')
    cy.get('[data-testid="champion-search"]').type('Jinx')
    cy.get('[data-testid="suggestion-Jinx"]').click()
    cy.get('[data-testid="champion-details"]').should('be.visible')
    cy.get('[data-testid="build-recommendations"]').should('contain', 'Kraken Slayer')
  })
})
```

---

## 🚀 Deployment Guide

### **Environment Setup**
```bash
# Production environment variables
NODE_ENV=production
RIOT_API_KEY=your-production-api-key
PORT=3001
ALLOWED_ORIGINS=https://your-domain.com
```

### **Build Process**
```bash
# Frontend build
cd seneca/react-vite-app
npm run build

# Backend preparation
cd ../..
npm install --production
```

### **Docker Configuration** (Recommended)
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install --production

COPY . .
EXPOSE 3001

CMD ["node", "proxy-server.js"]
```

---

## 📈 Monitoring & Analytics

### **Performance Metrics**
- API response times
- Cache hit rates
- Error frequencies
- User engagement metrics

### **Logging Strategy**
```javascript
// Structured logging with Winston
const winston = require('winston')

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'app.log' }),
    new winston.transports.Console()
  ]
})
```

---

*This technical documentation provides comprehensive implementation details for developers working on the League of Legends AI Assistant project.*