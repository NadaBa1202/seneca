const express = require('express');
const cors = require('cors');
const RiotApiService = require('./services/riot_api_updated');

const app = express();
const PORT = process.env.PORT || 3001;

// Initialize services
const riotApi = new RiotApiService(); // Will use API key from environment or user input

// Middleware
app.use(cors());
app.use(express.json());

// Request logging
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        services: {
            riotApi: !!riotApi.apiKey && riotApi.apiKey !== 'YOUR_API_KEY_HERE',
            dragontail: true
        }
    });
});

// Set API key endpoint
app.post('/api/set-api-key', (req, res) => {
    try {
        const { apiKey } = req.body;
        if (!apiKey) {
            return res.status(400).json({ error: 'API key is required' });
        }
        
        riotApi.apiKey = apiKey;
        riotApi.http.defaults.headers['X-Riot-Token'] = apiKey;
        
        console.log('🔑 API key updated');
        res.json({ success: true, message: 'API key updated successfully' });
    } catch (error) {
        console.error('Error setting API key:', error);
        res.status(500).json({ error: 'Failed to set API key' });
    }
});

// Get comprehensive player information
app.get('/api/player/:gameName/:tagLine', async (req, res) => {
    try {
        const { gameName, tagLine } = req.params;
        console.log(`🔍 Looking up player: ${gameName}#${tagLine}`);
        
        const playerInfo = await riotApi.getPlayerInfo(gameName, tagLine);
        res.json(playerInfo);
    } catch (error) {
        console.error('Player lookup error:', error);
        res.status(404).json({ 
            error: error.message,
            details: 'Player not found or API error'
        });
    }
});

// Get player match history
app.get('/api/player/:gameName/:tagLine/matches', async (req, res) => {
    try {
        const { gameName, tagLine } = req.params;
        const count = parseInt(req.query.count) || 20;
        
        console.log(`📊 Getting match history for ${gameName}#${tagLine}`);
        
        // First get account to get PUUID
        const account = await riotApi.getAccountByRiotId(gameName, tagLine);
        const matches = await riotApi.getMatchHistory(account.puuid, count);
        
        res.json(matches);
    } catch (error) {
        console.error('Match history error:', error);
        res.status(404).json({ 
            error: error.message,
            details: 'Could not retrieve match history'
        });
    }
});

// Get match details
app.get('/api/match/:matchId', async (req, res) => {
    try {
        const { matchId } = req.params;
        console.log(`🎮 Getting match details for ${matchId}`);
        
        const matchDetails = await riotApi.getMatchDetails(matchId);
        res.json(matchDetails);
    } catch (error) {
        console.error('Match details error:', error);
        res.status(404).json({ 
            error: error.message,
            details: 'Match not found'
        });
    }
});

// Get current game
app.get('/api/player/:gameName/:tagLine/current-game', async (req, res) => {
    try {
        const { gameName, tagLine } = req.params;
        console.log(`🎮 Checking current game for ${gameName}#${tagLine}`);
        
        // First get account to get PUUID
        const account = await riotApi.getAccountByRiotId(gameName, tagLine);
        const currentGame = await riotApi.getCurrentGame(account.puuid);
        
        if (currentGame) {
            res.json(currentGame);
        } else {
            res.status(404).json({ error: 'Player not currently in game' });
        }
    } catch (error) {
        console.error('Current game error:', error);
        res.status(404).json({ 
            error: error.message,
            details: 'Could not check current game'
        });
    }
});

// Get champion rotation
app.get('/api/champion-rotation', async (req, res) => {
    try {
        console.log('📅 Getting champion rotation');
        const rotation = await riotApi.getChampionRotations();
        res.json(rotation);
    } catch (error) {
        console.error('Champion rotation error:', error);
        res.status(500).json({ 
            error: error.message,
            details: 'Could not get champion rotation'
        });
    }
});

// Get featured games
app.get('/api/featured-games', async (req, res) => {
    try {
        console.log('🌟 Getting featured games');
        const featuredGames = await riotApi.getFeaturedGames();
        res.json(featuredGames);
    } catch (error) {
        console.error('Featured games error:', error);
        res.status(500).json({ 
            error: error.message,
            details: 'Could not get featured games'
        });
    }
});

// Champion search endpoint - using simple mock for now
app.get('/api/champions/search', async (req, res) => {
    try {
        const { q: query } = req.query;
        if (!query) {
            return res.status(400).json({ error: 'Query parameter is required' });
        }
        
        // Mock response for now
        res.json([]);
    } catch (error) {
        console.error('Champion search error:', error);
        res.status(500).json({ 
            error: error.message,
            details: 'Could not search champions'
        });
    }
});

// Get champion details - mock for now
app.get('/api/champions/:championId', async (req, res) => {
    try {
        const { championId } = req.params;
        // Mock response
        res.json({ id: championId, name: championId });
    } catch (error) {
        console.error('Champion details error:', error);
        res.status(404).json({ 
            error: error.message,
            details: 'Champion not found'
        });
    }
});

// Get all champions - mock for now
app.get('/api/champions', async (req, res) => {
    try {
        // Mock response
        res.json([]);
    } catch (error) {
        console.error('Get all champions error:', error);
        res.status(500).json({ 
            error: error.message,
            details: 'Could not get champions'
        });
    }
});

// Item search endpoint - mock for now
app.get('/api/items/search', async (req, res) => {
    try {
        const { q: query } = req.query;
        if (!query) {
            return res.status(400).json({ error: 'Query parameter is required' });
        }
        
        // Mock response
        res.json([]);
    } catch (error) {
        console.error('Item search error:', error);
        res.status(500).json({ 
            error: error.message,
            details: 'Could not search items'
        });
    }
});

// Get all items - mock for now
app.get('/api/items', async (req, res) => {
    try {
        // Mock response
        res.json([]);
    } catch (error) {
        console.error('Get all items error:', error);
        res.status(500).json({ 
            error: error.message,
            details: 'Could not get items'
        });
    }
});

// Test API connectivity
app.get('/api/test', async (req, res) => {
    try {
        console.log('🧪 Testing API connectivity');
        
        // Test champion rotation (doesn't require player lookup)
        const rotation = await riotApi.getChampionRotations();
        
        res.json({
            success: true,
            message: 'API is working correctly',
            test: 'Champion rotation',
            data: rotation
        });
    } catch (error) {
        console.error('API test error:', error);
        res.status(500).json({ 
            success: false,
            error: error.message,
            details: 'API test failed - check your API key'
        });
    }
});

// Quick player search (tries multiple formats)
app.get('/api/search/:searchTerm', async (req, res) => {
    try {
        const { searchTerm } = req.params;
        console.log(`🔍 Quick search for: ${searchTerm}`);
        
        const playerInfo = await riotApi.findPlayer(searchTerm);
        res.json(playerInfo);
    } catch (error) {
        console.error('Quick search error:', error);
        res.status(404).json({ 
            error: error.message,
            details: 'Player not found. Try format: GameName#TAG'
        });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({ 
        error: 'Internal server error',
        details: error.message
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ 
        error: 'Endpoint not found',
        availableEndpoints: [
            'GET /health',
            'POST /api/set-api-key',
            'GET /api/player/:gameName/:tagLine',
            'GET /api/player/:gameName/:tagLine/matches',
            'GET /api/match/:matchId',
            'GET /api/player/:gameName/:tagLine/current-game',
            'GET /api/champion-rotation',
            'GET /api/featured-games',
            'GET /api/champions',
            'GET /api/champions/search?q=query',
            'GET /api/champions/:championId',
            'GET /api/items',
            'GET /api/items/search?q=query',
            'GET /api/test',
            'GET /api/search/:searchTerm'
        ]
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 League API Server running on port ${PORT}`);
    console.log(`📍 Health check: http://localhost:${PORT}/health`);
    console.log(`🔑 Set API key: POST http://localhost:${PORT}/api/set-api-key`);
    console.log(`🧪 Test API: http://localhost:${PORT}/api/test`);
    
    if (!riotApi.apiKey || riotApi.apiKey === 'YOUR_API_KEY_HERE') {
        console.log('⚠️  No Riot API key configured. Use POST /api/set-api-key to set it.');
    } else {
        console.log('✅ Riot API key configured');
    }
});

module.exports = app;