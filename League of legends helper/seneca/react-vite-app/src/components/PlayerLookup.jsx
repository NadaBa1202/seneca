import { useState } from 'react'
import './PlayerLookup.css'

const PlayerLookup = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [playerData, setPlayerData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const PROXY_URL = 'http://localhost:3001'

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
    return regionMap[tagLine.toUpperCase()] || 'na1';
  }

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setError('Please enter a player name')
      return
    }

    setLoading(true)
    setError('')
    setPlayerData(null)

    try {
      // Parse player input
      let gameName, tagLine
      if (searchTerm.includes('#')) {
        [gameName, tagLine] = searchTerm.split('#')
        gameName = gameName.trim()
        tagLine = tagLine.trim()
      } else {
        gameName = searchTerm.trim()
        tagLine = 'NA1'
      }

      console.log(`🔍 Looking up player: ${gameName}#${tagLine}`)

      // Get the correct region for API calls
      const region = getRegionFromTag(tagLine)
      console.log(`🌍 Using region: ${region}`)

      // Step 1: Get account by Riot ID
      const accountResponse = await fetch(`${PROXY_URL}/api/account/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`)

      if (!accountResponse.ok) {
        const errorData = await accountResponse.json()
        throw new Error(errorData.error || `Player not found: ${gameName}#${tagLine}`)
      }

      const account = await accountResponse.json()
      console.log('✅ Found account:', account.gameName)

      // Step 2: Get summoner info
      const summonerResponse = await fetch(`${PROXY_URL}/api/summoner/${account.puuid}/${region}`)

      if (!summonerResponse.ok) {
        const errorData = await summonerResponse.json()
        throw new Error(errorData.error || 'Failed to get summoner information')
      }

      const summoner = await summonerResponse.json()
      console.log('✅ Found summoner:', summoner.summonerLevel)

      // Step 3: Get ranked info
      const rankedResponse = await fetch(`${PROXY_URL}/api/ranked/${account.puuid}/${region}`)
      const rankedInfo = rankedResponse.ok ? await rankedResponse.json() : []

      // Step 4: Get champion mastery
      const masteryResponse = await fetch(`${PROXY_URL}/api/mastery/${account.puuid}/${region}`)
      const masteryData = masteryResponse.ok ? await masteryResponse.json() : { masteries: [], masteryScore: 0 }

      // Step 5: Get recent matches
      const matchResponse = await fetch(`${PROXY_URL}/api/matches/${account.puuid}`)
      const recentMatches = matchResponse.ok ? await matchResponse.json() : []

      // Step 6: Check if currently in game
      const currentGameResponse = await fetch(`${PROXY_URL}/api/current-game/${account.puuid}/${region}`)
      const currentGame = currentGameResponse.ok ? await currentGameResponse.json() : null

      setPlayerData({
        account,
        summoner,
        rankedInfo,
        masteries: masteryData.masteries,
        masteryScore: masteryData.masteryScore,
        recentMatches,
        currentGame
      })

    } catch (error) {
      console.error('Player lookup error:', error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const formatRank = (rankEntry) => {
    if (!rankEntry) return 'Unranked'
    return `${rankEntry.tier} ${rankEntry.rank} ${rankEntry.leaguePoints} LP`
  }

  const getWinRate = (rankEntry) => {
    if (!rankEntry || !rankEntry.wins) return 0
    return Math.round((rankEntry.wins / (rankEntry.wins + rankEntry.losses)) * 100)
  }

  return (
    <div className="player-lookup">
      <div className="search-section">
        <h2>🔍 Player Lookup</h2>
        <p>Search for any League player using their Riot ID (GameName#TAG)</p>
        
        <div className="search-container">
          <input
            type="text"
            placeholder="Enter player name (e.g., Doublelift#NA1)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="search-input"
          />
          <button 
            onClick={handleSearch} 
            disabled={loading}
            className="search-button"
          >
            {loading ? '⏳ Searching...' : '🔍 Search'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Searching for player...</p>
        </div>
      )}

      {playerData && !loading && (
        <div className="player-results">
          <div className="player-header">
            <div className="player-info">
              <h3>{playerData.account.gameName}#{playerData.account.tagLine}</h3>
              <p>Level {playerData.summoner.summonerLevel}</p>
              {playerData.currentGame && (
                <div className="live-game">🔴 Currently in game!</div>
              )}
            </div>
          </div>

          <div className="player-stats">
            <div className="stat-section">
              <h4>🏆 Ranked Information</h4>
              {playerData.rankedInfo.length > 0 ? (
                <div className="ranked-info">
                  {playerData.rankedInfo.map((rank, index) => (
                    <div key={index} className="rank-entry">
                      <div className="queue-type">
                        {rank.queueType === 'RANKED_SOLO_5x5' ? 'Solo/Duo' : 'Flex'}
                      </div>
                      <div className="rank-details">
                        <span className="rank">{formatRank(rank)}</span>
                        <span className="wins-losses">{rank.wins}W / {rank.losses}L</span>
                        <span className="winrate">({getWinRate(rank)}% WR)</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No ranked data found</p>
              )}
            </div>

            <div className="stat-section">
              <h4>⭐ Champion Mastery</h4>
              <div className="mastery-score">
                <strong>Total Mastery Score: {playerData.masteryScore.toLocaleString()}</strong>
              </div>
              {playerData.masteries.length > 0 && (
                <div className="top-champions">
                  <h5>Top Champions:</h5>
                  {playerData.masteries.map((mastery, index) => (
                    <div key={index} className="mastery-entry">
                      <span className="champion-id">Champion {mastery.championId}</span>
                      <span className="mastery-level">Level {mastery.championLevel}</span>
                      <span className="mastery-points">{mastery.championPoints.toLocaleString()} points</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="stat-section">
              <h4>📊 Recent Activity</h4>
              <div className="recent-matches">
                <p>Recent Matches: {playerData.recentMatches.length}</p>
                {playerData.recentMatches.slice(0, 3).map((matchId, index) => (
                  <div key={index} className="match-entry">
                    <span className="match-id">{matchId}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="examples">
        <h4>Try searching for:</h4>
        <div className="example-players">
          <button onClick={() => setSearchTerm('Doublelift#NA1')}>Doublelift#NA1</button>
          <button onClick={() => setSearchTerm('Tyler1#NA1')}>Tyler1#NA1</button>
          <button onClick={() => setSearchTerm('Faker#T1')}>Faker#T1</button>
        </div>
      </div>
    </div>
  )
}

export default PlayerLookup