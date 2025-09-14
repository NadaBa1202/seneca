#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🚀 League of Legends Dynamic Features Setup\n');

// Check if .env file exists
const envPath = path.join(__dirname, '.env');
if (!fs.existsSync(envPath)) {
    console.log('📝 Creating .env file...');
    fs.copyFileSync(path.join(__dirname, '.env.example'), envPath);
    console.log('✅ .env file created from .env.example');
    console.log('⚠️  Please edit .env and add your RIOT_API_KEY');
    console.log('   Get your API key from: https://developer.riotgames.com/\n');
} else {
    console.log('✅ .env file already exists\n');
}

// Check if dragontail data exists
const dragontailPath = path.join(__dirname, '..', 'League of legends helper', '15.18.1', 'data', 'en_US');
if (fs.existsSync(dragontailPath)) {
    console.log('✅ Dragontail dataset found');
    
    // Check key files
    const championPath = path.join(dragontailPath, 'champion.json');
    const itemPath = path.join(dragontailPath, 'item.json');
    
    if (fs.existsSync(championPath) && fs.existsSync(itemPath)) {
        console.log('✅ Champion and item data files found');
    } else {
        console.log('❌ Missing champion.json or item.json files');
    }
} else {
    console.log('❌ Dragontail dataset not found');
    console.log('   Expected location:', dragontailPath);
}

console.log('\n📦 Checking dependencies...');

// Check if node_modules exists
if (fs.existsSync(path.join(__dirname, 'node_modules'))) {
    console.log('✅ Node modules installed');
} else {
    console.log('❌ Node modules not found. Run: npm install');
}

// Check package.json scripts
const packagePath = path.join(__dirname, 'package.json');
if (fs.existsSync(packagePath)) {
    const package = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    if (!package.scripts) {
        package.scripts = {};
    }
    
    // Add helpful scripts
    package.scripts['start:api'] = 'node league_api_server.js';
    package.scripts['test:data'] = 'node test_data_services.js';
    package.scripts['test:api'] = 'node test_api_components.js';
    
    fs.writeFileSync(packagePath, JSON.stringify(package, null, 2));
    console.log('✅ Added helpful npm scripts to package.json');
}

console.log('\n🎯 Setup Complete! Next Steps:');
console.log('1. Edit .env file and add your RIOT_API_KEY');
console.log('2. Start the API server: npm run start:api');
console.log('3. Update your React app to use LeagueFeaturesV2.jsx');
console.log('4. Test the data service: npm run test:data');
console.log('5. Test API components: npm run test:api');

console.log('\n🔗 Useful URLs:');
console.log('- Riot Developer Portal: https://developer.riotgames.com/');
console.log('- API Documentation: https://developer.riotgames.com/apis');
console.log('- League Data Dragon: https://developer.riotgames.com/docs/lol#data-dragon');

console.log('\n📚 Features Available:');
console.log('- ✅ Dynamic champion lookup with abilities and stats');
console.log('- ✅ Live player search with rank and match history');
console.log('- ✅ Item database with build paths and stats');
console.log('- ✅ Champion mastery tracking');
console.log('- ✅ Current game detection');
console.log('- 🔄 League-aware chat integration (in progress)');

console.log('\n🎮 Ready to make your League features dynamic!');