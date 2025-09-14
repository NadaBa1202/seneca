import React, { useState } from 'react'
import './LeagueFeatures.css'
import ChampionAssistant from './ChampionAssistant'
import PlayerLookup from './PlayerLookup'

const LeagueFeatures = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('player-lookup')

  return (
    <div className="league-features">
      <header className="league-header">
        <div className="header-left">
          <button onClick={onBack} className="back-button">
            ← Back to Dashboard
          </button>
          <div className="page-info">
            <h1>League of Legends Helper</h1>
            <p>Dynamic player analysis, champion lookup, and game insights</p>
          </div>
        </div>
        <div className="patch-info">
          <span className="patch-label">Data Source</span>
          <span className="patch-version">Dragontail 15.18.1</span>
        </div>
      </header>

      <div className="league-content">
        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'player-lookup' ? 'active' : ''}`}
            onClick={() => setActiveTab('player-lookup')}
          >
            👤 Player Lookup
          </button>
          <button 
            className={`tab-button ${activeTab === 'champion-assistant' ? 'active' : ''}`}
            onClick={() => setActiveTab('champion-assistant')}
          >
            🎮 Champion Assistant
          </button>
          <button 
            className={`tab-button ${activeTab === 'item-builds' ? 'active' : ''}`}
            onClick={() => setActiveTab('item-builds')}
          >
            🛡️ Item Builds
          </button>
        </div>

        {/* Player Lookup Tab */}
        {activeTab === 'player-lookup' && (
          <PlayerLookup />
        )}

        {/* Champion Assistant Tab */}
        {activeTab === 'champion-assistant' && (
          <ChampionAssistant />
        )}

        {/* Item Builds Tab */}
        {activeTab === 'item-builds' && (
          <div className="tab-content">
            <div className="item-builds-section">
              <div className="builds-header">
                <h3>🛡️ Popular Item Builds</h3>
                <p>Curated builds for every role and situation</p>
              </div>
              
              <div className="builds-grid">
                <div className="build-category">
                  <h4>🏹 ADC Builds</h4>
                  <div className="build-item">
                    <h5>Crit ADC</h5>
                    <div className="item-list">
                      <span className="item">Kraken Slayer</span>
                      <span className="item">Phantom Dancer</span>
                      <span className="item">Infinity Edge</span>
                      <span className="item">Lord Dominik's</span>
                    </div>
                  </div>
                  <div className="build-item">
                    <h5>On-Hit ADC</h5>
                    <div className="item-list">
                      <span className="item">Wit's End</span>
                      <span className="item">Guinsoo's</span>
                      <span className="item">Blade of the Ruined King</span>
                      <span className="item">Runaan's Hurricane</span>
                    </div>
                  </div>
                </div>

                <div className="build-category">
                  <h4>⚔️ Mid Lane</h4>
                  <div className="build-item">
                    <h5>Burst Mage</h5>
                    <div className="item-list">
                      <span className="item">Luden's Tempest</span>
                      <span className="item">Shadowflame</span>
                      <span className="item">Zhonya's Hourglass</span>
                      <span className="item">Void Staff</span>
                    </div>
                  </div>
                  <div className="build-item">
                    <h5>Assassin</h5>
                    <div className="item-list">
                      <span className="item">Eclipse</span>
                      <span className="item">Youmuu's Ghostblade</span>
                      <span className="item">Edge of Night</span>
                      <span className="item">Serylda's Grudge</span>
                    </div>
                  </div>
                </div>

                <div className="build-category">
                  <h4>💪 Top Lane</h4>
                  <div className="build-item">
                    <h5>Tank</h5>
                    <div className="item-list">
                      <span className="item">Sunfire Aegis</span>
                      <span className="item">Thornmail</span>
                      <span className="item">Force of Nature</span>
                      <span className="item">Gargoyle Stoneplate</span>
                    </div>
                  </div>
                  <div className="build-item">
                    <h5>Fighter</h5>
                    <div className="item-list">
                      <span className="item">Trinity Force</span>
                      <span className="item">Sterak's Gage</span>
                      <span className="item">Death's Dance</span>
                      <span className="item">Guardian Angel</span>
                    </div>
                  </div>
                </div>

                <div className="build-category">
                  <h4>🌟 Support</h4>
                  <div className="build-item">
                    <h5>Enchanter</h5>
                    <div className="item-list">
                      <span className="item">Moonstone Renewer</span>
                      <span className="item">Staff of Flowing Water</span>
                      <span className="item">Chemtech Putrifier</span>
                      <span className="item">Redemption</span>
                    </div>
                  </div>
                  <div className="build-item">
                    <h5>Tank Support</h5>
                    <div className="item-list">
                      <span className="item">Locket of the Iron Solari</span>
                      <span className="item">Frozen Heart</span>
                      <span className="item">Knight's Vow</span>
                      <span className="item">Zeke's Convergence</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="build-tips">
                <h4>💡 Build Tips</h4>
                <ul>
                  <li>🎯 <strong>Early Game:</strong> Focus on core items that give you power spikes</li>
                  <li>⚖️ <strong>Mid Game:</strong> Adapt your build based on enemy team composition</li>
                  <li>🛡️ <strong>Late Game:</strong> Consider defensive items to survive team fights</li>
                  <li>👁️ <strong>Vision:</strong> Don't forget Control Wards - they win games!</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default LeagueFeatures