# 📋 Open Source Attribution & Components

This document provides comprehensive attribution and documentation of all open source components, APIs, datasets, and libraries used in the League of Legends Assistant application, as required by Seneca Hacks 2025 competition criteria.

## 🎯 Core Framework & Build Tools

### React (v18.3.1)
- **License**: MIT License
- **Purpose**: Frontend user interface framework
- **Website**: https://react.dev/
- **Repository**: https://github.com/facebook/react
- **Usage**: Primary UI framework for all components (Dashboard, ChampionAssistant, PlayerLookup, etc.)

### Vite (v6.0.4)
- **License**: MIT License
- **Purpose**: Build tool and development server
- **Website**: https://vite.dev/
- **Repository**: https://github.com/vitejs/vite
- **Usage**: Development server, hot reload, production builds

### Node.js & Express.js
- **Node.js**: MIT License - JavaScript runtime for backend services
- **Express.js** (v4.21.0): MIT License - Web application framework
- **Repository**: https://github.com/expressjs/express
- **Usage**: API proxy server for Riot Games API integration

## 🎮 Gaming APIs & Data Sources

### Riot Games API
- **License**: Riot Games API Terms of Service
- **Purpose**: League of Legends player data, match history, champion information
- **Documentation**: https://developer.riotgames.com/
- **Usage**: Player lookup, recent matches, ranking data, champion mastery
- **Regional Routing**: Americas, Europe, Asia platforms

### Dragontail Dataset
- **License**: Riot Games Data Dragon License
- **Purpose**: Static League of Legends data (champions, items, abilities)
- **Documentation**: https://developer.riotgames.com/docs/lol#data-dragon
- **Usage**: Champion information, item data, ability descriptions
- **Version**: 15.18.1 (Latest available)

## 💬 Chat & Communication

### TMI.js (v1.8.5)
- **License**: MIT License
- **Purpose**: Twitch Messaging Interface for chat integration
- **Repository**: https://github.com/tmijs/tmi.js
- **Usage**: Real-time Twitch chat monitoring and message processing

## 📊 Data Visualization & Charts

### Chart.js (v4.4.6)
- **License**: MIT License
- **Purpose**: Interactive charts and data visualization
- **Website**: https://www.chartjs.org/
- **Repository**: https://github.com/chartjs/Chart.js
- **Usage**: Sentiment timeline, emotion analysis charts, statistics visualization

### React-Chartjs-2 (v5.2.0)
- **License**: MIT License
- **Purpose**: React wrapper for Chart.js
- **Repository**: https://github.com/reactchartjs/react-chartjs-2
- **Usage**: Integration of Chart.js components in React

## 🧠 AI & Natural Language Processing

### Custom Sentiment Analysis Engine
- **Implementation**: Custom-built using weighted keyword analysis
- **Purpose**: Real-time sentiment analysis of chat messages
- **Features**: Positive, negative, neutral, toxic classification
- **Emotion Detection**: Joy, anger, fear, sadness, surprise, disgust

### Gaming-Specific Language Model
- **Training Data**: Gaming terminology, League of Legends vocabulary
- **Purpose**: Context-aware sentiment analysis for gaming content
- **Implementation**: Rule-based with machine learning concepts

## 🛠️ Development & Build Dependencies

### JavaScript/TypeScript Ecosystem
- **@types/node**: Type definitions for Node.js
- **ESLint**: Code linting and style enforcement
- **PostCSS**: CSS processing and optimization
- **Autoprefixer**: CSS vendor prefix automation

### React Ecosystem
- **@vitejs/plugin-react**: Vite plugin for React support
- **react-dom**: DOM-specific methods for React
- **react-router-dom**: Client-side routing (if used)

## 🎨 Styling & UI Components

### CSS3 & Modern Web Standards
- **Flexbox & Grid**: Layout systems
- **CSS Custom Properties**: Theme management
- **CSS Animations**: Interactive UI elements
- **Media Queries**: Responsive design

### Custom Design System
- **Color Palette**: Gaming-themed gradient backgrounds
- **Typography**: Inter font family
- **Iconography**: Unicode emojis and custom symbols
- **Glassmorphism**: Backdrop blur effects

## 🗄️ Data Management

### Local Storage & Session Management
- **Browser APIs**: localStorage, sessionStorage
- **State Management**: React hooks (useState, useEffect, useRef)
- **Data Persistence**: User preferences, session data

### Caching Strategy
- **API Response Caching**: In-memory caching for Riot API responses
- **Static Asset Caching**: Browser caching for champion data
- **Rate Limiting**: Client-side request throttling

## 🚀 Deployment & Infrastructure

### Docker & Containerization
- **Docker**: Container platform for deployment
- **Docker Compose**: Multi-container orchestration
- **nginx**: Reverse proxy and load balancer
- **License**: Various (Docker - Apache 2.0, nginx - BSD-2-Clause)

### Cloud Platform Support
- **Heroku**: Platform-as-a-Service deployment
- **Railway**: Modern deployment platform
- **DigitalOcean**: Cloud infrastructure
- **Vercel**: Frontend deployment (if used)

## 📦 Package Managers & Tools

### npm Ecosystem
- **Package Manager**: npm (Node Package Manager)
- **Dependencies**: All packages managed through package.json
- **Scripts**: Build, development, and deployment automation

### Development Tools
- **Git**: Version control system
- **GitHub**: Repository hosting and collaboration
- **VS Code**: Recommended development environment

## 🔐 Security & Environment

### Environment Management
- **dotenv**: Environment variable management
- **CORS**: Cross-Origin Resource Sharing configuration
- **Rate Limiting**: API request throttling
- **Input Validation**: XSS and injection prevention

### API Security
- **HTTPS**: Secure communication protocols
- **API Key Management**: Secure storage and rotation
- **Request Sanitization**: Input cleaning and validation

## 📊 Datasets & Training Data

### League of Legends Data
- **Champion Database**: All 160+ champions with abilities and stats
- **Item Database**: Complete item information and build paths
- **Patch Data**: Current game version 15.18.1
- **Source**: Riot Games Data Dragon

### Chat Analysis Training
- **Gaming Terminology**: League of Legends specific vocabulary
- **Toxicity Patterns**: Common negative language patterns
- **Positive Reinforcement**: Constructive gaming communication
- **Emoji Recognition**: Gaming-related emoji usage

## 🤝 Community & Attribution

### Open Source Contributors
- Special thanks to all maintainers of the libraries used
- React team for the robust framework
- Riot Games for comprehensive API access
- Chart.js community for visualization tools
- TMI.js developers for Twitch integration

### Competition Compliance
- **Seneca Hacks 2025**: All components properly attributed
- **Licensing**: All components use compatible open source licenses
- **Documentation**: Comprehensive usage documentation provided
- **Deployment**: Easy deployment instructions for judges

## 📝 License Compatibility

All components used in this project are compatible with open source distribution:

- **MIT License**: React, Express, Chart.js, TMI.js, Vite (most permissive)
- **BSD License**: nginx (permissive)
- **Apache 2.0**: Docker (permissive)
- **Riot Games Terms**: API usage within developer terms
- **Custom Implementation**: Original sentiment analysis and game logic

## 🔄 Continuous Updates

This project benefits from the active maintenance of:
- Regular security updates from npm audit
- Latest React features and optimizations
- Current League of Legends data from Riot API
- Modern web standards and best practices

---

*Last Updated: January 2025*  
*For Competition: Seneca Hacks 2025*  
*Project: League of Legends Assistant*