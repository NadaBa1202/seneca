require('dotenv').config();

async function testTwistedApi() {
    console.log('🔍 Investigating Twisted API structure...\n');
    
    try {
        const twisted = require('twisted');
        console.log('Twisted module keys:', Object.keys(twisted));
        
        if (twisted.LolApi) {
            console.log('✅ LolApi found');
            const api = new twisted.LolApi({
                key: process.env.RIOT_API_KEY
            });
            
            console.log('API methods:', Object.getOwnPropertyNames(api));
            
            // Try a simple API call
            console.log('\n🧪 Testing API call...');
            const result = await api.Summoner.getByName('Faker', twisted.Constants.Regions.KOREA);
            console.log('✅ API call successful!');
            console.log('Summoner name:', result.response.name);
            console.log('Summoner level:', result.response.summonerLevel);
            
        } else if (twisted.default) {
            console.log('Using default export...');
            const api = new twisted.default({
                key: process.env.RIOT_API_KEY
            });
        } else {
            console.log('Available exports:', Object.keys(twisted));
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.error('Stack:', error.stack);
    }
}

testTwistedApi();