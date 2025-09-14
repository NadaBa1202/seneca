require('dotenv').config();
const express = require('express');
const cors = require('cors');
const RiotApiService = require('./services/riot_api');
const DragontailDataService = require('./services/dragontail_data');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize services
const riotApi = new RiotApiService();
const dragontailData = new DragontailDataService();

// API Routes

// Search champions
app.get('/api/champions/search', async (req, res) => {
    try {
        const { query } = req.query;
        if (!query) {
            const allChampions = await dragontailData.getAllChampions();
            return res.json(allChampions);
        }
        
        const champions = await dragontailData.searchChampions(query);
        res.json(champions);
    } catch (error) {
        console.error('Error searching champions:', error);
        res.status(500).json({ error: 'Failed to search champions' });
    }
});

// Get champion details
app.get('/api/champions/:championId', async (req, res) => {
    try {
        const { championId } = req.params;
        const champion = await dragontailData.getChampion(championId);
        const abilities = await dragontailData.getChampionAbilities(championId);
        const stats = await dragontailData.getChampionStats(championId);
        
        res.json({
            ...champion,
            abilities,
            detailedStats: stats
        });
    } catch (error) {
        console.error('Error fetching champion:', error);
        res.status(404).json({ error: 'Champion not found' });
    }
});

// Search items
app.get('/api/items/search', async (req, res) => {
    try {
        const { query } = req.query;
        const items = await dragontailData.searchItems(query || '');
        res.json(items.slice(0, 20)); // Limit to 20 results
    } catch (error) {
        console.error('Error searching items:', error);
        res.status(500).json({ error: 'Failed to search items' });
    }
});

// Get item details with build path
app.get('/api/items/:itemId', async (req, res) => {
    try {
        const { itemId } = req.params;
        const buildPath = await dragontailData.getItemBuildPath(itemId);
        res.json(buildPath);
    } catch (error) {
        console.error('Error fetching item:', error);
        res.status(404).json({ error: 'Item not found' });
    }
});

// Search player
app.get('/api/player/:summonerName', async (req, res) => {
    try {
        const { summonerName } = req.params;
        const { region = 'na1' } = req.query;
        
        const profile = await riotApi.getPlayerProfile(summonerName, region);
        res.json(profile);
    } catch (error) {
        console.error('Error fetching player:', error);
        if (error.message.includes('404')) {
            res.status(404).json({ error: 'Player not found' });
        } else {
            res.status(500).json({ error: 'Failed to fetch player data' });
        }
    }
});

// Get current game for player
app.get('/api/player/:summonerName/current-game', async (req, res) => {
    try {
        const { summonerName } = req.params;
        const { region = 'na1' } = req.query;
        
        const summoner = await riotApi.getSummonerByName(summonerName, region);
        const currentGame = await riotApi.getCurrentGame(summoner.id, region);
        
        if (!currentGame) {
            return res.json({ inGame: false });
        }
        
        res.json({ inGame: true, gameData: currentGame });
    } catch (error) {
        console.error('Error fetching current game:', error);
        res.status(500).json({ error: 'Failed to fetch current game data' });
    }
});

// Get match details
app.get('/api/match/:matchId', async (req, res) => {
    try {
        const { matchId } = req.params;
        const { region = 'americas' } = req.query;
        
        const match = await riotApi.getMatchDetails(matchId, region);
        res.json(match);
    } catch (error) {
        console.error('Error fetching match:', error);
        res.status(404).json({ error: 'Match not found' });
    }
});

// League knowledge endpoint for chat
app.post('/api/league/query', async (req, res) => {
    try {
        const { question } = req.body;
        
        // Simple keyword-based responses - could be enhanced with NLP
        const lowerQuestion = question.toLowerCase();
        
        let response = null;
        
        if (lowerQuestion.includes('champion')) {
            // Extract champion name if mentioned
            const champions = await dragontailData.getAllChampions();
            const mentionedChampion = champions.find(champ => 
                lowerQuestion.includes(champ.name.toLowerCase())
            );
            
            if (mentionedChampion) {
                const details = await dragontailData.getChampion(mentionedChampion.id);
                const abilities = await dragontailData.getChampionAbilities(mentionedChampion.id);
                
                response = {
                    type: 'champion_info',
                    champion: mentionedChampion.name,
                    data: {
                        overview: `${details.name} - ${details.title}. Tags: ${details.tags.join(', ')}. Difficulty: ${details.info.difficulty}/10`,
                        lore: details.lore,
                        abilities: abilities.spells.map(spell => `${spell.name}: ${spell.description}`),
                        tips: details.allytips
                    }
                };
            }
        } else if (lowerQuestion.includes('item')) {
            // Search for items
            const searchTerm = lowerQuestion.replace(/.*item.*?(\w+).*/, '$1');
            const items = await dragontailData.searchItems(searchTerm);
            
            if (items.length > 0) {
                const item = items[0];
                const buildPath = await dragontailData.getItemBuildPath(item.id);
                
                response = {
                    type: 'item_info',
                    item: item.name,
                    data: {
                        description: item.description,
                        stats: item.stats,
                        cost: item.gold,
                        buildPath: {
                            from: buildPath.buildsFrom.map(i => i.name),
                            into: buildPath.buildsInto.map(i => i.name)
                        }
                    }
                };
            }
        }
        
        if (!response) {
            response = {
                type: 'general',
                message: "I can help you with champion information, item details, and general League of Legends questions. Try asking about a specific champion or item!"
            };
        }
        
        res.json(response);
    } catch (error) {
        console.error('Error processing league query:', error);
        res.status(500).json({ error: 'Failed to process query' });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    console.log(`🚀 League API server running on port ${PORT}`);
    console.log(`📊 Dragontail data service initialized`);
    console.log(`🎮 Riot API service configured`);
    console.log(`💡 Remember to set your RIOT_API_KEY in .env file`);
});