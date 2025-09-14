const fs = require('fs');
const path = require('path');

class DragontailDataService {
    constructor() {
        this.dataPath = path.join(__dirname, '..', '..', 'League of legends helper', '15.18.1', 'data', 'en_US');
        this.champions = null;
        this.items = null;
        this.championDetails = new Map();
        this.version = '15.18.1';
    }

    /**
     * Load champion data from dragontail dataset
     * @returns {Promise} Champion data
     */
    async loadChampions() {
        if (this.champions) {
            return this.champions;
        }

        try {
            const championPath = path.join(this.dataPath, 'champion.json');
            const data = JSON.parse(fs.readFileSync(championPath, 'utf8'));
            this.champions = data.data;
            return this.champions;
        } catch (error) {
            console.error('Error loading champions:', error);
            throw new Error('Failed to load champion data');
        }
    }

    /**
     * Load item data from dragontail dataset
     * @returns {Promise} Item data
     */
    async loadItems() {
        if (this.items) {
            return this.items;
        }

        try {
            const itemPath = path.join(this.dataPath, 'item.json');
            const data = JSON.parse(fs.readFileSync(itemPath, 'utf8'));
            this.items = data.data;
            return this.items;
        } catch (error) {
            console.error('Error loading items:', error);
            throw new Error('Failed to load item data');
        }
    }

    /**
     * Get detailed champion information including abilities
     * @param {string} championKey - Champion key (e.g., 'Ahri')
     * @returns {Promise} Detailed champion data
     */
    async getChampionDetails(championKey) {
        if (this.championDetails.has(championKey)) {
            return this.championDetails.get(championKey);
        }

        try {
            const championPath = path.join(this.dataPath, 'champion', `${championKey}.json`);
            const data = JSON.parse(fs.readFileSync(championPath, 'utf8'));
            const championData = data.data[championKey];
            
            this.championDetails.set(championKey, championData);
            return championData;
        } catch (error) {
            console.error(`Error loading champion details for ${championKey}:`, error);
            throw new Error(`Failed to load champion details for ${championKey}`);
        }
    }

    /**
     * Search for champions by name or tags
     * @param {string} query - Search query
     * @returns {Promise} Array of matching champions
     */
    async searchChampions(query) {
        const champions = await this.loadChampions();
        const searchTerm = query.toLowerCase();

        return Object.values(champions).filter(champion => {
            return (
                champion.name.toLowerCase().includes(searchTerm) ||
                champion.title.toLowerCase().includes(searchTerm) ||
                champion.tags.some(tag => tag.toLowerCase().includes(searchTerm)) ||
                champion.id.toLowerCase().includes(searchTerm)
            );
        });
    }

    /**
     * Get champion by exact name or ID
     * @param {string} identifier - Champion name or ID
     * @returns {Promise} Champion data
     */
    async getChampion(identifier) {
        const champions = await this.loadChampions();
        
        // Try exact match first
        let champion = champions[identifier];
        if (champion) {
            return await this.getChampionDetails(identifier);
        }

        // Try case-insensitive name match
        for (const [key, champ] of Object.entries(champions)) {
            if (champ.name.toLowerCase() === identifier.toLowerCase() || 
                champ.id.toLowerCase() === identifier.toLowerCase()) {
                return await this.getChampionDetails(key);
            }
        }

        throw new Error(`Champion '${identifier}' not found`);
    }

    /**
     * Get item by ID or name
     * @param {string} identifier - Item ID or name
     * @returns {Promise} Item data
     */
    async getItem(identifier) {
        const items = await this.loadItems();
        
        // Try exact ID match first
        let item = items[identifier];
        if (item) {
            return { ...item, id: identifier };
        }

        // Try case-insensitive name match
        for (const [id, itemData] of Object.entries(items)) {
            if (itemData.name.toLowerCase() === identifier.toLowerCase()) {
                return { ...itemData, id };
            }
        }

        throw new Error(`Item '${identifier}' not found`);
    }

    /**
     * Search for items by name or tags
     * @param {string} query - Search query
     * @returns {Promise} Array of matching items
     */
    async searchItems(query) {
        const items = await this.loadItems();
        const searchTerm = query.toLowerCase();

        return Object.entries(items)
            .filter(([id, item]) => {
                return (
                    item.name.toLowerCase().includes(searchTerm) ||
                    item.description.toLowerCase().includes(searchTerm) ||
                    (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
                );
            })
            .map(([id, item]) => ({ ...item, id }));
    }

    /**
     * Get champion statistics and info
     * @param {string} championKey - Champion key
     * @returns {Promise} Champion stats and info
     */
    async getChampionStats(championKey) {
        const champion = await this.getChampionDetails(championKey);
        
        return {
            name: champion.name,
            title: champion.title,
            tags: champion.tags,
            info: champion.info, // attack, defense, magic, difficulty
            stats: champion.stats, // hp, mp, armor, etc.
            lore: champion.lore,
            tips: {
                ally: champion.allytips,
                enemy: champion.enemytips
            }
        };
    }

    /**
     * Get champion abilities
     * @param {string} championKey - Champion key
     * @returns {Promise} Champion abilities
     */
    async getChampionAbilities(championKey) {
        const champion = await this.getChampionDetails(championKey);
        
        return {
            passive: champion.passive,
            spells: champion.spells.map(spell => ({
                id: spell.id,
                name: spell.name,
                description: spell.description,
                tooltip: spell.tooltip,
                cooldown: spell.cooldown,
                cost: spell.cost,
                range: spell.range,
                maxrank: spell.maxrank
            }))
        };
    }

    /**
     * Get all champions with basic info
     * @returns {Promise} Array of all champions
     */
    async getAllChampions() {
        const champions = await this.loadChampions();
        
        return Object.values(champions).map(champion => ({
            id: champion.id,
            key: champion.key,
            name: champion.name,
            title: champion.title,
            tags: champion.tags,
            info: champion.info,
            image: champion.image
        }));
    }

    /**
     * Get build recommendations for items
     * @param {string} itemId - Item ID
     * @returns {Promise} Build path information
     */
    async getItemBuildPath(itemId) {
        const item = await this.getItem(itemId);
        const items = await this.loadItems();
        
        const buildPath = {
            item: item,
            buildsFrom: [],
            buildsInto: []
        };

        // Find what this item builds from
        if (item.from) {
            buildPath.buildsFrom = item.from.map(fromId => ({
                id: fromId,
                ...items[fromId]
            }));
        }

        // Find what builds into this item
        for (const [id, otherItem] of Object.entries(items)) {
            if (otherItem.from && otherItem.from.includes(itemId)) {
                buildPath.buildsInto.push({
                    id,
                    ...otherItem
                });
            }
        }

        return buildPath;
    }

    /**
     * Get image URL for champion or item
     * @param {string} type - 'champion' or 'item'
     * @param {string} imageName - Image filename
     * @returns {string} Image URL
     */
    getImageUrl(type, imageName) {
        return `https://ddragon.leagueoflegends.com/cdn/${this.version}/img/${type}/${imageName}`;
    }
}

module.exports = DragontailDataService;