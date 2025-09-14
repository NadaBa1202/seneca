import { useState, useEffect } from 'react'
import LeagueDataService from '../services/LeagueDataService'

const TestDragontailData = () => {
  const [status, setStatus] = useState('Loading...')
  const [champions, setChampions] = useState([])
  const [items, setItems] = useState([])
  const [selectedChampion, setSelectedChampion] = useState(null)

  useEffect(() => {
    testDataLoading()
  }, [])

  const testDataLoading = async () => {
    const dataService = new LeagueDataService()
    
    try {
      setStatus('Loading champions...')
      const champData = await dataService.loadChampions()
      setChampions(champData)
      setStatus(`✅ Loaded ${champData.length} champions`)
      
      setStatus('Loading items...')
      const itemData = await dataService.loadItems()
      setItems(itemData)
      setStatus(`✅ Loaded ${champData.length} champions and ${itemData.length} items`)
      
      // Test detailed champion loading
      if (champData.length > 0) {
        const testChampion = champData.find(c => c.name === 'Ahri') || champData[0]
        setStatus(`Loading details for ${testChampion.name}...`)
        const detailedChampion = await dataService.getChampion(testChampion.id)
        setSelectedChampion(detailedChampion)
        setStatus(`✅ All data loaded successfully! Test champion: ${testChampion.name}`)
      }
      
    } catch (error) {
      setStatus(`❌ Error: ${error.message}`)
      console.error('Data loading error:', error)
    }
  }

  return (
    <div style={{ padding: '2rem', background: '#1a1a2e', color: '#fff', minHeight: '100vh' }}>
      <h1>🧪 Dragontail Data Test</h1>
      <p><strong>Status:</strong> {status}</p>
      
      {champions.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Champions ({champions.length})</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            {champions.slice(0, 12).map(champion => (
              <div key={champion.id} style={{ 
                background: 'rgba(255,255,255,0.1)', 
                padding: '1rem', 
                borderRadius: '8px',
                cursor: 'pointer'
              }}
              onClick={() => testDataLoading()}>
                <h4>{champion.name}</h4>
                <p>{champion.title}</p>
                <p>Tags: {champion.tags.join(', ')}</p>
                <p>Difficulty: {champion.info.difficulty}/10</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {selectedChampion && (
        <div style={{ marginTop: '2rem', background: 'rgba(255,255,255,0.05)', padding: '2rem', borderRadius: '12px' }}>
          <h2>📋 Detailed Champion Data: {selectedChampion.name}</h2>
          
          {selectedChampion.abilities && (
            <div style={{ marginTop: '1rem' }}>
              <h3>⚡ Abilities</h3>
              {selectedChampion.abilities.passive && (
                <div style={{ margin: '1rem 0', padding: '1rem', background: 'rgba(255,215,0,0.1)', borderRadius: '8px' }}>
                  <h4>Passive: {selectedChampion.abilities.passive.name}</h4>
                  <p>{selectedChampion.abilities.passive.description}</p>
                </div>
              )}
              {selectedChampion.abilities.spells && selectedChampion.abilities.spells.map((spell, index) => (
                <div key={index} style={{ margin: '1rem 0', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                  <h4>{['Q', 'W', 'E', 'R'][index]}: {spell.name}</h4>
                  <p>{spell.description}</p>
                  {spell.cooldown && <p><strong>Cooldown:</strong> {Array.isArray(spell.cooldown) ? spell.cooldown.join('/') : spell.cooldown}</p>}
                  {spell.cost && <p><strong>Cost:</strong> {Array.isArray(spell.cost) ? spell.cost.join('/') : spell.cost}</p>}
                  {spell.range && <p><strong>Range:</strong> {spell.range}</p>}
                </div>
              ))}
            </div>
          )}
          
          {selectedChampion.detailedStats && (
            <div style={{ marginTop: '1rem' }}>
              <h3>📊 Stats</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <div>
                  <p><strong>Health:</strong> {selectedChampion.detailedStats.hp} (+{selectedChampion.detailedStats.hpperlevel})</p>
                  <p><strong>Mana:</strong> {selectedChampion.detailedStats.mp} (+{selectedChampion.detailedStats.mpperlevel})</p>
                </div>
                <div>
                  <p><strong>Attack Damage:</strong> {selectedChampion.detailedStats.attackdamage} (+{selectedChampion.detailedStats.attackdamageperlevel})</p>
                  <p><strong>Armor:</strong> {selectedChampion.detailedStats.armor} (+{selectedChampion.detailedStats.armorperlevel})</p>
                </div>
              </div>
            </div>
          )}
          
          {selectedChampion.lore && (
            <div style={{ marginTop: '1rem' }}>
              <h3>📖 Lore</h3>
              <p style={{ lineHeight: '1.6' }}>{selectedChampion.lore}</p>
            </div>
          )}
        </div>
      )}
      
      {items.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Items ({items.length})</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
            {items.slice(0, 8).map(item => (
              <div key={item.id} style={{ 
                background: 'rgba(255,255,255,0.1)', 
                padding: '1rem', 
                borderRadius: '8px'
              }}>
                <h4>{item.name}</h4>
                <p>{item.plaintext}</p>
                {item.gold && <p><strong>Cost:</strong> {item.gold.total}g</p>}
                {item.stats && Object.keys(item.stats).length > 0 && (
                  <div>
                    <strong>Stats:</strong>
                    {Object.entries(item.stats).slice(0, 3).map(([stat, value]) => (
                      <p key={stat} style={{ fontSize: '0.9rem' }}>{stat}: +{value}</p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TestDragontailData