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
            🔍 Player Lookup
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
          <button 
            className={`tab-button ${activeTab === 'league-chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('league-chat')}
          >
            � League Assistant
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
                <h3>🛡️ Champion Item Builds & Recommendations</h3>
                <p>Discover optimal item builds for different champion roles and game phases</p>
              </div>
              
              <div className="build-categories">
                <div className="build-category">
                  <h4>🗡️ AD Carry Builds</h4>
                  <div className="build-examples">
                    <div className="build-item">
                      <strong>Jinx:</strong> Infinity Edge → Runaan's Hurricane → Bloodthirster → Guardian Angel
                    </div>
                    <div className="build-item">
                      <strong>Vayne:</strong> Kraken Slayer → Wit's End → Infinity Edge → Guardian Angel
                    </div>
                  </div>
                </div>
                
                <div className="build-category">
                  <h4>🛡️ Tank Builds</h4>
                  <div className="build-examples">
                    <div className="build-item">
                      <strong>Alistar:</strong> Locket of Iron Solari → Thornmail → Gargoyle Stoneplate → Warmog's
                    </div>
                    <div className="build-item">
                      <strong>Malphite:</strong> Sunfire Aegis → Thornmail → Force of Nature → Randuin's Omen
                    </div>
                  </div>
                </div>
                
                <div className="build-category">
                  <h4>⚡ AP Carry Builds</h4>
                  <div className="build-examples">
                    <div className="build-item">
                      <strong>Syndra:</strong> Luden's Tempest → Sorcerer's Shoes → Shadowflame → Rabadon's
                    </div>
                    <div className="build-item">
                      <strong>Yasuo:</strong> Immortal Shieldbow → Berserker's Greaves → Infinity Edge → Death's Dance
                    </div>
                  </div>
                </div>
                
                <div className="build-category">
                  <h4>🌿 Jungle Builds</h4>
                  <div className="build-examples">
                    <div className="build-item">
                      <strong>Graves:</strong> Eclipse → Collector → Lord Dominik's → Guardian Angel
                    </div>
                    <div className="build-item">
                      <strong>Ammu:</strong> Sunfire Aegis → Demonic Embrace → Thornmail → Spirit Visage
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="build-tips">
                <h4>💡 Pro Tips</h4>
                <ul>
                  <li>🎯 <strong>Early Game:</strong> Focus on core items that provide immediate power spikes</li>
                  <li>⚖️ <strong>Mid Game:</strong> Adapt your build based on enemy team composition</li>
                  <li>🛡️ <strong>Late Game:</strong> Consider defensive items to survive team fights</li>
                  <li>👁️ <strong>Vision:</strong> Don't forget Control Wards - they win games!</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* League Assistant Chat Tab */}
        {activeTab === 'league-chat' && (
          <div className="tab-content">
            <div className="league-chat-section">
              <div className="chat-header">
                <h3>💬 League of Legends AI Assistant</h3>
                <p>Ask me anything about champions, strategies, builds, or gameplay tips!</p>
              </div>
              
              <div className="chat-container">
                <div className="chat-messages">
                  <div className="ai-message">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">
                      <p>Hello! I'm your League of Legends assistant. I can help you with:</p>
                      <ul>
                        <li>🎮 Champion strategies and tips</li>
                        <li>🛡️ Item builds and recommendations</li>
                        <li>⚔️ Matchup advice and counters</li>
                        <li>🎯 Team composition suggestions</li>
                        <li>📈 Gameplay improvement tips</li>
                      </ul>
                      <p>Try asking me something like: "How do I play Alistar as support?" or "What items should I build on Jinx?"</p>
                    </div>
                  </div>
                </div>
                
                <div className="chat-examples">
                  <h4>💡 Try these questions:</h4>
                  <div className="example-questions">
                    <button className="example-btn" onClick={() => handleExampleQuestion("How do I play Alistar effectively?")}>
                      How do I play Alistar effectively?
                    </button>
                    <button className="example-btn" onClick={() => handleExampleQuestion("What's the best build for Jinx?")}>
                      What's the best build for Jinx?
                    </button>
                    <button className="example-btn" onClick={() => handleExampleQuestion("How do I counter Yasuo?")}>
                      How do I counter Yasuo?
                    </button>
                    <button className="example-btn" onClick={() => handleExampleQuestion("What are good team compositions?")}>
                      What are good team compositions?
                    </button>
                  </div>
                </div>
                
                <div className="chat-input-area">
                  <div className="chat-input-group">
                    <input
                      type="text"
                      placeholder="Ask me anything about League of Legends..."
                      className="chat-input"
                    />
                    <button className="send-button">
                      📤 Send
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  function handleExampleQuestion(question) {
    // This will be implemented with actual AI responses
    console.log('Example question clicked:', question)
  }
}

export default LeagueFeatures