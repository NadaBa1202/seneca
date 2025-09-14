import fetch from 'node-fetch'

async function testDragontailData() {
  const baseUrl = 'http://localhost:5175'
  
  console.log('🧪 Testing Dragontail Data Loading...\n')
  
  try {
    // Test champion.json
    console.log('📋 Testing Champion Data...')
    const champResponse = await fetch(`${baseUrl}/dragontail/champion.json`)
    if (champResponse.ok) {
      const champData = await champResponse.json()
      console.log(`✅ Champions loaded: ${Object.keys(champData.data || {}).length} champions`)
      
      // Show first few champions
      const champions = Object.values(champData.data || {}).slice(0, 5)
      champions.forEach(champ => {
        console.log(`   - ${champ.name}: ${champ.title}`)
      })
    } else {
      console.log(`❌ Champion data failed: ${champResponse.status}`)
    }
    
    console.log('\n📦 Testing Item Data...')
    const itemResponse = await fetch(`${baseUrl}/dragontail/item.json`)
    if (itemResponse.ok) {
      const itemData = await itemResponse.json()
      console.log(`✅ Items loaded: ${Object.keys(itemData.data || {}).length} items`)
      
      // Show first few items
      const items = Object.values(itemData.data || {}).slice(0, 5)
      items.forEach(item => {
        console.log(`   - ${item.name}: ${item.plaintext || 'No description'}`)
      })
    } else {
      console.log(`❌ Item data failed: ${itemResponse.status}`)
    }
    
    // Test specific champion
    console.log('\n🎯 Testing Specific Champion (Ahri)...')
    const ahriResponse = await fetch(`${baseUrl}/dragontail/champion/Ahri.json`)
    if (ahriResponse.ok) {
      const ahriData = await ahriResponse.json()
      const ahri = ahriData.data?.Ahri
      if (ahri) {
        console.log(`✅ Ahri data loaded:`)
        console.log(`   - Name: ${ahri.name}`)
        console.log(`   - Title: ${ahri.title}`)
        console.log(`   - Passive: ${ahri.passive?.name}`)
        console.log(`   - Abilities: ${ahri.spells?.length || 0} spells`)
        if (ahri.spells && ahri.spells.length > 0) {
          ahri.spells.forEach((spell, i) => {
            console.log(`     ${['Q', 'W', 'E', 'R'][i]}: ${spell.name}`)
          })
        }
        console.log(`   - Lore: ${ahri.lore?.slice(0, 100)}...`)
      }
    } else {
      console.log(`❌ Ahri data failed: ${ahriResponse.status}`)
    }
    
  } catch (error) {
    console.error('❌ Error testing data:', error.message)
  }
}

// Run the test
testDragontailData()