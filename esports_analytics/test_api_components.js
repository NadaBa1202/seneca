const fs = require('fs');
const path = require('path');

// Simple test to verify our API components work before starting the server
async function testApiComponents() {
    console.log('🧪 Testing API Components...\n');
    
    try {
        // Test dragontail data service
        const DragontailDataService = require('./services/dragontail_data');
        const dataService = new DragontailDataService();
        
        console.log('✅ DragontailDataService imported successfully');
        
        // Test loading champions
        const champions = await dataService.loadChampions();
        console.log(`✅ Loaded ${Object.keys(champions).length} champions`);
        
        // Test champion search
        const searchResults = await dataService.searchChampions('fire');
        console.log(`✅ Champion search working: found ${searchResults.length} fire-related champions`);
        
        // Test specific champion
        const ahri = await dataService.getChampion('Ahri');
        console.log(`✅ Champion details working: ${ahri.name} loaded with ${ahri.spells.length} abilities`);
        
        // Test items
        const items = await dataService.loadItems();
        console.log(`✅ Loaded ${Object.keys(items).length} items`);
        
        // Test Riot API service (without actual API call)
        const RiotApiService = require('./services/riot_api');
        const riotApi = new RiotApiService();
        console.log('✅ RiotApiService imported successfully');
        
        console.log('\n🎉 All API components are working correctly!');
        console.log('\n📋 Next steps:');
        console.log('1. Set your RIOT_API_KEY in a .env file');
        console.log('2. Start the API server: node league_api_server.js');
        console.log('3. Update your React app to use LeagueFeaturesV2.jsx');
        console.log('4. Make sure CORS is properly configured for your React app');
        
    } catch (error) {
        console.error('❌ Component test failed:', error.message);
        console.error('\n🔧 Check the following:');
        console.error('- Make sure dragontail dataset is in the correct location');
        console.error('- Verify all npm packages are installed');
        console.error('- Check file paths in the services');
    }
}

testApiComponents();