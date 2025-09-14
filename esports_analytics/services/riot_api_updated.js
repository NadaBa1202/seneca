const axios = require('axios');

class RiotApiService {
    constructor(apiKey = null) {
        this.apiKey = apiKey || process.env.RIOT_API_KEY || 'YOUR_API_KEY_HERE';
        this.baseUrls = {
            na1: 'https://na1.api.riotgames.com',
            americas: 'https://americas.api.riotgames.com',
            kr: 'https://kr.api.riotgames.com',
            euw1: 'https://euw1.api.riotgames.com'
        };
        this.defaultRegion = 'na1';
        this.defaultCluster = 'americas';
        
        // Create axios instance with default headers
        this.http = axios.create({
            timeout: 15000,
            headers: {
                'X-Riot-Token': this.apiKey
            }
        });

        // Add response interceptor for rate limiting
        this.http.interceptors.response.use(
            response => response,
            error => {
                if (error.response?.status === 429) {
                    console.warn('Rate limit exceeded. Please wait before making more requests.');
                }
                throw error;
            }
        );
    }

    /**
     * Get account by Riot ID (gameName#tagLine) - NEW PREFERRED METHOD
     */
    async getAccountByRiotId(gameName, tagLine, cluster = this.defaultCluster) {
        try {
            const baseUrl = this.baseUrls[cluster];
            const url = `${baseUrl}/riot/account/v1/accounts/by-riot-id/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching account by Riot ID:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch account: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get summoner by PUUID
     */
    async getSummonerByPuuid(puuid, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/summoner/v4/summoners/by-puuid/${puuid}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching summoner by PUUID:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch summoner: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get ranked information for a summoner by PUUID
     */
    async getRankedInfo(puuid, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/league/v4/entries/by-puuid/${puuid}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching ranked info:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch ranked info: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get champion mastery for summoner by PUUID
     */
    async getChampionMastery(puuid, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/champion-mastery/v4/champion-masteries/by-puuid/${puuid}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching champion mastery:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch champion mastery: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get top champion masteries
     */
    async getTopChampionMastery(puuid, count = 10, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/champion-mastery/v4/champion-masteries/by-puuid/${puuid}/top?count=${count}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching top champion mastery:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch top champion mastery: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get mastery for specific champion
     */
    async getChampionMasteryById(puuid, championId, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/champion-mastery/v4/champion-masteries/by-puuid/${puuid}/by-champion/${championId}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching champion mastery by ID:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch champion mastery: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get mastery score
     */
    async getMasteryScore(puuid, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/champion-mastery/v4/scores/by-puuid/${puuid}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching mastery score:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch mastery score: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get match history
     */
    async getMatchHistory(puuid, count = 20, cluster = this.defaultCluster) {
        try {
            const baseUrl = this.baseUrls[cluster];
            const url = `${baseUrl}/lol/match/v5/matches/by-puuid/${puuid}/ids?count=${count}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching match history:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch match history: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get match details
     */
    async getMatchDetails(matchId, cluster = this.defaultCluster) {
        try {
            const baseUrl = this.baseUrls[cluster];
            const url = `${baseUrl}/lol/match/v5/matches/${matchId}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching match details:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch match details: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get current game info by PUUID
     */
    async getCurrentGame(puuid, region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/spectator/v5/active-games/by-summoner/${puuid}`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            if (error.response?.status === 404) {
                return null; // Player not in game
            }
            console.error('Error fetching current game:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch current game: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get champion rotations
     */
    async getChampionRotations(region = this.defaultRegion) {
        try {
            const baseUrl = this.baseUrls[region];
            const url = `${baseUrl}/lol/platform/v3/champion-rotations`;
            
            const response = await this.http.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching champion rotations:', error.response?.status, error.response?.data || error.message);
            throw new Error(`Failed to fetch champion rotations: ${error.response?.data?.status?.message || error.message}`);
        }
    }

    /**
     * Get comprehensive player information
     */
    async getPlayerInfo(gameName, tagLine) {
        try {
            console.log(`🔍 Getting player info for ${gameName}#${tagLine}`);
            
            // Step 1: Get account by Riot ID
            const account = await this.getAccountByRiotId(gameName, tagLine);
            console.log(`✅ Found account: ${account.gameName}#${account.tagLine}`);
            
            // Step 2: Get summoner info
            const summoner = await this.getSummonerByPuuid(account.puuid);
            console.log(`✅ Found summoner: Level ${summoner.summonerLevel}`);
            
            // Step 3: Get ranked info
            let rankedInfo = [];
            try {
                rankedInfo = await this.getRankedInfo(account.puuid);
                console.log(`✅ Found ${rankedInfo.length} ranked entries`);
            } catch (error) {
                console.log(`⚠️ No ranked info found`);
            }
            
            // Step 4: Get champion mastery
            let masteries = [];
            let masteryScore = 0;
            try {
                masteries = await this.getTopChampionMastery(account.puuid, 5);
                masteryScore = await this.getMasteryScore(account.puuid);
                console.log(`✅ Found ${masteries.length} top masteries, total score: ${masteryScore}`);
            } catch (error) {
                console.log(`⚠️ No mastery info found`);
            }
            
            // Step 5: Get recent matches
            let recentMatches = [];
            try {
                recentMatches = await this.getMatchHistory(account.puuid, 10);
                console.log(`✅ Found ${recentMatches.length} recent matches`);
            } catch (error) {
                console.log(`⚠️ No match history found`);
            }

            // Step 6: Check if currently in game
            let currentGame = null;
            try {
                currentGame = await this.getCurrentGame(account.puuid);
                if (currentGame) {
                    console.log(`🎮 Player is currently in game!`);
                }
            } catch (error) {
                console.log(`⚠️ Player not currently in game`);
            }
            
            return {
                account,
                summoner,
                rankedInfo,
                masteries,
                masteryScore,
                recentMatches,
                currentGame
            };
        } catch (error) {
            console.error('Failed to get comprehensive player info:', error.message);
            throw new Error(`Failed to get player info: ${error.message}`);
        }
    }

    /**
     * Quick player lookup by name (tries to find summoner)
     */
    async findPlayer(searchTerm) {
        // Try to parse as gameName#tagLine
        if (searchTerm.includes('#')) {
            const [gameName, tagLine] = searchTerm.split('#');
            return this.getPlayerInfo(gameName.trim(), tagLine.trim());
        } else {
            // Try with default tag
            return this.getPlayerInfo(searchTerm.trim(), 'NA1');
        }
    }
}

module.exports = RiotApiService;