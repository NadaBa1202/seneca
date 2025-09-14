require('dotenv').config();
const axios = require('axios');

async function testDirectApiCall() {
    console.log('🧪 Testing Direct Riot API Call...\n');
    
    const apiKey = process.env.RIOT_API_KEY;
    console.log('API Key:', apiKey.substring(0, 10) + '...');
    
    try {
        // Try the exact API format from Riot's documentation
        const url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Doublelift';
        
        console.log('Testing URL:', url);
        console.log('Headers: X-Riot-Token');
        
        const response = await axios.get(url, {
            headers: {
                'X-Riot-Token': apiKey
            },
            timeout: 10000
        });
        
        console.log('✅ Success!');
        console.log('Summoner:', response.data.name);
        console.log('Level:', response.data.summonerLevel);
        console.log('PUUID:', response.data.puuid.substring(0, 10) + '...');
        
    } catch (error) {
        console.error('❌ Error Details:');
        console.error('Status:', error.response?.status);
        console.error('Status Text:', error.response?.statusText);
        console.error('Data:', JSON.stringify(error.response?.data, null, 2));
        console.error('URL:', error.config?.url);
        console.error('Headers:', error.config?.headers);
        
        if (error.response?.status === 403) {
            console.log('\n🔍 Troubleshooting 403 Forbidden:');
            console.log('1. Make sure your API key is from https://developer.riotgames.com/');
            console.log('2. API keys expire every 24 hours');
            console.log('3. Make sure you\'re logged in to your Riot account when generating the key');
            console.log('4. Try a different summoner name (some may have special characters)');
        }
    }
}

testDirectApiCall();