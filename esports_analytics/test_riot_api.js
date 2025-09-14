require('dotenv').config();

async function testRiotApiKey() {
    console.log('🔑 Testing Riot API Key...\n');
    
    const apiKey = process.env.RIOT_API_KEY;
    console.log('API Key found:', apiKey ? '✅ Yes' : '❌ No');
    console.log('API Key length:', apiKey ? apiKey.length : 0);
    console.log('API Key starts with RGAPI:', apiKey ? apiKey.startsWith('RGAPI-') : false);
    
    if (!apiKey || !apiKey.startsWith('RGAPI-')) {
        console.log('❌ Invalid API key format');
        return;
    }
    
    try {
        const { Twisted, Constants } = require('twisted');
        const api = new Twisted({
            rateLimitRetry: true,
            rateLimitRetryAttempts: 3,
            key: apiKey
        });
        
        console.log('\n✅ Twisted API client created successfully');
        
        // Try a simple API call
        console.log('\n🧪 Testing API call to get a summoner...');
        const summoner = await api.Summoner.getByName('Faker', Constants.Regions.KOREA);
        console.log('✅ API call successful! Summoner level:', summoner.response.summonerLevel);
        
    } catch (error) {
        console.error('❌ API test failed:', error.message);
        if (error.status) {
            console.error('Status code:', error.status);
        }
        if (error.status === 401) {
            console.error('🔑 API key is invalid or expired');
        }
        if (error.status === 429) {
            console.error('⏰ Rate limit exceeded');
        }
    }
}

testRiotApiKey();