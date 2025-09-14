/**
 * Simple API server to serve Dragontail champion data to the React app
 * This bridges the existing Python dragontail data with the JavaScript frontend
 */

const express = require('express')
const cors = require('cors')
const path = require('path')
const fs = require('fs')

const app = express()
const PORT = 3001

// Enable CORS for the React app
app.use(cors({
  origin: 'http://localhost:5173', // Vite dev server
  credentials: true
}))

app.use(express.json())

// Serve static Dragontail files
app.use('/15.18.1', express.static(path.join(__dirname, '../../15.18.1')))

// Champions API endpoint
app.get('/api/champions', async (req, res) => {
  try {
    // Try to load from the actual dragontail data
    const championDataPath = path.join(__dirname, '../../15.18.1/data/en_US/champion.json')
    
    if (fs.existsSync(championDataPath)) {
      const championData = JSON.parse(fs.readFileSync(championDataPath, 'utf8'))
      
      // Load detailed data for each champion
      const championsWithDetails = {}
      const championsDir = path.join(__dirname, '../../15.18.1/data/en_US/champion')
      
      for (const [key, champion] of Object.entries(championData.data || {})) {
        const detailPath = path.join(championsDir, `${key}.json`)
        if (fs.existsSync(detailPath)) {
          try {
            const detailData = JSON.parse(fs.readFileSync(detailPath, 'utf8'))
            championsWithDetails[key] = detailData.data[key]
          } catch (error) {
            console.warn(`Failed to load details for ${key}:`, error.message)
            championsWithDetails[key] = champion
          }
        } else {
          championsWithDetails[key] = champion
        }
      }
      
      res.json({
        champions: championsWithDetails,
        version: '15.18.1',
        source: 'dragontail'
      })
    } else {
      // Fallback response if dragontail data is not available
      res.json({
        champions: {},
        version: '15.18.1',
        source: 'fallback',
        error: 'Dragontail data not found'
      })
    }
  } catch (error) {
    console.error('Error serving champions:', error)
    res.status(500).json({
      error: 'Failed to load champion data',
      message: error.message
    })
  }
})

// Player API endpoint (mock for now, would connect to Python backend)
app.get('/api/player/:summonerName', async (req, res) => {
  const { summonerName } = req.params
  
  // This would normally call the Python backend's Riot API integration
  // For now, return enhanced mock data
  res.json({
    name: summonerName,
    level: Math.floor(Math.random() * 300) + 50,
    rank: {
      tier: ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster', 'Challenger'][Math.floor(Math.random() * 9)],
      rank: ['IV', 'III', 'II', 'I'][Math.floor(Math.random() * 4)],
      lp: Math.floor(Math.random() * 100),
      winRate: (Math.random() * 30 + 50).toFixed(1)
    },
    currentMatch: Math.random() > 0.7 ? {
      gameMode: 'Ranked Solo/Duo',
      championName: ['Zed', 'Yasuo', 'Ahri', 'Jinx', 'Thresh'][Math.floor(Math.random() * 5)],
      gameLength: Math.floor(Math.random() * 1800) + 300 // 5-35 minutes
    } : null,
    recentMatches: Array.from({ length: 5 }, () => ({
      championName: ['Zed', 'Yasuo', 'Ahri', 'Jinx', 'Thresh', 'Lee Sin', 'Katarina'][Math.floor(Math.random() * 7)],
      result: Math.random() > 0.5 ? 'Victory' : 'Defeat',
      kda: `${Math.floor(Math.random() * 15) + 1}/${Math.floor(Math.random() * 8) + 1}/${Math.floor(Math.random() * 12) + 1}`
    })),
    source: 'mock-api'
  })
})

// Live matches API endpoint
app.get('/api/live-matches', async (req, res) => {
  // This would normally fetch from Riot's spectator API via Python backend
  res.json({
    matches: [
      {
        rank: 'Challenger',
        region: 'KR',
        gameLength: Math.floor(Math.random() * 1800) + 300,
        participants: [
          { summonerName: 'Faker', championName: 'Azir' },
          { summonerName: 'ShowMaker', championName: 'LeBlanc' },
          { summonerName: 'Chovy', championName: 'Yasuo' },
          { summonerName: 'Doinb', championName: 'Orianna' },
          { summonerName: 'Caps', championName: 'Syndra' }
        ]
      },
      {
        rank: 'Grandmaster',
        region: 'NA',
        gameLength: Math.floor(Math.random() * 1800) + 300,
        participants: [
          { summonerName: 'Doublelift', championName: 'Jinx' },
          { summonerName: 'Sneaky', championName: 'Kai\'Sa' },
          { summonerName: 'Bjergsen', championName: 'Zed' },
          { summonerName: 'Jensen', championName: 'Kassadin' },
          { summonerName: 'CoreJJ', championName: 'Thresh' }
        ]
      }
    ],
    source: 'mock-api'
  })
})

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    dragontailAvailable: fs.existsSync(path.join(__dirname, '../../15.18.1/data/en_US/champion.json'))
  })
})

// Start server
app.listen(PORT, () => {
  console.log(`🚀 League Data API Server running on http://localhost:${PORT}`)
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`)
  console.log(`🏆 Champions endpoint: http://localhost:${PORT}/api/champions`)
  
  // Check if dragontail data is available
  const dragontailPath = path.join(__dirname, '../../15.18.1/data/en_US/champion.json')
  if (fs.existsSync(dragontailPath)) {
    console.log(`✅ Dragontail data found at ${dragontailPath}`)
  } else {
    console.log(`⚠️  Dragontail data not found at ${dragontailPath}`)
    console.log(`   The API will serve fallback data instead`)
  }
})

module.exports = app