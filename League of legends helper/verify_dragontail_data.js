// Verify the dragontail data files are properly loaded
const fs = require('fs')
const path = require('path')

const basePath = "d:\\Seneca Hacks\\League of legends helper\\seneca\\react-vite-app\\public\\dragontail"

console.log('🔍 Verifying Dragontail Data Files...\n')

// Check champion.json
try {
  const championPath = path.join(basePath, 'champion.json')
  const championData = JSON.parse(fs.readFileSync(championPath, 'utf8'))
  const champions = Object.values(championData.data || {})
  
  console.log(`✅ Champion Data: ${champions.length} champions loaded`)
  console.log('📋 Sample Champions:')
  champions.slice(0, 5).forEach(champ => {
    console.log(`   • ${champ.name} - ${champ.title}`)
    console.log(`     Tags: ${champ.tags.join(', ')}`)
    console.log(`     Difficulty: ${champ.info.difficulty}/10`)
  })
  
  // Verify specific champion file
  const ahriPath = path.join(basePath, 'champion', 'Ahri.json')
  if (fs.existsSync(ahriPath)) {
    const ahriData = JSON.parse(fs.readFileSync(ahriPath, 'utf8'))
    const ahri = ahriData.data?.Ahri
    if (ahri) {
      console.log('\n🎯 Detailed Champion Example (Ahri):')
      console.log(`   Name: ${ahri.name}`)
      console.log(`   Title: ${ahri.title}`)
      console.log(`   Passive: ${ahri.passive?.name}`)
      console.log(`   Abilities: ${ahri.spells?.length || 0} spells`)
      if (ahri.spells && ahri.spells.length > 0) {
        ahri.spells.forEach((spell, i) => {
          console.log(`     ${['Q', 'W', 'E', 'R'][i]}: ${spell.name}`)
        })
      }
      console.log(`   Base Stats:`)
      console.log(`     Health: ${ahri.stats.hp} (+${ahri.stats.hpperlevel}/level)`)
      console.log(`     Mana: ${ahri.stats.mp} (+${ahri.stats.mpperlevel}/level)`)
      console.log(`     Attack Damage: ${ahri.stats.attackdamage} (+${ahri.stats.attackdamageperlevel}/level)`)
    }
  }
  
} catch (error) {
  console.error('❌ Error reading champion data:', error.message)
}

// Check item.json
try {
  const itemPath = path.join(basePath, 'item.json')
  const itemData = JSON.parse(fs.readFileSync(itemPath, 'utf8'))
  const items = Object.values(itemData.data || {})
  
  console.log(`\n✅ Item Data: ${items.length} items loaded`)
  console.log('📦 Sample Items:')
  items.slice(0, 5).forEach(item => {
    console.log(`   • ${item.name}`)
    console.log(`     Description: ${item.plaintext || 'No description'}`)
    if (item.gold) {
      console.log(`     Cost: ${item.gold.total}g`)
    }
    if (item.stats && Object.keys(item.stats).length > 0) {
      const statStr = Object.entries(item.stats).slice(0, 3).map(([stat, value]) => `${stat}: +${value}`).join(', ')
      console.log(`     Stats: ${statStr}`)
    }
  })
  
} catch (error) {
  console.error('❌ Error reading item data:', error.message)
}

console.log('\n🎉 Data verification complete!')