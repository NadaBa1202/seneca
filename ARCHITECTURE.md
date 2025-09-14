# 🏗️ Architecture Documentation

## League of Legends Gaming Analytics Platform

### 📊 System Overview

The League of Legends Gaming Analytics Platform is a full-stack web application that combines real-time Twitch chat sentiment analysis with comprehensive League of Legends player analytics. The system is built using modern web technologies and follows a microservices-inspired architecture pattern.

## 🎯 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  React Frontend (Port 5179)                                    │
│  ├── Landing Page (Twitch Integration)                         │
│  ├── Dashboard (Real-time Analytics)                           │
│  ├── League Features (Player Lookup, Champion Assistant)       │
│  └── AI Chatbot (Gaming Assistant)                             │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Express.js API Server (Port 3001)                             │
│  ├── Proxy Server (Regional Routing)                           │
│  ├── CORS Configuration                                         │
│  ├── Request/Response Handling                                  │
│  └── Error Handling & Rate Limiting                            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  External APIs  │ │  Data Processing │ │  Real-time      │
│                 │ │                 │ │  Communication  │
│ • Riot Games API│ │ • Chat Analysis │ │ • WebSocket     │
│ • Twitch API    │ │ • Sentiment ML  │ │ • Live Updates  │
│ • Data Dragon   │ │ • Data Caching  │ │ • Event Stream  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🏗️ Component Architecture

### Frontend Architecture (React + Vite)

```
src/
├── components/                    # Reusable React Components
│   ├── LandingPage.jsx           # Main landing page with Twitch integration
│   │   ├── Feature Cards         # Analytics feature showcase
│   │   ├── Channel Input         # Twitch channel connection
│   │   └── How It Works         # Usage instructions
│   │
│   ├── Dashboard.jsx             # Real-time analytics dashboard
│   │   ├── StatCards            # Key metrics display
│   │   ├── ChartContainer       # Data visualization
│   │   ├── MessageFeed          # Live chat messages
│   │   └── SentimentSummary     # Sentiment breakdown
│   │
│   ├── LeagueFeaturesV2.jsx      # League of Legends features
│   │   ├── PlayerLookup         # Player search and stats
│   │   ├── ChampionAssistant    # AI-powered recommendations
│   │   └── ItemBuilds           # Dynamic item suggestions
│   │
│   ├── AIChatbot.jsx             # Intelligent gaming assistant
│   │   ├── MessageHistory       # Chat conversation
│   │   ├── InputField           # User input interface
│   │   └── TypingIndicator      # Real-time feedback
│   │
│   └── Shared Components/
│       ├── LoadingSpinner.jsx   # Loading states
│       ├── ErrorBoundary.jsx    # Error handling
│       └── SearchInput.jsx      # Reusable search inputs
│
├── styles/                       # Component-specific styling
│   ├── LandingPage.css          # Landing page styles
│   ├── Dashboard.css            # Dashboard styles
│   ├── LeagueFeatures.css       # League features styles
│   └── AIChatbot.css            # Chatbot styles
│
├── utils/                        # Utility functions
│   ├── api.js                   # API communication
│   ├── dataProcessing.js        # Data transformation
│   └── constants.js             # Application constants
│
├── App.jsx                       # Main application component
├── main.jsx                      # Application entry point
└── index.css                     # Global styles
```

### Backend Architecture (Express.js)

```
League of legends helper/
├── proxy-server.js               # Main Express application
│   ├── CORS Configuration        # Cross-origin resource sharing
│   ├── Route Definitions         # API endpoint routing
│   ├── Regional Routing Logic    # Riot API region handling
│   ├── Error Handling           # Centralized error management
│   └── Rate Limiting            # API rate limit compliance
│
├── modules/ (conceptual)
│   ├── riotApiService.js        # Riot Games API integration
│   ├── chatMonitoring.js        # Twitch chat processing
│   ├── sentimentAnalysis.js     # AI sentiment classification
│   └── dataCache.js             # Response caching layer
│
└── package.json                  # Dependencies and scripts
```

## 🔄 Data Flow Architecture

### 1. Twitch Chat Analysis Flow
```
User Input (Channel Name)
    │
    ▼
Frontend Validation
    │
    ▼
API Request (/api/twitch/connect)
    │
    ▼
Backend Channel Connection
    │
    ▼
WebSocket Establishment
    │
    ▼
Real-time Chat Stream
    │
    ▼
Sentiment Analysis Processing
    │
    ▼
Data Aggregation & Statistics
    │
    ▼
Frontend Dashboard Updates
    │
    ▼
User Visualization (Charts & Metrics)
```

### 2. League of Legends Data Flow
```
User Search (Player Name + Tag)
    │
    ▼
Frontend Input Validation
    │
    ▼
API Request (/api/account/{name}/{tag})
    │
    ▼
Regional Route Determination
    │
    ▼
Riot API Call (Account Service)
    │
    ▼
Player PUUID Retrieved
    │
    ▼
Match History Request (/api/matches/{puuid}/{region})
    │
    ▼
Batch Match Detail Requests
    │
    ▼
Data Processing & Aggregation
    │
    ▼
Response Formatting
    │
    ▼
Frontend Data Display
```

### 3. AI Assistant Interaction Flow
```
User Question Input
    │
    ▼
Frontend Message Formatting
    │
    ▼
Context Building (Game State, Champion Data)
    │
    ▼
AI Processing (LLM Integration)
    │
    ▼
Response Generation
    │
    ▼
League-specific Knowledge Injection
    │
    ▼
Frontend Message Display
    │
    ▼
Conversation History Update
```

## 🌐 API Architecture

### RESTful Endpoints Structure
```
/api/
├── /health                       # System health check
├── /account/{name}/{tag}         # Player account lookup
├── /matches/{puuid}/{region}     # Match history retrieval
├── /match/{matchId}/{region}     # Detailed match data
├── /champions                    # Champion data (Data Dragon)
├── /items                        # Item data (Data Dragon)
└── /ai/
    ├── /champion-recommend       # AI champion suggestions
    ├── /build-optimize          # Item build optimization
    └── /chat                    # AI assistant chat
```

### Regional Routing System
```javascript
const REGION_MAPPINGS = {
  // Platform to Regional Mapping
  platforms: {
    'euw1': 'europe',
    'eun1': 'europe',
    'na1': 'americas',
    'kr': 'asia',
    'jp1': 'asia',
    // ... additional mappings
  },
  
  // Regional Endpoints
  endpoints: {
    'americas': 'americas.api.riotgames.com',
    'europe': 'europe.api.riotgames.com',
    'asia': 'asia.api.riotgames.com'
  }
};
```

## 💾 State Management

### Frontend State Architecture
```javascript
// Application State Structure
const AppState = {
  // User Interface State
  ui: {
    currentView: 'landing' | 'dashboard' | 'league',
    loading: boolean,
    errors: Error[],
    notifications: Notification[]
  },
  
  // Twitch Integration State
  twitch: {
    connected: boolean,
    channelName: string,
    chatMessages: Message[],
    sentimentStats: {
      positive: number,
      neutral: number,
      toxic: number,
      total: number
    }
  },
  
  // League of Legends State
  league: {
    currentPlayer: Player | null,
    matchHistory: Match[],
    champions: Champion[],
    selectedChampion: Champion | null,
    aiRecommendations: Recommendation[]
  },
  
  // AI Assistant State
  ai: {
    chatHistory: ChatMessage[],
    isTyping: boolean,
    context: GameContext
  }
};
```

### Backend State Management
- **Stateless Design**: Each request is independent
- **Session Management**: WebSocket connections for real-time features
- **Caching Strategy**: In-memory caching for frequently accessed data
- **Rate Limiting**: Per-endpoint and global rate limiting

## 🔒 Security Architecture

### Frontend Security
- **Input Validation**: Client-side validation for all user inputs
- **XSS Prevention**: Sanitization of user-generated content
- **HTTPS Enforcement**: Secure communication protocols
- **Error Handling**: Safe error messages without sensitive data exposure

### Backend Security
- **API Key Management**: Secure storage and rotation of Riot API keys
- **CORS Configuration**: Restricted cross-origin requests
- **Rate Limiting**: Protection against abuse and DoS attacks
- **Input Sanitization**: Server-side validation and sanitization

### Data Security
- **No User Data Storage**: Stateless operations without persistent user data
- **API Key Rotation**: Regular rotation of external API keys
- **Audit Logging**: Comprehensive logging for security monitoring

## 📈 Performance Architecture

### Frontend Optimization
- **Code Splitting**: Dynamic imports for route-based chunking
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo and useMemo for expensive operations
- **Virtual Scrolling**: Efficient rendering of large data sets

### Backend Optimization
- **Response Caching**: Intelligent caching of API responses
- **Connection Pooling**: Efficient HTTP request management
- **Compression**: Gzip compression for API responses
- **Concurrent Processing**: Parallel API calls where possible

### Database-Free Architecture
- **No Database**: Stateless design eliminates database overhead
- **Cache-First**: In-memory caching for performance
- **External API Optimization**: Strategic API call batching

## 🚀 Deployment Architecture

### Development Environment
```
Developer Machine
├── Frontend (Vite Dev Server: 5179)
├── Backend (Node.js: 3001)
└── External APIs (Riot, Twitch)
```

### Production Environment
```
Production Server
├── Nginx (Reverse Proxy: 80/443)
│   ├── Static File Serving
│   ├── SSL Termination
│   └── Load Balancing
├── PM2 (Process Manager)
│   └── Node.js Application (3001)
└── System Services
    ├── Monitoring (PM2, System)
    ├── Logging (Application, Access)
    └── Security (Firewall, Updates)
```

## 🔄 Real-time Architecture

### WebSocket Implementation
```javascript
// Real-time Communication Flow
Client WebSocket Connection
    │
    ▼
Server WebSocket Handler
    │
    ├── Chat Message Processing
    ├── Sentiment Analysis
    ├── Statistics Aggregation
    └── Broadcast Updates
    │
    ▼
Client State Updates
    │
    ▼
UI Re-rendering (React)
```

### Event-Driven Updates
- **Chat Messages**: Real-time message streaming
- **Sentiment Analysis**: Live sentiment classification
- **Statistics**: Dynamic chart updates
- **Connection Status**: Real-time connection monitoring

## 🧪 Testing Architecture

### Frontend Testing Strategy
- **Unit Tests**: Component logic testing with Vitest
- **Integration Tests**: API integration testing
- **E2E Tests**: Full user flow testing with Cypress
- **Visual Regression**: UI consistency testing

### Backend Testing Strategy
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Load Testing**: Performance under stress
- **Security Testing**: Vulnerability assessment

## 📊 Monitoring & Analytics

### Application Monitoring
- **Performance Metrics**: Response times, throughput
- **Error Tracking**: Exception monitoring and alerting
- **User Analytics**: Usage patterns and feature adoption
- **API Monitoring**: External API health and rate limits

### Infrastructure Monitoring
- **System Resources**: CPU, memory, disk usage
- **Network Performance**: Latency and bandwidth
- **Application Logs**: Centralized logging and analysis
- **Uptime Monitoring**: Service availability tracking

## 🔮 Scalability Considerations

### Horizontal Scaling
- **Load Balancing**: Multiple application instances
- **Microservices**: Service decomposition for independent scaling
- **CDN Integration**: Global content distribution
- **Auto-scaling**: Dynamic resource allocation

### Vertical Scaling
- **Resource Optimization**: Efficient resource utilization
- **Performance Tuning**: Code and infrastructure optimization
- **Caching Strategies**: Multi-level caching implementation
- **Database Optimization**: If database layer is added

---

**This architecture documentation provides a comprehensive overview of the system design, enabling developers to understand, maintain, and extend the platform effectively.**