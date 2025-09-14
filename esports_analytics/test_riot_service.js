require('dotenv').config();
const RiotApiService = require('./services/riot_api');

async function testRiotApiService() {
    console.log('🧪 Testing Updated Riot API Service...\n');
    
    try {
        const riotApi = new RiotApiService();
        console.log('✅ RiotApiService initialized');
        
        // Test with a well-known summoner
        console.log('\n🔍 Testing getSummonerByName...');
        const summoner = await riotApi.getSummonerByName('Faker', 'kr');
        console.log('✅ Summoner found:', summoner.name, 'Level:', summoner.summonerLevel);
        
        console.log('\n🏆 Testing getRankedInfo...');
        const ranked = await riotApi.getRankedInfo(summoner.id, 'kr');
        console.log('✅ Ranked info retrieved:', ranked.length, 'queue(s)');
        
        console.log('\n🏅 Testing getChampionMastery...');
        const mastery = await riotApi.getChampionMastery(summoner.id, 'kr');
        console.log('✅ Champion mastery retrieved:', mastery.length, 'champions');
        if (mastery.length > 0) {
            console.log('   Top champion:', mastery[0].championId, 'Level:', mastery[0].championLevel);
        }
        
        console.log('\n🎮 Testing getCurrentGame...');
        const currentGame = await riotApi.getCurrentGame(summoner.id, 'kr');
        if (currentGame) {
            console.log('✅ Currently in game:', currentGame.gameMode);
        } else {
            console.log('✅ Not currently in game');
        }
        
        console.log('\n🎯 All API tests passed!');
        
    } catch (error) {
        console.error('❌ API test failed:', error.message);
        
        if (error.message.includes('401')) {
            console.error('🔑 API key is invalid or expired');
        } else if (error.message.includes('429')) {
            console.error('⏰ Rate limit exceeded - try again later');
        } else if (error.message.includes('403')) {
            console.error('🚫 Forbidden - check API key permissions');
        }
    }
}

testRiotApiService();