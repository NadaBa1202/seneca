const axios = require('axios');

const API_BASE = 'http://localhost:3001';
const API_KEY = 'RGAPI-30e37cb1-bf92-4d7e-8ea0-3aab8f28cf9e'; // Your API key

async function testApi() {
    try {
        console.log('🔧 Setting API key...');
        
        // Set the API key
        const keyResponse = await axios.post(`${API_BASE}/api/set-api-key`, {
            apiKey: API_KEY
        });
        console.log('✅ API key set:', keyResponse.data.message);
        
        console.log('\n🧪 Testing API connectivity...');
        
        // Test basic connectivity
        const testResponse = await axios.get(`${API_BASE}/api/test`);
        console.log('✅ API test successful:', testResponse.data.message);
        console.log('   Free champion rotation:', testResponse.data.data.freeChampionIds?.length || 0, 'champions');
        
        console.log('\n🔍 Testing player lookup...');
        
        // Test player lookup with a well-known player
        try {
            const playerResponse = await axios.get(`${API_BASE}/api/player/Doublelift/NA1`);
            console.log('✅ Player lookup successful!');
            console.log('   Player:', playerResponse.data.account.gameName + '#' + playerResponse.data.account.tagLine);
            console.log('   Level:', playerResponse.data.summoner.summonerLevel);
            console.log('   Ranked entries:', playerResponse.data.rankedInfo.length);
            console.log('   Top masteries:', playerResponse.data.masteries.length);
            console.log('   Total mastery score:', playerResponse.data.masteryScore);
        } catch (error) {
            console.log('⚠️ Player lookup failed (trying different player):', error.response?.data?.error || error.message);
            
            // Try a simpler test
            try {
                const simpleTest = await axios.get(`${API_BASE}/api/search/Faker`);
                console.log('✅ Alternative player search worked!');
                console.log('   Found:', simpleTest.data.account.gameName);
            } catch (error2) {
                console.log('❌ Player lookup completely failed:', error2.response?.data?.error || error2.message);
            }
        }
        
        console.log('\n📊 Testing champion rotation...');
        
        // Test champion rotation
        const rotationResponse = await axios.get(`${API_BASE}/api/champion-rotation`);
        console.log('✅ Champion rotation:', rotationResponse.data.freeChampionIds.length, 'free champions');
        
        console.log('\n🎮 Testing featured games...');
        
        // Test featured games
        try {
            const featuredResponse = await axios.get(`${API_BASE}/api/featured-games`);
            console.log('✅ Featured games:', featuredResponse.data.gameList?.length || 0, 'games');
        } catch (error) {
            console.log('⚠️ Featured games failed:', error.response?.data?.error || error.message);
        }
        
        console.log('\n✅ API testing complete! All basic endpoints are working.');
        
    } catch (error) {
        console.error('❌ API test failed:', error.response?.data || error.message);
        
        if (error.response?.status === 403) {
            console.log('\n🔑 API key might be invalid or expired.');
            console.log('   Please check your API key in the Riot Developer Portal.');
        }
    }
}

// Health check
async function healthCheck() {
    try {
        const response = await axios.get(`${API_BASE}/health`);
        console.log('🏥 Health check:', response.data);
        return true;
    } catch (error) {
        console.log('❌ Server not responding. Make sure league_api_server_updated.js is running.');
        return false;
    }
}

async function main() {
    console.log('🚀 Testing League API Server\n');
    
    const isHealthy = await healthCheck();
    if (!isHealthy) {
        return;
    }
    
    await testApi();
}

main();