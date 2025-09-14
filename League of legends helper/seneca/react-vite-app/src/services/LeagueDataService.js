// Client-side League of Legends data service using dragontail dataset
class LeagueDataService {
  constructor() {
    this.championData = null;
    this.itemData = null;
    this.championDetails = new Map();
    this.baseUrl = '/dragontail';
  }

  /**
   * Load champion data from local dragontail files
   */
  async loadChampions() {
    if (this.championData) {
      return this.championData;
    }

    try {
      const response = await fetch(`${this.baseUrl}/champion.json`);
      const data = await response.json();
      this.championData = Object.values(data.data);
      return this.championData;
    } catch (error) {
      console.error('Error loading champions:', error);
      // Fall back to mock data if files aren't available
      this.championData = this.getMockChampionData();
      return this.championData;
    }
  }

  /**
   * Load item data from local dragontail files
   */
  async loadItems() {
    if (this.itemData) {
      return this.itemData;
    }

    try {
      const response = await fetch(`${this.baseUrl}/item.json`);
      const data = await response.json();
      this.itemData = Object.entries(data.data).map(([id, item]) => ({ ...item, id }));
      return this.itemData;
    } catch (error) {
      console.error('Error loading items:', error);
      // Fall back to mock data if files aren't available
      this.itemData = this.getMockItemData();
      return this.itemData;
    }
  }

  /**
   * Search champions by name or tags
   */
  async searchChampions(query) {
    const champions = await this.loadChampions();
    const searchTerm = query.toLowerCase();

    return champions.filter(champion => {
      return (
        champion.name.toLowerCase().includes(searchTerm) ||
        champion.title.toLowerCase().includes(searchTerm) ||
        champion.tags.some(tag => tag.toLowerCase().includes(searchTerm)) ||
        champion.id.toLowerCase().includes(searchTerm)
      );
    });
  }

  /**
   * Get champion by ID
   */
  async getChampion(championId) {
    const champions = await this.loadChampions();
    const champion = champions.find(c => c.id === championId || c.name.toLowerCase() === championId.toLowerCase());
    
    if (!champion) {
      throw new Error(`Champion '${championId}' not found`);
    }

    // Try to load detailed champion data
    let detailedChampion = champion;
    try {
      const response = await fetch(`${this.baseUrl}/champion/${championId}.json`);
      const data = await response.json();
      detailedChampion = data.data[championId];
    } catch (error) {
      console.warn(`Could not load detailed data for ${championId}, using basic data`);
    }

    return {
      ...detailedChampion,
      abilities: this.getChampionAbilities(detailedChampion),
      detailedStats: this.getChampionStats(detailedChampion)
    };
  }

  /**
   * Search items by name
   */
  async searchItems(query) {
    const items = await this.loadItems();
    const searchTerm = query.toLowerCase();

    return items.filter(item => {
      return (
        item.name.toLowerCase().includes(searchTerm) ||
        item.description.toLowerCase().includes(searchTerm) ||
        (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
      );
    });
  }

  /**
   * Get champion abilities (from real dragontail data or fallback)
   */
  getChampionAbilities(championData) {
    if (championData.spells && championData.passive) {
      // Real dragontail data
      return {
        passive: championData.passive,
        spells: championData.spells.map(spell => ({
          id: spell.id,
          name: spell.name,
          description: spell.description,
          tooltip: spell.tooltip,
          cooldown: spell.cooldown,
          cost: spell.cost,
          range: Array.isArray(spell.range) ? spell.range[0] : spell.range,
          maxrank: spell.maxrank
        }))
      };
    }

    // Fallback for basic champion data
    const championId = championData.id || championData.name;
    const abilityMock = {
      'Ahri': {
        passive: { name: 'Essence Theft', description: 'After killing 9 minions or monsters, Ahri heals. After taking down an enemy champion, Ahri heals for a greater amount.' },
        spells: [
          { name: 'Orb of Deception', description: 'Ahri sends out and pulls back her orb, dealing magic damage on the way out and true damage on the way back.', cooldown: [7, 7, 7, 7, 7], cost: [55, 65, 75, 85, 95], range: 970 },
          { name: 'Fox-Fire', description: 'Ahri gains a brief burst of Move Speed and releases three fox-fires, that lock onto and attack nearby enemies.', cooldown: [10, 9, 8, 7, 6], cost: [30, 30, 30, 30, 30], range: 700 },
          { name: 'Charm', description: 'Ahri blows a kiss that damages and charms an enemy it encounters, instantly stopping movement abilities and causing them to walk harmlessly towards her.', cooldown: [12, 12, 12, 12, 12], cost: [60, 60, 60, 60, 60], range: 975 },
          { name: 'Spirit Rush', description: 'Ahri dashes forward and fires essence bolts, damaging nearby enemies. Spirit Rush can be cast up to three times before going on cooldown.', cooldown: [140, 120, 100], cost: [100, 100, 100], range: 450 }
        ]
      }
    };

    return abilityMock[championId] || {
      passive: { name: 'Unknown Passive', description: 'Passive ability information not available.' },
      spells: [
        { name: 'Q Ability', description: 'Q ability information not available.', cooldown: [0], cost: [0], range: 0 },
        { name: 'W Ability', description: 'W ability information not available.', cooldown: [0], cost: [0], range: 0 },
        { name: 'E Ability', description: 'E ability information not available.', cooldown: [0], cost: [0], range: 0 },
        { name: 'R Ability', description: 'R ability information not available.', cooldown: [0], cost: [0], range: 0 }
      ]
    };
  }

  /**
   * Get champion stats (from real data or fallback)
   */
  getChampionStats(championData) {
    if (championData.stats) {
      // Real dragontail data
      return championData.stats;
    }

    // Fallback for basic champion data
    const championId = championData.id || championData.name;
    const statsMock = {
      'Ahri': {
        hp: 590, hpperlevel: 104, mp: 418, mpperlevel: 25,
        armor: 21, armorperlevel: 4.2, spellblock: 30, spellblockperlevel: 1.3,
        attackdamage: 53, attackdamageperlevel: 3, attackspeed: 0.668, attackspeedperlevel: 2.2
      }
    };

    return statsMock[championId] || {
      hp: 500, hpperlevel: 80, mp: 300, mpperlevel: 40,
      armor: 25, armorperlevel: 3, spellblock: 30, spellblockperlevel: 1,
      attackdamage: 55, attackdamageperlevel: 3, attackspeed: 0.65, attackspeedperlevel: 2
    };
  }

  /**
   * Mock champion data based on our dragontail analysis
   */
  getMockChampionData() {
    return [
      {
        id: 'Ahri',
        key: '103',
        name: 'Ahri',
        title: 'the Nine-Tailed Fox',
        tags: ['Mage', 'Assassin'],
        info: { attack: 3, defense: 4, magic: 8, difficulty: 5 },
        lore: 'Innately connected to the magic of the spirit realm, Ahri is a fox-like vastaya who can manipulate her prey\'s emotions and consume their essence—receiving flashes of their memory and insight from each soul she consumes.',
        image: { full: 'Ahri.png' }
      },
      {
        id: 'Jinx',
        key: '222',
        name: 'Jinx',
        title: 'the Loose Cannon',
        tags: ['Marksman'],
        info: { attack: 9, defense: 2, magic: 4, difficulty: 6 },
        lore: 'A manic and impulsive criminal from Zaun, Jinx lives to wreak havoc without care for the consequences.',
        image: { full: 'Jinx.png' }
      },
      {
        id: 'Yasuo',
        key: '157',
        name: 'Yasuo',
        title: 'the Unforgiven',
        tags: ['Fighter', 'Assassin'],
        info: { attack: 8, defense: 4, magic: 4, difficulty: 10 },
        lore: 'An Ionian of deep resolve, Yasuo is an agile swordsman who wields the air itself against his enemies.',
        image: { full: 'Yasuo.png' }
      },
      {
        id: 'Lux',
        key: '99',
        name: 'Lux',
        title: 'the Lady of Luminosity',
        tags: ['Mage', 'Support'],
        info: { attack: 2, defense: 4, magic: 9, difficulty: 5 },
        lore: 'Luxanna Crownguard hails from Demacia, an insular realm where magical abilities are viewed with fear and suspicion.',
        image: { full: 'Lux.png' }
      },
      {
        id: 'Zed',
        key: '238',
        name: 'Zed',
        title: 'the Master of Shadows',
        tags: ['Assassin'],
        info: { attack: 9, defense: 2, magic: 1, difficulty: 7 },
        lore: 'The contemptuous leader of the Order of Shadow, Zed is an anti-hero fighting to preserve his homeland.',
        image: { full: 'Zed.png' }
      },
      {
        id: 'Thresh',
        key: '412',
        name: 'Thresh',
        title: 'the Chain Warden',
        tags: ['Support'],
        info: { attack: 5, defense: 6, magic: 6, difficulty: 7 },
        lore: 'Sadistic and cunning, Thresh is an ambitious and restless spirit of the Shadow Isles.',
        image: { full: 'Thresh.png' }
      }
    ];
  }

  /**
   * Mock item data
   */
  getMockItemData() {
    return [
      {
        id: '3031',
        name: 'Infinity Edge',
        description: 'Massively increases critical strike damage.',
        plaintext: 'Massively increases critical strike damage.',
        gold: { total: 3450, base: 675 },
        stats: { FlatCritChanceMod: 0.25, FlatPhysicalDamageMod: 65 },
        tags: ['Damage', 'CriticalStrike']
      },
      {
        id: '3006',
        name: 'Berserker\'s Greaves',
        description: 'Enhanced Movement Speed and Attack Speed.',
        plaintext: 'Enhanced Movement Speed and Attack Speed.',
        gold: { total: 1100, base: 500 },
        stats: { FlatMovementSpeedMod: 45, PercentAttackSpeedMod: 0.35 },
        tags: ['Boots', 'AttackSpeed']
      },
      {
        id: '3020',
        name: 'Sorcerer\'s Shoes',
        description: 'Enhanced Movement Speed and Magic Penetration.',
        plaintext: 'Enhanced Movement Speed and Magic Penetration.',
        gold: { total: 1100, base: 500 },
        stats: { FlatMovementSpeedMod: 45, FlatMagicPenetrationMod: 18 },
        tags: ['Boots', 'MagicPenetration']
      },
      {
        id: '3089',
        name: 'Rabadon\'s Deathcap',
        description: 'Massively increases Ability Power.',
        plaintext: 'Massively increases Ability Power.',
        gold: { total: 3600, base: 1250 },
        stats: { FlatMagicDamageMod: 120 },
        tags: ['SpellDamage']
      },
      {
        id: '3047',
        name: 'Plated Steelcaps',
        description: 'Enhanced Movement Speed and Armor. Reduces incoming basic attack damage.',
        plaintext: 'Enhanced Movement Speed and Armor.',
        gold: { total: 1100, base: 500 },
        stats: { FlatMovementSpeedMod: 45, FlatArmorMod: 20 },
        tags: ['Armor', 'Boots']
      }
    ];
  }

  /**
   * Mock player lookup (since we can't use live API without server)
   */
  async searchPlayer(summonerName) {
    // Return mock data for demonstration
    return {
      summoner: {
        name: summonerName,
        summonerLevel: Math.floor(Math.random() * 200) + 50,
        profileIconId: Math.floor(Math.random() * 4000)
      },
      ranked: [
        {
          queueType: 'RANKED_SOLO_5x5',
          tier: ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM'][Math.floor(Math.random() * 5)],
          rank: ['IV', 'III', 'II', 'I'][Math.floor(Math.random() * 4)],
          leaguePoints: Math.floor(Math.random() * 100)
        }
      ],
      mastery: Array.from({ length: 5 }, (_, i) => ({
        championId: Math.floor(Math.random() * 170) + 1,
        championLevel: Math.floor(Math.random() * 7) + 1,
        championPoints: Math.floor(Math.random() * 100000) + 10000
      })),
      currentGame: null,
      recentMatches: Array.from({ length: 3 }, (_, i) => `NA1_${Math.floor(Math.random() * 1000000000)}`)
    };
  }
}

export default LeagueDataService;