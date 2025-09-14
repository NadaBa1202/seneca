require('dotenv').config();
const RiotApiService = require('./services/riot_api');

async function testBasicApiCall() {
    console.log('🧪 Testing Basic API Call...\n');
    
    try {
        const riotApi = new RiotApiService();
        console.log('API Key:', process.env.RIOT_API_KEY ? 'Present' : 'Missing');
        console.log('API Key Length:', process.env.RIOT_API_KEY?.length);
        
        // Try a simple NA summoner lookup
        console.log('\n🔍 Testing with NA summoner...');
        const summoner = await riotApi.getSummonerByName('Doublelift', 'na1');
        console.log('✅ Summoner found:', summoner.name);
        
    } catch (error) {
        console.error('❌ API Error:', error.message);
        
        // Let's check what the actual error response looks like
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Data:', error.response.data);
        }
        
        console.log('\n💡 Note: API keys from developer.riotgames.com expire every 24 hours');
        console.log('   You may need to get a new key from: https://developer.riotgames.com/');
        console.log('   For now, we can still test the dragontail data service!');
    }
}

testBasicApiCall();