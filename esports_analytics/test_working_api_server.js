const axios = require('axios');

async function testApiServer() {
    const baseUrl = 'http://localhost:3001';
    
    console.log('🚀 Testing League API Server with working key...\n');
    
    try {
        // Test health check
        console.log('❤️ Testing health check...');
        const healthResponse = await axios.get(`${baseUrl}/health`);
        console.log('✅ Health check:', healthResponse.data);
        
        // Test API key test endpoint
        console.log('\n🧪 Testing API connectivity...');
        const testResponse = await axios.get(`${baseUrl}/api/test`);
        console.log('✅ API test:', testResponse.data.message);
        console.log(`   Free champions in rotation: ${testResponse.data.data.freeChampionIds.length}`);
        
        // Test player lookup
        console.log('\n🔍 Testing player lookup...');
        const playerResponse = await axios.get(`${baseUrl}/api/player/Doublelift/NA1`);
        console.log('✅ Player lookup successful!');
        console.log(`   Player: ${playerResponse.data.account.gameName}#${playerResponse.data.account.tagLine}`);
        console.log(`   Level: ${playerResponse.data.summoner.summonerLevel}`);
        console.log(`   Mastery Score: ${playerResponse.data.masteryScore}`);
        console.log(`   Top Champion Masteries: ${playerResponse.data.masteries.length}`);
        console.log(`   Recent Matches: ${playerResponse.data.recentMatches.length}`);
        
        if (playerResponse.data.rankedInfo && playerResponse.data.rankedInfo.length > 0) {
            const soloRank = playerResponse.data.rankedInfo.find(r => r.queueType === 'RANKED_SOLO_5x5');
            if (soloRank) {
                console.log(`   Ranked: ${soloRank.tier} ${soloRank.rank} (${soloRank.leaguePoints} LP)`);
                console.log(`   Win Rate: ${Math.round((soloRank.wins / (soloRank.wins + soloRank.losses)) * 100)}%`);
            }
        }
        
        // Test champion rotation
        console.log('\n📅 Testing champion rotation...');
        const rotationResponse = await axios.get(`${baseUrl}/api/champion-rotation`);
        console.log('✅ Champion rotation successful!');
        console.log(`   Free champions: ${rotationResponse.data.freeChampionIds.length}`);
        
        console.log('\n🎉 All API server tests passed! The League assistant is fully functional.');
        
    } catch (error) {
        console.error('❌ API server test failed:', error.response?.status, error.response?.data || error.message);
    }
}

testApiServer();