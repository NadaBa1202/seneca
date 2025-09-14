# 🛠️ Development Setup Guide

## Development Environment Setup for League of Legends Gaming Analytics Platform

### 📋 Prerequisites

#### Required Software
- **Node.js** 16.0 or higher ([Download](https://nodejs.org/))
- **npm** 7.0 or higher (comes with Node.js)
- **Git** for version control ([Download](https://git-scm.com/))
- **Visual Studio Code** (recommended) ([Download](https://code.visualstudio.com/))

#### Required Accounts & Keys
- **Riot Games Developer Account** ([Sign up](https://developer.riotgames.com/))
- **GitHub Account** for version control
- **Twitch Developer Account** (optional, for extended features)

## 🚀 Initial Setup

### 1. Clone the Repository
```bash
git clone https://github.com/NadaBa1202/seneca.git
cd seneca
```

### 2. Project Structure Overview
```
seneca/
├── League of legends helper/          # Main application directory
│   ├── seneca/                       # Frontend React application
│   │   └── react-vite-app/          # Vite + React setup
│   │       ├── src/                 # Source files
│   │       │   ├── components/      # React components
│   │       │   ├── App.jsx         # Main app component
│   │       │   └── main.jsx        # Entry point
│   │       ├── public/             # Static assets
│   │       ├── package.json        # Frontend dependencies
│   │       └── vite.config.js      # Vite configuration
│   ├── proxy-server.js             # Express API server
│   ├── package.json                # Backend dependencies
│   └── README.md                   # Application-specific docs
├── chat_monitor/                    # Twitch chat monitoring
├── esports_analytics/              # Additional analytics tools
└── README.md                       # Main project documentation
```

### 3. Backend Setup
```bash
cd "League of legends helper"
npm install
```

#### Configure API Key
Edit `proxy-server.js` and add your Riot Games API key:

```javascript
// Find this line and replace with your key
const API_KEY = 'RGAPI-your-development-api-key-here';
```

#### Start Backend Server
```bash
node proxy-server.js
```
✅ Server should be running on `http://localhost:3001`

### 4. Frontend Setup
```bash
cd "seneca/react-vite-app"
npm install
```

#### Start Development Server
```bash
npm run dev
```
✅ Frontend should be running on `http://localhost:5179`

## 🔧 Development Tools

### Recommended VS Code Extensions
```json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json",
    "formulahendry.auto-rename-tag",
    "ms-vscode.vscode-eslint"
  ]
}
```

### ESLint Configuration
Create `.eslintrc.js` in the frontend directory:

```javascript
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: [
    'react',
    '@typescript-eslint',
  ],
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

### Prettier Configuration
Create `.prettierrc` in the project root:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

## 🔄 Development Workflow

### Daily Development Routine
1. **Pull latest changes**
   ```bash
   git pull origin main
   ```

2. **Start development servers**
   ```bash
   # Terminal 1 - Backend
   cd "League of legends helper"
   node proxy-server.js
   
   # Terminal 2 - Frontend
   cd "seneca/react-vite-app"
   npm run dev
   ```

3. **Make changes and test**
4. **Commit and push changes**
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   git push origin your-branch-name
   ```

### Branch Management
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Work on your feature
# ... make changes ...

# Commit changes
git add .
git commit -m "feat: implement your feature"

# Push branch
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 🧪 Testing

### Frontend Testing
```bash
cd "seneca/react-vite-app"

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run e2e tests
npm run test:e2e
```

### Backend Testing
```bash
cd "League of legends helper"

# Test API endpoints
curl http://localhost:3001/health
curl http://localhost:3001/api/account/MinouLion/EUW

# Run integration tests
npm test
```

### Manual Testing Checklist
- [ ] Frontend loads without errors
- [ ] Backend API responds to health check
- [ ] Player lookup functionality works
- [ ] Champion assistant responds
- [ ] Twitch chat monitoring connects
- [ ] All navigation works correctly
- [ ] Responsive design works on mobile
- [ ] Error handling displays properly

## 🐛 Debugging

### Frontend Debugging
1. **Browser DevTools**
   - Open Chrome/Firefox DevTools (F12)
   - Check Console for errors
   - Network tab for API calls
   - React DevTools extension

2. **Vite Debug Mode**
   ```bash
   DEBUG=vite:* npm run dev
   ```

3. **React Error Boundaries**
   Components have error boundaries for graceful error handling

### Backend Debugging
1. **Enable Debug Logging**
   ```javascript
   // Add to proxy-server.js
   const DEBUG = process.env.DEBUG || false;
   
   if (DEBUG) {
     console.log('Debug mode enabled');
   }
   ```

2. **Use Node.js Debugger**
   ```bash
   node --inspect proxy-server.js
   ```

3. **Check API Responses**
   ```bash
   curl -v http://localhost:3001/api/account/test/EUW
   ```

## 📊 Performance Monitoring

### Development Performance
```bash
# Analyze bundle size
cd "seneca/react-vite-app"
npm run build
npm run analyze

# Monitor backend performance
cd "League of legends helper"
npm install --save-dev clinic
clinic doctor -- node proxy-server.js
```

### Memory Usage
```bash
# Monitor Node.js memory
node --inspect --max-old-space-size=4096 proxy-server.js
```

## 🔒 Environment Configuration

### Development Environment Variables
Create `.env.development` in the frontend directory:

```env
VITE_API_URL=http://localhost:3001
VITE_APP_TITLE=League Analytics - Development
VITE_DEBUG=true
```

### Backend Environment
Create `.env` in the backend directory:

```env
NODE_ENV=development
PORT=3001
RIOT_API_KEY=your-development-key
DEBUG=true
FRONTEND_URL=http://localhost:5179
```

## 📝 Code Style Guidelines

### JavaScript/React Conventions
```javascript
// Use functional components with hooks
import { useState, useEffect } from 'react';

const PlayerLookup = ({ onPlayerFound }) => {
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(false);

  // Use descriptive variable names
  const handlePlayerSearch = async (gameName, tagLine) => {
    setLoading(true);
    try {
      const playerData = await fetchPlayerData(gameName, tagLine);
      setPlayer(playerData);
      onPlayerFound(playerData);
    } catch (error) {
      console.error('Player search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="player-lookup">
      {/* Component JSX */}
    </div>
  );
};

export default PlayerLookup;
```

### CSS Conventions
```css
/* Use BEM methodology */
.player-lookup {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.player-lookup__input {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.player-lookup__button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.player-lookup__button:hover {
  background: #2563eb;
}

.player-lookup__button--loading {
  opacity: 0.7;
  cursor: not-allowed;
}
```

## 🚀 Build and Deploy

### Frontend Build
```bash
cd "seneca/react-vite-app"
npm run build

# Preview production build
npm run preview
```

### Backend Production Mode
```bash
cd "League of legends helper"
NODE_ENV=production node proxy-server.js
```

## 📚 Additional Resources

### Documentation Links
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Express.js Documentation](https://expressjs.com/)
- [Riot Games API Documentation](https://developer.riotgames.com/docs/lol)

### Learning Resources
- [React Tutorial](https://react.dev/learn)
- [Modern JavaScript](https://javascript.info/)
- [CSS Grid and Flexbox](https://css-tricks.com/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)

### Community
- [League of Legends subreddit](https://reddit.com/r/leagueoflegends)
- [React community](https://react.dev/community)
- [Riot API community](https://discord.gg/riotgamesapi)

## 🆘 Getting Help

### Common Issues and Solutions

1. **Port already in use**
   ```bash
   # Find process using port
   lsof -i :3001
   # Kill process
   kill -9 <PID>
   ```

2. **npm install fails**
   ```bash
   # Clear npm cache
   npm cache clean --force
   # Delete node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **API key issues**
   - Verify key is correct in proxy-server.js
   - Check key hasn't expired
   - Ensure proper rate limiting

4. **CORS errors**
   - Verify backend is running
   - Check proxy configuration
   - Ensure frontend is calling correct backend URL

### Getting Support
- Check existing GitHub issues
- Create new issue with detailed error information
- Include environment details and steps to reproduce
- Join development Discord server (if available)

---

**Happy coding! 🎮✨**