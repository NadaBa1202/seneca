require('dotenv').config();

async function exploreTwistedApi() {
    console.log('🔍 Exploring Twisted API methods...\n');
    
    try {
        const { LolApi, Constants } = require('twisted');
        const api = new LolApi({
            key: process.env.RIOT_API_KEY
        });
        
        console.log('Summoner methods:', Object.getOwnPropertyNames(api.Summoner));
        console.log('Match methods:', Object.getOwnPropertyNames(api.Match));
        console.log('League methods:', Object.getOwnPropertyNames(api.League));
        
        // Let's try the correct method name
        if (typeof api.Summoner.getByName === 'function') {
            console.log('\n✅ getByName is available');
        } else if (typeof api.Summoner.get === 'function') {
            console.log('\n✅ get method available');
        } else {
            console.log('\nAvailable Summoner methods:');
            Object.getOwnPropertyNames(api.Summoner).forEach(method => {
                if (typeof api.Summoner[method] === 'function') {
                    console.log(`  - ${method}`);
                }
            });
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

exploreTwistedApi();