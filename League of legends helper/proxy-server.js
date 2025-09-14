const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
const PORT = 3001;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

const API_KEY = 'RGAPI-8994cf2c-4239-4033-b040-20e200c43151';

// Region mapping for different tag lines
const getRegionFromTag = (tagLine) => {
  const regionMap = {
    'NA1': 'na1',
    'EUW': 'euw1', 
    'EUW1': 'euw1',
    'EUNE': 'eun1',
    'KR': 'kr',
    'BR1': 'br1',
    'LA1': 'la1',
    'LA2': 'la2',
    'OC1': 'oc1',
    'RU': 'ru',
    'TR1': 'tr1',
    'JP1': 'jp1'
  };
  return regionMap[tagLine.toUpperCase()] || 'na1'; // Default to NA1 if unknown
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Riot API proxy server is running' });
});

// Get account by Riot ID
app.get('/api/account/:gameName/:tagLine', async (req, res) => {
  try {
    const { gameName, tagLine } = req.params;
    console.log(`🔍 Looking up account: ${gameName}#${tagLine}`);
    
    const url = `https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`;
    console.log(`📡 Making request to: ${url}`);
    
    const response = await fetch(url, {
      headers: {
        'X-Riot-Token': API_KEY
      }
    });
    
    console.log(`📊 Response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ API Error: ${response.status} - ${errorText}`);
      return res.status(response.status).json({ error: `Player not found: ${gameName}#${tagLine}` });
    }
    
    const data = await response.json();
    console.log(`✅ Found account: ${data.gameName}#${data.tagLine} (PUUID: ${data.puuid.substring(0, 8)}...)`);
    res.json(data);
  } catch (error) {
    console.error('❌ Account lookup error:', error);
    res.status(500).json({ error: 'Failed to fetch account data' });
  }
});

// Get summoner by PUUID (with region)
app.get('/api/summoner/:puuid/:region', async (req, res) => {
  try {
    const { puuid, region } = req.params;
    const response = await fetch(
      `https://${region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}`,
      {
        headers: {
          'X-Riot-Token': API_KEY
        }
      }
    );
    
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to get summoner information' });
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Summoner lookup error:', error);
    res.status(500).json({ error: 'Failed to fetch summoner data' });
  }
});

// Get summoner by PUUID (default region)
app.get('/api/summoner/:puuid', async (req, res) => {
  try {
    const { puuid } = req.params;
    const region = 'na1'; // Default region
    const response = await fetch(
      `https://${region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}`,
      {
        headers: {
          'X-Riot-Token': API_KEY
        }
      }
    );
    
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to get summoner information' });
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Summoner lookup error:', error);
    res.status(500).json({ error: 'Failed to fetch summoner data' });
  }
});

// Get ranked info by PUUID (with region)
app.get('/api/ranked/:puuid/:region', async (req, res) => {
  try {
    const { puuid, region } = req.params;
    const response = await fetch(
      `https://${region}.api.riotgames.com/lol/league/v4/entries/by-puuid/${puuid}`,
      {
        headers: {
          'X-Riot-Token': API_KEY
        }
      }
    );
    
    if (!response.ok) {
      return res.status(200).json([]); // Return empty array if no ranked data
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Ranked lookup error:', error);
    res.status(200).json([]); // Return empty array on error
  }
});

// Get ranked info by PUUID (default region)
app.get('/api/ranked/:puuid', async (req, res) => {
  try {
    const { puuid } = req.params;
    const region = 'na1'; // Default region
    const response = await fetch(
      `https://${region}.api.riotgames.com/lol/league/v4/entries/by-puuid/${puuid}`,
      {
        headers: {
          'X-Riot-Token': API_KEY
        }
      }
    );
    
    if (!response.ok) {
      return res.status(200).json([]); // Return empty array if no ranked data
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Ranked lookup error:', error);
    res.status(200).json([]); // Return empty array on error
  }
});

// Get champion mastery by PUUID (with region)
app.get('/api/mastery/:puuid/:region', async (req, res) => {
  try {
    const { puuid, region } = req.params;
    const [masteryResponse, scoreResponse] = await Promise.all([
      fetch(
        `https://${region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/${puuid}/top?count=5`,
        { headers: { 'X-Riot-Token': API_KEY } }
      ),
      fetch(
        `https://${region}.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/${puuid}`,
        { headers: { 'X-Riot-Token': API_KEY } }
      )
    ]);
    
    const masteries = masteryResponse.ok ? await masteryResponse.json() : [];
    const masteryScore = scoreResponse.ok ? await scoreResponse.json() : 0;
    
    res.json({ masteries, masteryScore });
  } catch (error) {
    console.error('Mastery lookup error:', error);
    res.status(200).json({ masteries: [], masteryScore: 0 });
  }
});

// Get champion mastery by PUUID (default region)
app.get('/api/mastery/:puuid', async (req, res) => {
  try {
    const { puuid } = req.params;
    const region = 'na1'; // Default region
    const [masteryResponse, scoreResponse] = await Promise.all([
      fetch(
        `https://${region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/${puuid}/top?count=5`,
        { headers: { 'X-Riot-Token': API_KEY } }
      ),
      fetch(
        `https://${region}.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/${puuid}`,
        { headers: { 'X-Riot-Token': API_KEY } }
      )
    ]);
    
    const masteries = masteryResponse.ok ? await masteryResponse.json() : [];
    const masteryScore = scoreResponse.ok ? await scoreResponse.json() : 0;
    
    res.json({ masteries, masteryScore });
  } catch (error) {
    console.error('Mastery lookup error:', error);
    res.status(200).json({ masteries: [], masteryScore: 0 });
  }
});

// Get recent matches by PUUID
app.get('/api/matches/:puuid', async (req, res) => {
  try {
    const { puuid } = req.params;
    const response = await fetch(
      `https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/${puuid}/ids?count=5`,
      {
        headers: {
          'X-Riot-Token': API_KEY
        }
      }
    );
    
    if (!response.ok) {
      return res.status(200).json([]);
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Matches lookup error:', error);
    res.status(200).json([]);
  }
});

// Get current game by PUUID (with region)
app.get('/api/current-game/:puuid/:region', async (req, res) => {
  try {
    const { puuid, region } = req.params;
    const response = await fetch(
      `https://${region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/${puuid}`,
      {
        headers: {
          'X-Riot-Token': API_KEY
        }
      }
    );
    
    if (!response.ok) {
      return res.status(200).json(null); // Player not in game
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Current game lookup error:', error);
    res.status(200).json(null); // Player not in game on error
  }
});

// Get current game by PUUID (default region)
app.get('/api/current-game/:puuid', async (req, res) => {
  try {
    const { puuid } = req.params;
    const region = 'na1'; // Default region
    const response = await fetch(
      `https://${region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/${puuid}`,
      {
        headers: {
          'X-Riot-Token': API_KEY
        }
      }
    );
    
    if (!response.ok) {
      return res.status(200).json(null); // Player not in game
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Current game lookup error:', error);
    res.status(200).json(null); // Player not in game on error
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Riot API proxy server running on http://localhost:${PORT}`);
  console.log(`🔑 Using API key: ${API_KEY.substring(0, 10)}...`);
});