const axios = require('axios');

class RiotApiService {
    constructor() {
        this.apiKey = process.env.RIOT_API_KEY || 'YOUR_API_KEY_HERE';
        this.baseUrls = {
            na1: 'https://na1.api.riotgames.com',
            americas: 'https://americas.api.riotgames.com',
            kr: 'https://kr.api.riotgames.com',
            euw1: 'https://euw1.api.riotgames.com'
        };
        this.defaultRegion = 'na1';
        
        // Create axios instance with default headers
        this.http = axios.create({
            timeout: 10000,
            headers: {
                'X-Riot-Token': this.apiKey
            }
        });
    }

    /**
     * Get summoner information by name
     * @param {string} summonerName - The summoner name to search for
     * @param {string} region - The region to search in (optional)
     * @returns {Promise} Summoner data
     */
    async getSummonerByName(summonerName, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region] || this.baseUrls[this.defaultRegion];
            const url = `${baseUrl}/lol/summoner/v4/summoners/by-name/${encodeURIComponent(summonerName)}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching summoner:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch summoner: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get ranked information for a summoner
     * @param {string} summonerId - The summoner ID
     * @param {string} region - The region to search in (optional)
     * @returns {Promise} Ranked data
     */
    async getRankedInfo(summonerId, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region] || this.baseUrls[this.defaultRegion];
            const url = `${baseUrl}/lol/league/v4/entries/by-summoner/${summonerId}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching ranked info:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch ranked info: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get match history for a summoner
     * @param {string} puuid - The summoner PUUID
     * @param {number} count - Number of matches to retrieve (max 20)
     * @param {string} region - The regional routing value (americas, asia, europe)
     * @returns {Promise} Match history
     */
    async getMatchHistory(puuid, count = 10, region = 'americas') {
        try {
            const baseUrl = this.baseUrls[region] || this.baseUrls['americas'];
            const url = `${baseUrl}/lol/match/v5/matches/by-puuid/${puuid}/ids?start=0&count=${Math.min(count, 20)}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching match history:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch match history: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get detailed match information
     * @param {string} matchId - The match ID
     * @param {string} region - The regional routing value (americas, asia, europe)
     * @returns {Promise} Match details
     */
    async getMatchDetails(matchId, region = 'americas') {
        try {
            const baseUrl = this.baseUrls[region] || this.baseUrls['americas'];
            const url = `${baseUrl}/lol/match/v5/matches/${matchId}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching match details:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch match details: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get current game information for a summoner
     * @param {string} summonerId - The summoner ID
     * @param {string} region - The region to search in (optional)
     * @returns {Promise} Current game data or null if not in game
     */
    async getCurrentGame(summonerId, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region] || this.baseUrls[this.defaultRegion];
            const url = `${baseUrl}/lol/spectator/v4/active-games/by-summoner/${summonerId}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            if (error.response?.status === 404) {
                return null; // Not in game
            }
            console.error('Error fetching current game:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch current game: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get champion mastery for a summoner
     * @param {string} summonerId - The summoner ID
     * @param {string} region - The region to search in (optional)
     * @returns {Promise} Champion mastery data
     */
    async getChampionMastery(summonerId, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region] || this.baseUrls[this.defaultRegion];
            const url = `${baseUrl}/lol/champion-mastery/v4/champion-masteries/by-summoner/${summonerId}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching champion mastery:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch champion mastery: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Search for summoners with partial name match
     * @param {string} partialName - Partial summoner name
     * @param {string} region - The region to search in (optional)
     * @returns {Promise} Array of potential matches
     */
    async searchSummoners(partialName, region = this.defaultRegion) {
        // Note: Riot API doesn't have a search endpoint, so we'll implement
        // exact match for now. In a production app, you'd want to implement
        // a database of summoner names for fuzzy searching.
        try {
            const summoner = await this.getSummonerByName(partialName, region);
            return [summoner];
        } catch (error) {
            return []; // No exact match found
        }
    }

    /**
     * Get comprehensive player profile
     * @param {string} summonerName - The summoner name
     * @param {string} region - The region to search in (optional)
     * @returns {Promise} Complete player profile
     */
    async getPlayerProfile(summonerName, region = this.defaultRegion) {
        try {
            // Get basic summoner info
            const summoner = await this.getSummonerByName(summonerName, region);
            
            // Get ranked info
            const ranked = await this.getRankedInfo(summoner.id, region);
            
            // Get champion mastery
            const mastery = await this.getChampionMastery(summoner.id, region);
            
            // Get current game (if any)
            const currentGame = await this.getCurrentGame(summoner.id, region);
            
            // Get recent match history
            const regionalGroup = this.getRegionalGroup(region);
            const recentMatches = await this.getMatchHistory(summoner.puuid, 5, regionalGroup);
            
            return {
                summoner,
                ranked,
                mastery: mastery.slice(0, 10), // Top 10 champions
                currentGame,
                recentMatches
            };
        } catch (error) {
            console.error('Error fetching player profile:', error);
            throw new Error(`Failed to fetch player profile: ${error.message}`);
        }
    }

    /**
     * Get regional routing value for match API
     * @param {string} region - Platform routing value
     * @returns {string} Regional routing value
     */
    getRegionalGroup(region) {
        const mapping = {
            'na1': 'americas',
            'br1': 'americas',
            'la1': 'americas',
            'la2': 'americas',
            'euw1': 'europe',
            'eun1': 'europe',
            'tr1': 'europe',
            'ru': 'europe',
            'kr': 'asia',
            'jp1': 'asia'
        };
        return mapping[region] || 'americas';
    }
}

module.exports = RiotApiService;

module.exports = RiotApiService;