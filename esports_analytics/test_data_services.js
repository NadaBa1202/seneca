const DragontailDataService = require('./services/dragontail_data');

async function testDragontailService() {
    const dataService = new DragontailDataService();
    
    try {
        console.log('🧪 Testing Dragontail Data Service...\n');
        
        // Test champion loading
        console.log('📖 Loading all champions...');
        const champions = await dataService.loadChampions();
        console.log(`✅ Loaded ${Object.keys(champions).length} champions\n`);
        
        // Test champion search
        console.log('🔍 Searching for "fox" champions...');
        const foxChampions = await dataService.searchChampions('fox');
        console.log(`✅ Found ${foxChampions.length} champions:`, foxChampions.map(c => c.name).join(', '), '\n');
        
        // Test champion details
        console.log('📋 Getting Ahri details...');
        const ahri = await dataService.getChampion('Ahri');
        console.log(`✅ Ahri loaded: ${ahri.name} - ${ahri.title}`);
        console.log(`   Tags: ${ahri.tags.join(', ')}`);
        console.log(`   Difficulty: ${ahri.info.difficulty}/10\n`);
        
        // Test champion abilities
        console.log('⚡ Getting Ahri abilities...');
        const abilities = await dataService.getChampionAbilities('Ahri');
        console.log(`✅ Abilities loaded:`);
        console.log(`   Passive: ${abilities.passive.name}`);
        abilities.spells.forEach((spell, index) => {
            console.log(`   ${['Q', 'W', 'E', 'R'][index]}: ${spell.name}`);
        });
        console.log();
        
        // Test item loading
        console.log('🛡️ Loading all items...');
        const items = await dataService.loadItems();
        console.log(`✅ Loaded ${Object.keys(items).length} items\n`);
        
        // Test item search
        console.log('🔍 Searching for "sword" items...');
        const swordItems = await dataService.searchItems('sword');
        console.log(`✅ Found ${swordItems.length} items:`, swordItems.slice(0, 5).map(i => i.name).join(', '), '\n');
        
        // Test specific item
        console.log('🗡️ Getting Infinity Edge details...');
        const ie = await dataService.getItem('3031');
        console.log(`✅ Item loaded: ${ie.name}`);
        console.log(`   Gold: ${ie.gold.total} (${ie.gold.base} base)`);
        console.log(`   Stats: ${JSON.stringify(ie.stats, null, 2)}\n`);
        
        // Test build path
        console.log('🔧 Getting Infinity Edge build path...');
        const buildPath = await dataService.getItemBuildPath('3031');
        console.log(`✅ Build path:`);
        console.log(`   Builds from: ${buildPath.buildsFrom.map(i => i.name).join(', ')}`);
        console.log(`   Builds into: ${buildPath.buildsInto.map(i => i.name).join(', ')}\n`);
        
        console.log('🎉 All tests passed! Dragontail service is working correctly.');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        console.error(error);
    }
}

// Run the test
testDragontailService();