import { useState, useEffect, useRef } from 'react'
import LeagueDataService from '../services/LeagueDataService'
import EnhancedDynamicItemService from '../services/EnhancedDynamicItemService'
import AIChatbot from './AIChatbot'
import './ChampionAssistant.css'

const ChampionAssistant = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [champions, setChampions] = useState([])
  const [filteredChampions, setFilteredChampions] = useState([])
  const [selectedChampion, setSelectedChampion] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [dynamicBuilds, setDynamicBuilds] = useState(null)
  const [buildLoading, setBuildLoading] = useState(false)
  const [showChatbot, setShowChatbot] = useState(false)
  const searchRef = useRef(null)
  const dataService = new LeagueDataService()
  const itemService = new EnhancedDynamicItemService()

  const loadChampions = async () => {
    try {
      const champData = await dataService.loadChampions()
      setChampions(champData)
      setLoading(false)
    } catch (error) {
      console.error('Error loading champions:', error)
      setLoading(false)
    }
  }

  useEffect(() => {
    loadChampions()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (searchTerm.length > 0) {
      const filtered = champions.filter(champion =>
        champion.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        champion.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        champion.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      setFilteredChampions(filtered.slice(0, 8))
      setShowSuggestions(true)
    } else {
      setFilteredChampions([])
      setShowSuggestions(false)
    }
  }, [searchTerm, champions])

  const handleChampionSelect = async (championId) => {
    try {
      setLoading(true)
      setBuildLoading(true)
      setSelectedChampion(null) // Clear previous champion
      
      console.log('Loading champion:', championId)
      const champion = await dataService.getChampion(championId)
      console.log('Champion loaded successfully:', champion.name)
      
      const championName = champion.name || championId
      
      // Load enhanced dynamic item builds with AI insights
      const gameContext = {
        gameMode: 'ranked',
        role: 'default',
        gameLength: 'normal',
        enemyTeam: [],
        allyTeam: [],
        gameState: 'even',
        playerSkill: 'average'
      }
      
      console.log('Loading builds for:', championName)
      const builds = await itemService.getIntelligentBuildRecommendations(champion, gameContext)
      
      // Validate and sanitize builds data
      const sanitizedBuilds = {
        core: Array.isArray(builds?.core) ? builds.core : ['No core items available'],
        starter: Array.isArray(builds?.starter) ? builds.starter : ['No starter items available'],
        boots: builds?.boots || 'No boots specified',
        situational: builds?.situational || {},
        lateGame: Array.isArray(builds?.lateGame) ? builds.lateGame : ['No late game items available'],
        ...builds // Keep other properties
      }
      
      console.log('Sanitized builds:', sanitizedBuilds)
      setDynamicBuilds(sanitizedBuilds)
      setBuildLoading(false)
      
      // Enhanced champion data with tips and strategies
      const enhancedChampion = {
        ...champion,
        playTips: getPlayTips(championName),
        counterTips: getCounterTips(championName),
        itemBuilds: getRecommendedBuilds(championName),
        teamComps: getTeamCompositions(championName)
      }
      
      setSelectedChampion(enhancedChampion)
      setSearchTerm(champion.name)
      setShowSuggestions(false)
      setLoading(false)
      console.log('Champion selection completed successfully')
      
    } catch (error) {
      console.error('Error loading champion:', error)
      // Don't break the UI, just show an error state
      setSelectedChampion({
        id: championId,
        name: championId,
        title: 'Champion not found',
        error: error.message,
        playTips: ['Unable to load champion data'],
        counterTips: ['Please try another champion'],
        itemBuilds: { standard: { core: ['Data unavailable'], boots: 'N/A', situational: [] } },
        teamComps: ['Unable to load team composition data']
      })
      setDynamicBuilds(null)
      setSearchTerm('')
      setShowSuggestions(false)
      setLoading(false)
      setBuildLoading(false)
    }
  }

  const getPlayTips = (championName) => {
    const tips = {
      'Alistar': [
        '🔥 Combo Mastery: Use W+Q combo for reliable knockup engage',
        '🛡️ Tanking: Save your ultimate for when you\'re low on health to maximize damage reduction',
        '🎯 Positioning: Flash + W + Q is one of the strongest engage combos in the game',
        '⚡ Early Game: Focus on protecting your ADC and looking for roam opportunities',
        '🏰 Late Game: Be the frontline - your job is to absorb damage and disrupt enemies'
      ],
      'Ahri': [
        '💫 Charm Setup: Use Q to push minions, then look for E on enemies',
        '🌟 Ultimate Usage: Don\'t use all 3 R charges at once - space them out for repositioning',
        '🎯 Positioning: Stay at max range and kite backwards with your abilities',
        '⚡ Laning: Use Q to farm and poke simultaneously',
        '🔮 Team Fights: Look to pick off isolated targets with E + full combo'
      ],
      'Yasuo': [
        '🌪️ Wind Wall: Use W to block key abilities in team fights',
        '⚔️ Stack Q: Always keep your Q tornado ready for opportunities',
        '🎯 Minion Dancing: Use E on minions to dodge skillshots and reposition',
        '💨 Ultimate: Only use R when you have backup or guaranteed kill',
        '🗡️ Power Spikes: Very strong at 2 items (Infinity Edge + Phantom Dancer)'
      ]
    }
    
    return tips[championName] || [
      '🎯 Focus on learning the champion\'s optimal combo sequence',
      '📊 Study the champion\'s power spikes and play around them',
      '🎮 Practice last-hitting and trading in lane',
      '👥 Learn when to engage in team fights vs when to peel',
      '📈 Master the champion\'s build paths for different situations'
    ]
  }

  const getCounterTips = (championName) => {
    const counterTips = {
      'Alistar': [
        '🚫 Spread Out: Don\'t group up - makes his W+Q combo less effective',
        '🏃 Respect Flash Range: Stay away from walls when he has flash up',
        '💥 Burst When Ultimate Down: His R reduces damage by 70% - wait for it to end',
        '🎯 Poke from Range: He struggles against long-range champions',
        '⚡ Punish Cooldowns: His W+Q combo has long cooldowns early game'
      ],
      'Ahri': [
        '👁️ Sidestep Charm: Her E is predictable - dodge it to avoid full combo',
        '🛡️ Magic Resist: Early MR makes her struggle to burst you down',
        '🏃 Stay Behind Minions: Blocks her charm and Q return damage',
        '⚡ Punish Ultimate Cooldown: She\'s vulnerable when R is down',
        '🎯 All-in When Low Mana: She needs mana for her escape tools'
      ],
      'Yasuo': [
        '🌪️ Respect Wind Wall: Don\'t waste key abilities when it\'s up',
        '⚔️ Avoid Extended Trades: He gets stronger the longer fights go',
        '🎯 Target in Team Fights: He\'s squishy despite being melee',
        '🔄 Reset His Passive: Auto attack to break his shield regularly',
        '📊 Punish Before Power Spikes: He\'s weak before completing items'
      ]
    }
    
    return counterTips[championName] || [
      '📊 Learn the champion\'s cooldowns and punish them',
      '🎯 Identify their power spikes and play safely during them',
      '🛡️ Build appropriate defensive items against their damage type',
      '👥 Coordinate with team to focus them in fights',
      '🎮 Study their common build paths to understand their strengths'
    ]
  }

  const getRecommendedBuilds = (championName) => {
    const builds = {
      'Alistar': {
        support: {
          core: ['Locket of the Iron Solari', 'Knight\'s Vow', 'Thornmail'],
          boots: 'Mobility Boots',
          situational: ['Redemption', 'Zeke\'s Convergence', 'Randuin\'s Omen']
        }
      },
      'Ahri': {
        mid: {
          core: ['Luden\'s Tempest', 'Shadowflame', 'Zhonya\'s Hourglass'],
          boots: 'Sorcerer\'s Shoes',
          situational: ['Banshee\'s Veil', 'Morellonomicon', 'Void Staff']
        }
      },
      'Yasuo': {
        mid: {
          core: ['Infinity Edge', 'Phantom Dancer', 'Immortal Shieldbow'],
          boots: 'Berserker\'s Greaves',
          situational: ['Death\'s Dance', 'Guardian Angel', 'Mortal Reminder']
        }
      }
    }
    
    return builds[championName] || {
      standard: {
        core: ['Check champion guides for optimal builds'],
        boots: 'Situational',
        situational: ['Adapt based on game state and enemy team']
      }
    }
  }

  const getTeamCompositions = (championName) => {
    const teamComps = {
      'Alistar': [
        '🛡️ Engage Comp: Pairs well with follow-up damage (Orianna, Miss Fortune)',
        '🏰 Protect the Carry: Great with hypercarries (Kog\'Maw, Jinx)',
        '⚡ Pick Comp: Works with assassins for quick eliminations'
      ],
      'Ahri': [
        '🎯 Pick Comp: Excellent for catching enemies out of position',
        '💫 Poke Comp: Good poke and disengage with charm',
        '🔄 Skirmish Comp: Mobile and good for small team fights'
      ],
      'Yasuo': [
        '🌪️ Knockup Comp: Needs teammates with knockups (Malphite, Gragas)',
        '⚔️ Dive Comp: Good for getting to enemy backline',
        '🛡️ Protect Yasuo: Needs peel and shields to succeed'
      ]
    }
    
    return teamComps[championName] || [
      '🤝 Works well in balanced team compositions',
      '🎯 Can fill multiple roles depending on build',
      '📊 Adapt team strategy based on champion strengths'
    ]
  }

  return (
    <div className="champion-assistant">
      <div className="search-section">
        <h1>🏆 League Champion Assistant</h1>
        <div className="search-container" ref={searchRef}>
          <input
            type="text"
            placeholder="Search for a champion (e.g., Alistar, Ahri, Yasuo...)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="champion-search"
            onFocus={() => setShowSuggestions(searchTerm.length > 0)}
          />
          
          {showSuggestions && filteredChampions.length > 0 && (
            <div className="suggestions-dropdown">
              {filteredChampions.map(champion => (
                <div
                  key={champion.id}
                  className="suggestion-item"
                  onClick={() => handleChampionSelect(champion.id)}
                >
                  <img 
                    src={`/dragontail/champion/${champion.id}_0.jpg`}
                    alt={champion.name}
                    className="suggestion-icon"
                    onError={(e) => {
                      e.target.src = `https://ddragon.leagueoflegends.com/cdn/15.18.1/img/champion/${champion.id}.png`
                    }}
                  />
                  <div className="suggestion-info">
                    <div className="suggestion-name">{champion.name}</div>
                    <div className="suggestion-title">{champion.title}</div>
                    <div className="suggestion-tags">{champion.tags.join(', ')}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading champion data...</p>
        </div>
      )}

      {selectedChampion && !loading && (
        <div className="champion-details">
          <div className="champion-header">
            <div className="champion-portrait">
              <img 
                src={`/dragontail/champion/${selectedChampion.id}_0.jpg`}
                alt={selectedChampion.name}
                className="champion-image"
                onError={(e) => {
                  e.target.src = `https://ddragon.leagueoflegends.com/cdn/15.18.1/img/champion/${selectedChampion.id}.png`
                }}
              />
            </div>
            <div className="champion-info">
              <h2>{selectedChampion.name}</h2>
              <p className="champion-title">{selectedChampion.title}</p>
              <div className="champion-tags">
                {selectedChampion.tags.map(tag => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
              <div className="difficulty">
                <span>Difficulty: </span>
                <div className="difficulty-bar">
                  {[...Array(10)].map((_, i) => (
                    <div 
                      key={i} 
                      className={`difficulty-dot ${i < selectedChampion.info.difficulty ? 'filled' : ''}`}
                    />
                  ))}
                </div>
                <span>{selectedChampion.info.difficulty}/10</span>
              </div>
            </div>
          </div>

          <div className="champion-tabs">
            <div className="tab-content">
              
              {/* Abilities Section */}
              {selectedChampion.abilities && (
                <div className="abilities-section">
                  <h3>⚡ Abilities</h3>
                  
                  {selectedChampion.abilities.passive && (
                    <div className="ability passive">
                      <div className="ability-header">
                        <span className="ability-key">Passive</span>
                        <h4>{selectedChampion.abilities.passive.name}</h4>
                      </div>
                      <p>{selectedChampion.abilities.passive.description}</p>
                    </div>
                  )}

                  {selectedChampion.abilities.spells && selectedChampion.abilities.spells.map((spell, index) => (
                    <div key={index} className="ability">
                      <div className="ability-header">
                        <span className="ability-key">{['Q', 'W', 'E', 'R'][index]}</span>
                        <h4>{spell.name}</h4>
                      </div>
                      <p>{spell.description}</p>
                      <div className="ability-stats">
                        {spell.cooldown && (
                          <span><strong>Cooldown:</strong> {Array.isArray(spell.cooldown) ? spell.cooldown.join('/') : spell.cooldown}s</span>
                        )}
                        {spell.cost && (
                          <span><strong>Cost:</strong> {Array.isArray(spell.cost) ? spell.cost.join('/') : spell.cost}</span>
                        )}
                        {spell.range && (
                          <span><strong>Range:</strong> {spell.range}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Stats Section */}
              {selectedChampion.detailedStats && (
                <div className="stats-section">
                  <h3>📊 Base Stats</h3>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-label">Health</span>
                      <span className="stat-value">{selectedChampion.detailedStats.hp} (+{selectedChampion.detailedStats.hpperlevel})</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Mana</span>
                      <span className="stat-value">{selectedChampion.detailedStats.mp} (+{selectedChampion.detailedStats.mpperlevel})</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Attack Damage</span>
                      <span className="stat-value">{selectedChampion.detailedStats.attackdamage} (+{selectedChampion.detailedStats.attackdamageperlevel})</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Armor</span>
                      <span className="stat-value">{selectedChampion.detailedStats.armor} (+{selectedChampion.detailedStats.armorperlevel})</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Magic Resistance</span>
                      <span className="stat-value">{selectedChampion.detailedStats.spellblock} (+{selectedChampion.detailedStats.spellblockperlevel})</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Movement Speed</span>
                      <span className="stat-value">{selectedChampion.detailedStats.movespeed}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Play Tips */}
              <div className="tips-section">
                <h3>🎮 How to Play as {selectedChampion.name}</h3>
                <ul className="tips-list">
                  {selectedChampion.playTips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </div>

              {/* Counter Tips */}
              <div className="tips-section">
                <h3>🛡️ How to Play Against {selectedChampion.name}</h3>
                <ul className="tips-list counter-tips">
                  {selectedChampion.counterTips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </div>

              {/* Dynamic Item Builds */}
              <div className="builds-section">
                <h3>🛠️ Dynamic Item Builds</h3>
                {buildLoading ? (
                  <div className="build-loading">Loading optimized builds...</div>
                ) : dynamicBuilds ? (
                  <div className="dynamic-builds">
                    <div className="build-path">
                      <h4>🚀 Starter Items</h4>
                      <div className="build-items">
                        <div className="items">
                          {Array.isArray(dynamicBuilds.starter) 
                            ? dynamicBuilds.starter.join(', ') 
                            : 'Loading starter items...'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="build-path">
                      <h4>⚡ Core Build</h4>
                      <div className="build-items">
                        <div className="items">
                          {Array.isArray(dynamicBuilds.core) 
                            ? dynamicBuilds.core.join(' → ') 
                            : 'Loading core build...'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="build-path">
                      <h4>👟 Boots Options</h4>
                      <div className="build-items">
                        <div className="items">
                          {dynamicBuilds.boots ? (
                            <>
                              <strong>
                                {typeof dynamicBuilds.boots === 'string' 
                                  ? dynamicBuilds.boots 
                                  : dynamicBuilds.boots.standard || 'Situational'}
                              </strong>
                              {Array.isArray(dynamicBuilds.boots?.alternatives) && (
                                <span className="alternatives">
                                  {' '} (Alt: {dynamicBuilds.boots.alternatives.join(', ')})
                                </span>
                              )}
                            </>
                          ) : (
                            'Loading boots options...'
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="build-path">
                      <h4>🎯 Situational Items</h4>
                      <div className="situational-builds">
                        {dynamicBuilds.situational && typeof dynamicBuilds.situational === 'object' ? (
                          Object.entries(dynamicBuilds.situational).map(([situation, items]) => (
                            <div key={situation} className="situation-category">
                              <span className="situation-label">{situation.charAt(0).toUpperCase() + situation.slice(1)}:</span>
                              <div className="items">
                                {Array.isArray(items) ? items.join(', ') : 'No items available'}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="items">Loading situational items...</div>
                        )}
                      </div>
                    </div>
                    
                    <div className="build-path">
                      <h4>🏆 Late Game</h4>
                      <div className="build-items">
                        <div className="items">
                          {Array.isArray(dynamicBuilds.lateGame) 
                            ? dynamicBuilds.lateGame.join(', ') 
                            : 'Loading late game items...'}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="fallback-builds">
                    {selectedChampion.itemBuilds && typeof selectedChampion.itemBuilds === 'object' ? (
                      Object.entries(selectedChampion.itemBuilds).map(([role, build]) => (
                        <div key={role} className="build-role">
                          <h4>{role.charAt(0).toUpperCase() + role.slice(1)}</h4>
                          <div className="build-items">
                            <div className="item-category">
                              <span className="category-label">Core Items:</span>
                              <div className="items">
                                {Array.isArray(build.core) ? build.core.join(', ') : 'No core items available'}
                              </div>
                            </div>
                            <div className="item-category">
                              <span className="category-label">Boots:</span>
                              <div className="items">{build.boots || 'No boots specified'}</div>
                            </div>
                            <div className="item-category">
                              <span className="category-label">Situational:</span>
                              <div className="items">
                                {Array.isArray(build.situational) ? build.situational.join(', ') : 'No situational items available'}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="no-builds">No build information available</div>
                    )}
                  </div>
                )}
              </div>

              {/* Team Compositions */}
              <div className="team-comps-section">
                <h3>👥 Team Compositions</h3>
                <ul className="comps-list">
                  {selectedChampion.teamComps.map((comp, index) => (
                    <li key={index}>{comp}</li>
                  ))}
                </ul>
              </div>

              {/* Lore */}
              {selectedChampion.lore && (
                <div className="lore-section">
                  <h3>📖 Champion Lore</h3>
                  <p className="lore-text">{selectedChampion.lore}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {!selectedChampion && !loading && (
        <div className="welcome-message">
          <h2>🔍 Search for any League of Legends champion!</h2>
          <p>Get comprehensive information including abilities, stats, tips, builds, and strategies.</p>
          <div className="example-searches">
            <h3>Try searching for:</h3>
            <div className="example-tags">
              <span onClick={() => handleChampionSelect('Alistar')}>Alistar</span>
              <span onClick={() => handleChampionSelect('Ahri')}>Ahri</span>
              <span onClick={() => handleChampionSelect('Yasuo')}>Yasuo</span>
              <span onClick={() => handleChampionSelect('Jinx')}>Jinx</span>
              <span onClick={() => handleChampionSelect('Thresh')}>Thresh</span>
            </div>
          </div>
        </div>
      )}

      {/* AI Chatbot Toggle Button */}
      <button 
        className="chatbot-toggle"
        onClick={() => setShowChatbot(!showChatbot)}
        title="Open AI Assistant"
      >
        💬 AI Help
      </button>

      {/* Enhanced AI Chatbot */}
      {showChatbot && (
        <AIChatbot 
          champion={selectedChampion}
          onClose={() => setShowChatbot(false)}
        />
      )}
    </div>
  )
}

export default ChampionAssistant