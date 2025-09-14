import React, { useState, useEffect } from 'react'
import './LeagueFeatures.css'

const LeagueFeatures = ({ onBack }) => {
  const [playerData, setPlayerData] = useState(null)
  const [searchUsername, setSearchUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentPatch, setCurrentPatch] = useState('14.19')

  // Simulated League data - in real app would connect to Riot API
  const samplePlayerData = {
    summoner: {
      name: "ExamplePlayer",
      level: 247,
      profileIconId: 4542,
      tier: "Gold",
      rank: "II",
      leaguePoints: 65
    },
    recentMatches: [
      {
        champion: "Jinx",
        gameMode: "Ranked Solo",
        result: "Victory",
        kda: "12/3/8",
        duration: "28:45",
        date: "2 hours ago"
      },
      {
        champion: "Aphelios", 
        gameMode: "Ranked Solo",
        result: "Defeat",
        kda: "6/7/12",
        duration: "35:22",
        date: "5 hours ago"
      }
    ],
    championStats: [
      { name: "Jinx", games: 45, winRate: 67, avgKDA: "8.2/4.1/9.3" },
      { name: "Aphelios", games: 32, winRate: 59, avgKDA: "7.8/4.8/8.1" },
      { name: "Caitlyn", games: 28, winRate: 71, avgKDA: "9.1/3.9/7.8" }
    ]
  }

  const searchPlayer = async () => {
    if (!searchUsername.trim()) return
    
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      setPlayerData(samplePlayerData)
      setLoading(false)
    }, 1500)
  }

  const getCurrentPatchNotes = () => {
    return [
      {
        category: "Champion Updates",
        changes: [
          "Jinx: Base AD increased from 57 to 59",
          "Aphelios: Infernum Q damage reduced by 10%",
          "Caitlyn: Headshot range increased by 25 units"
        ]
      },
      {
        category: "Item Changes", 
        changes: [
          "Infinity Edge: AD increased from 70 to 75",
          "Kraken Slayer: Attack speed reduced from 25% to 20%",
          "Galeforce: Cooldown increased from 90s to 110s"
        ]
      }
    ]
  }

  return (
    <div className="league-features">
      <header className="league-header">
        <div className="header-left">
          <button onClick={onBack} className="back-button">
            ← Back to Dashboard
          </button>
          <div className="page-info">
            <h1>League of Legends Helper</h1>
            <p>Player analysis, stats tracking, and game insights</p>
          </div>
        </div>
        <div className="patch-info">
          <span className="patch-label">Current Patch</span>
          <span className="patch-version">{currentPatch}</span>
        </div>
      </header>

      <div className="league-content">
        <div className="features-grid">
          {/* Player Search Section */}
          <div className="feature-card player-search">
            <h3>🔍 Player Lookup</h3>
            <div className="search-section">
              <div className="search-input-group">
                <input
                  type="text"
                  placeholder="Enter summoner name..."
                  value={searchUsername}
                  onChange={(e) => setSearchUsername(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchPlayer()}
                  className="player-input"
                />
                <button 
                  onClick={searchPlayer}
                  disabled={loading}
                  className="search-button"
                >
                  {loading ? '⏳' : '🔍'}
                </button>
              </div>
              
              {loading && (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Fetching player data...</p>
                </div>
              )}
              
              {playerData && !loading && (
                <div className="player-results">
                  <div className="player-overview">
                    <div className="player-info">
                      <h4>{playerData.summoner.name}</h4>
                      <p>Level {playerData.summoner.level}</p>
                      <div className="rank-info">
                        <span className="tier">{playerData.summoner.tier}</span>
                        <span className="rank">{playerData.summoner.rank}</span>
                        <span className="lp">{playerData.summoner.leaguePoints} LP</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="recent-matches">
                    <h5>Recent Matches</h5>
                    {playerData.recentMatches.map((match, index) => (
                      <div key={index} className={`match-item ${match.result.toLowerCase()}`}>
                        <span className="champion">{match.champion}</span>
                        <span className="kda">{match.kda}</span>
                        <span className="result">{match.result}</span>
                        <span className="duration">{match.duration}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Champion Statistics */}
          <div className="feature-card champion-stats">
            <h3>📊 Champion Performance</h3>
            {playerData && (
              <div className="champion-list">
                {playerData.championStats.map((champ, index) => (
                  <div key={index} className="champion-item">
                    <div className="champion-name">{champ.name}</div>
                    <div className="champion-metrics">
                      <span className="games">{champ.games} games</span>
                      <span className={`winrate ${champ.winRate >= 60 ? 'good' : champ.winRate >= 50 ? 'average' : 'poor'}`}>
                        {champ.winRate}% WR
                      </span>
                      <span className="kda">{champ.avgKDA} KDA</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {!playerData && (
              <div className="placeholder">
                <p>Search for a player to view champion statistics</p>
              </div>
            )}
          </div>

          {/* Patch Notes */}
          <div className="feature-card patch-notes">
            <h3>📝 Patch {currentPatch} Notes</h3>
            <div className="patch-content">
              {getCurrentPatchNotes().map((section, index) => (
                <div key={index} className="patch-section">
                  <h5>{section.category}</h5>
                  <ul>
                    {section.changes.map((change, i) => (
                      <li key={i}>{change}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* Game Tools */}
          <div className="feature-card game-tools">
            <h3>🛠️ Game Tools</h3>
            <div className="tools-grid">
              <button className="tool-button">
                <span className="tool-icon">⏱️</span>
                <span>Timer Tracker</span>
              </button>
              <button className="tool-button">
                <span className="tool-icon">🗺️</span>
                <span>Ward Tracker</span>
              </button>
              <button className="tool-button">
                <span className="tool-icon">📈</span>
                <span>Build Optimizer</span>
              </button>
              <button className="tool-button">
                <span className="tool-icon">🎯</span>
                <span>Skill Order</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LeagueFeatures