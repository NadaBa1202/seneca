// Player lookup service for React frontend
class PlayerLookupService {
    constructor() {
        this.apiBaseUrl = 'http://localhost:3001' // Our Express API server
    }

    async searchPlayer(gameName, tagLine = 'NA1') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/player/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`)
            
            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
            }
            
            return await response.json()
        } catch (error) {
            console.error('Player lookup error:', error)
            throw new Error(`Failed to find player: ${error.message}`)
        }
    }

    async getPlayerMatches(gameName, tagLine = 'NA1', count = 10) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/player/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}/matches?count=${count}`)
            
            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
            }
            
            return await response.json()
        } catch (error) {
            console.error('Match history error:', error)
            throw new Error(`Failed to get match history: ${error.message}`)
        }
    }

    async getChampionRotation() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/champion-rotation`)
            
            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
            }
            
            return await response.json()
        } catch (error) {
            console.error('Champion rotation error:', error)
            throw new Error(`Failed to get champion rotation: ${error.message}`)
        }
    }

    async getCurrentGame(gameName, tagLine = 'NA1') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/player/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}/current-game`)
            
            if (!response.ok) {
                if (response.status === 404) {
                    return null // Player not in game
                }
                const errorData = await response.json()
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
            }
            
            return await response.json()
        } catch (error) {
            console.error('Current game error:', error)
            if (error.message.includes('404')) {
                return null
            }
            throw new Error(`Failed to get current game: ${error.message}`)
        }
    }

    // Utility method to parse player search input
    parsePlayerInput(input) {
        if (input.includes('#')) {
            const [gameName, tagLine] = input.split('#')
            return {
                gameName: gameName.trim(),
                tagLine: tagLine.trim()
            }
        } else {
            return {
                gameName: input.trim(),
                tagLine: 'NA1'
            }
        }
    }

    // Enhanced player lookup with additional context
    async getFullPlayerProfile(input) {
        const { gameName, tagLine } = this.parsePlayerInput(input)
        
        try {
            console.log(`🔍 Looking up player: ${gameName}#${tagLine}`)
            
            // Get basic player info
            const playerInfo = await this.searchPlayer(gameName, tagLine)
            
            // Get current game if available
            let currentGame = null
            try {
                currentGame = await this.getCurrentGame(gameName, tagLine)
                if (currentGame) {
                    console.log(`🎮 Player is currently in game!`)
                }
            } catch (error) {
                console.log(`⚠️ Could not check current game status`)
            }
            
            // Get recent matches
            let recentMatches = []
            try {
                recentMatches = await this.getPlayerMatches(gameName, tagLine, 5)
                console.log(`📊 Found ${recentMatches.length} recent matches`)
            } catch (error) {
                console.log(`⚠️ Could not load match history`)
            }
            
            return {
                ...playerInfo,
                currentGame,
                recentMatches: recentMatches || []
            }
            
        } catch (error) {
            console.error('Full player profile error:', error)
            throw error
        }
    }

    // Format player data for display
    formatPlayerData(playerData) {
        if (!playerData) return null

        const { account, summoner, rankedInfo, masteries, masteryScore, currentGame, recentMatches } = playerData

        // Format ranked information
        const rankedSolo = rankedInfo?.find(entry => entry.queueType === 'RANKED_SOLO_5x5')
        const rankedFlex = rankedInfo?.find(entry => entry.queueType === 'RANKED_FLEX_SR')

        // Format champion masteries
        const topChampions = masteries?.slice(0, 5).map(mastery => ({
            championId: mastery.championId,
            championLevel: mastery.championLevel,
            championPoints: mastery.championPoints,
            tokensEarned: mastery.tokensEarned,
            chestGranted: mastery.chestGranted
        })) || []

        return {
            profile: {
                gameName: account?.gameName || 'Unknown',
                tagLine: account?.tagLine || 'NA1',
                summonerName: summoner?.name || account?.gameName || 'Unknown',
                summonerLevel: summoner?.summonerLevel || 1,
                profileIconId: summoner?.profileIconId || 0
            },
            ranked: {
                solo: rankedSolo ? {
                    tier: rankedSolo.tier,
                    rank: rankedSolo.rank,
                    leaguePoints: rankedSolo.leaguePoints,
                    wins: rankedSolo.wins,
                    losses: rankedSolo.losses,
                    winRate: Math.round((rankedSolo.wins / (rankedSolo.wins + rankedSolo.losses)) * 100)
                } : null,
                flex: rankedFlex ? {
                    tier: rankedFlex.tier,
                    rank: rankedFlex.rank,
                    leaguePoints: rankedFlex.leaguePoints,
                    wins: rankedFlex.wins,
                    losses: rankedFlex.losses,
                    winRate: Math.round((rankedFlex.wins / (rankedFlex.wins + rankedFlex.losses)) * 100)
                } : null
            },
            mastery: {
                totalScore: masteryScore || 0,
                topChampions
            },
            currentGame: currentGame ? {
                gameMode: currentGame.gameMode,
                gameType: currentGame.gameType,
                gameStartTime: currentGame.gameStartTime,
                gameLength: currentGame.gameLength,
                participants: currentGame.participants
            } : null,
            matchHistory: recentMatches || []
        }
    }
}

export default PlayerLookupService