console.log('🔧 Minimal API Server Test...\n');

try {
    require('dotenv').config();
    console.log('✅ dotenv loaded');
    
    const express = require('express');
    console.log('✅ express loaded');
    
    const cors = require('cors');
    console.log('✅ cors loaded');
    
    const DragontailDataService = require('./services/dragontail_data');
    console.log('✅ DragontailDataService loaded');
    
    const app = express();
    app.use(cors());
    app.use(express.json());
    
    // Simple health check
    app.get('/api/health', (req, res) => {
        res.json({ status: 'OK', timestamp: new Date().toISOString() });
    });
    
    // Test dragontail endpoint
    app.get('/api/test-champions', async (req, res) => {
        try {
            const dataService = new DragontailDataService();
            const champions = await dataService.loadChampions();
            res.json({ 
                status: 'success', 
                championCount: Object.keys(champions).length,
                sample: Object.keys(champions).slice(0, 5)
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
    
    const PORT = 3001;
    app.listen(PORT, () => {
        console.log(`✅ Server running on port ${PORT}`);
        console.log('Test URLs:');
        console.log(`  http://localhost:${PORT}/api/health`);
        console.log(`  http://localhost:${PORT}/api/test-champions`);
    });
    
} catch (error) {
    console.error('❌ Startup error:', error.message);
    console.error(error.stack);
}