const axios = require('axios');

// Simple direct API test
async function testRiotApiDirect() {
    const API_KEY = 'YOUR_API_KEY_HERE'; // Replace with your actual API key
    
    console.log('🧪 Testing Riot API directly...\n');
    
    try {
        // Test champion rotation
        console.log('📅 Testing champion rotation...');
        const response = await axios.get('https://na1.api.riotgames.com/lol/platform/v3/champion-rotations', {
            headers: {
                'X-Riot-Token': API_KEY
            }
        });
        
        console.log('✅ Champion rotation successful!');
        console.log(`   Free champions: ${response.data.freeChampionIds.length}`);
        console.log(`   New player champions: ${response.data.freeChampionIdsForNewPlayers.length}`);
        
        // Test account lookup
        console.log('\n🔍 Testing account lookup...');
        const accountResponse = await axios.get('https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Doublelift/NA1', {
            headers: {
                'X-Riot-Token': API_KEY
            }
        });
        
        console.log('✅ Account lookup successful!');
        console.log(`   PUUID: ${accountResponse.data.puuid}`);
        console.log(`   Game Name: ${accountResponse.data.gameName}#${accountResponse.data.tagLine}`);
        
        // Test summoner lookup
        console.log('\n👤 Testing summoner lookup...');
        const summonerResponse = await axios.get(`https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${accountResponse.data.puuid}`, {
            headers: {
                'X-Riot-Token': API_KEY
            }
        });
        
        console.log('✅ Summoner lookup successful!');
        console.log(`   Level: ${summonerResponse.data.summonerLevel}`);
        console.log(`   Profile Icon: ${summonerResponse.data.profileIconId}`);
        
        console.log('\n🎉 All API tests passed! Your API key is working correctly.');
        
    } catch (error) {
        console.error('❌ API test failed:', error.response?.status, error.response?.data || error.message);
        
        if (error.response?.status === 403) {
            console.log('\n🔑 API key might be invalid, expired, or doesn\'t have the required permissions.');
            console.log('   Please check your API key in the Riot Developer Portal.');
        } else if (error.response?.status === 429) {
            console.log('\n⏰ Rate limit exceeded. Please wait and try again.');
        }
    }
}

testRiotApiDirect();