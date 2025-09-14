// Dynamic Item Recommendation Service
class DynamicItemService {
  constructor() {
    this.itemData = null;
    this.championData = null;
    this.baseUrl = '/dragontail';
  }

  async loadItemData() {
    if (this.itemData) return this.itemData;
    
    try {
      const response = await fetch(`${this.baseUrl}/item.json`);
      const data = await response.json();
      this.itemData = data.data;
      return this.itemData;
    } catch (error) {
      console.error('Error loading item data:', error);
      return {};
    }
  }

  // Analyze champion tags and recommend item categories
  getItemCategoriesForChampion(champion) {
    const categories = {
      damage: [],
      defense: [],
      utility: [],
      boots: []
    };

    if (!champion.tags) return categories;

    // Damage items based on champion type
    if (champion.tags.includes('Mage')) {
      categories.damage = ['ap_items', 'mana_items', 'cdr_items'];
    }
    if (champion.tags.includes('Marksman')) {
      categories.damage = ['ad_items', 'crit_items', 'attack_speed_items'];
    }
    if (champion.tags.includes('Assassin')) {
      categories.damage = ['ad_items', 'lethality_items', 'ap_items'];
    }
    if (champion.tags.includes('Fighter') || champion.tags.includes('Tank')) {
      categories.damage = ['ad_items', 'health_items'];
      categories.defense = ['armor_items', 'mr_items', 'health_items'];
    }
    if (champion.tags.includes('Support')) {
      categories.utility = ['support_items', 'aura_items', 'cdr_items'];
      categories.defense = ['health_items', 'mr_items'];
    }

    return categories;
  }

  // Get dynamic item recommendations based on champion and game situation
  async getDynamicBuildRecommendations(champion, gameMode = 'ranked', role = 'default') {
    await this.loadItemData();
    
    const categories = this.getItemCategoriesForChampion(champion);
    const recommendations = {
      starter: this.getStarterItems(champion, role),
      core: this.getCoreItems(champion, categories),
      situational: this.getSituationalItems(champion, categories),
      boots: this.getBootsRecommendations(champion),
      lateGame: this.getLateGameItems(champion, categories)
    };

    return recommendations;
  }

  getStarterItems(champion, role) {
    const starters = {
      'Mage': ["Doran's Ring", "Health Potion", "Health Potion"],
      'Marksman': ["Doran's Blade", "Health Potion"],
      'Support': ["Relic Shield", "Health Potion", "Health Potion"],
      'Tank': ["Doran's Shield", "Health Potion"],
      'Fighter': ["Doran's Blade", "Health Potion"],
      'Assassin': ["Doran's Blade", "Health Potion"]
    };

    if (role === 'support') {
      return ["Spectral Sickle", "Health Potion", "Stealth Ward"];
    }

    for (const tag of champion.tags || []) {
      if (starters[tag]) {
        return starters[tag];
      }
    }

    return ["Doran's Ring", "Health Potion"];
  }

  getCoreItems(champion, categories) {
    const coreBuilds = {
      'Mage': [
        "Luden's Tempest",
        "Sorcerer's Shoes", 
        "Shadowflame",
        "Zhonya's Hourglass"
      ],
      'Marksman': [
        "Galeforce",
        "Berserker's Greaves",
        "The Collector",
        "Infinity Edge"
      ],
      'Assassin': [
        "Duskblade of Draktharr",
        "Ionian Boots of Lucidity",
        "Youmuu's Ghostblade",
        "Edge of Night"
      ],
      'Tank': [
        "Sunfire Aegis",
        "Plated Steelcaps",
        "Thornmail",
        "Spirit Visage"
      ],
      'Fighter': [
        "Divine Sunderer",
        "Plated Steelcaps",
        "Sterak's Gage",
        "Death's Dance"
      ],
      'Support': [
        "Locket of the Iron Solari",
        "Mobility Boots",
        "Knight's Vow",
        "Redemption"
      ]
    };

    for (const tag of champion.tags || []) {
      if (coreBuilds[tag]) {
        return coreBuilds[tag];
      }
    }

    return ["Situational build - check pro builds"];
  }

  getSituationalItems(champion, categories) {
    const situational = {
      antiHeal: ["Morellonomicon", "Thornmail", "Chempunk Chainsword"],
      antiTank: ["Void Staff", "Lord Dominik's Regards", "Serylda's Grudge"],
      survivability: ["Guardian Angel", "Banshee's Veil", "Edge of Night"],
      utility: ["Redemption", "Mikael's Blessing", "Shurelya's Battlesong"],
      damage: ["Rabadon's Deathcap", "Infinity Edge", "Manamune"]
    };

    const recommendations = {};
    
    // Add situational items based on champion type
    if (champion.tags?.includes('Mage')) {
      recommendations.burst = ["Rabadon's Deathcap", "Void Staff"];
      recommendations.survivability = ["Zhonya's Hourglass", "Banshee's Veil"];
    }
    
    if (champion.tags?.includes('Marksman')) {
      recommendations.damage = ["Infinity Edge", "Lord Dominik's Regards"];
      recommendations.survivability = ["Guardian Angel", "Mercurial Scimitar"];
    }

    if (champion.tags?.includes('Tank')) {
      recommendations.engage = ["Righteous Glory", "Dead Man's Plate"];
      recommendations.antiCarry = ["Randuin's Omen", "Frozen Heart"];
    }

    return recommendations;
  }

  getBootsRecommendations(champion) {
    const bootsOptions = {
      'Mage': {
        standard: "Sorcerer's Shoes",
        alternatives: ["Ionian Boots of Lucidity", "Mercury's Treads"]
      },
      'Marksman': {
        standard: "Berserker's Greaves",
        alternatives: ["Mercury's Treads", "Plated Steelcaps"]
      },
      'Tank': {
        standard: "Plated Steelcaps",
        alternatives: ["Mercury's Treads", "Mobility Boots"]
      },
      'Support': {
        standard: "Mobility Boots",
        alternatives: ["Ionian Boots of Lucidity", "Mercury's Treads"]
      }
    };

    for (const tag of champion.tags || []) {
      if (bootsOptions[tag]) {
        return bootsOptions[tag];
      }
    }

    return {
      standard: "Ionian Boots of Lucidity",
      alternatives: ["Mercury's Treads", "Plated Steelcaps"]
    };
  }

  getLateGameItems(champion, categories) {
    const lateGameOptimal = {
      'Mage': ["Rabadon's Deathcap", "Void Staff", "Cosmic Drive"],
      'Marksman': ["Infinity Edge", "Lord Dominik's Regards", "Bloodthirster"],
      'Tank': ["Gargoyle Stoneplate", "Warmog's Armor", "Force of Nature"],
      'Assassin': ["Youmuu's Ghostblade", "Serpent's Fang", "Guardian Angel"]
    };

    for (const tag of champion.tags || []) {
      if (lateGameOptimal[tag]) {
        return lateGameOptimal[tag];
      }
    }

    return ["Game state dependent items"];
  }

  // Generate build path with reasoning
  generateBuildPath(champion, gameLength = 'normal') {
    const path = {
      early: {
        items: this.getStarterItems(champion),
        reasoning: "Focus on sustain and early game trading"
      },
      mid: {
        items: this.getCoreItems(champion).slice(0, 3),
        reasoning: "Core power spike items for teamfights"
      },
      late: {
        items: this.getLateGameItems(champion),
        reasoning: "Maximize damage/utility for late game"
      }
    };

    return path;
  }

  // Get counters and adaptations
  getCounterBuilds(champion, againstChampions = []) {
    const adaptations = {
      antiAP: ["Mercury's Treads", "Spirit Visage", "Banshee's Veil"],
      antiAD: ["Plated Steelcaps", "Thornmail", "Guardian Angel"],
      antiHeal: ["Morellonomicon", "Thornmail", "Chempunk Chainsword"],
      antiTank: ["Void Staff", "Lord Dominik's Regards", "Black Cleaver"]
    };

    // Analyze enemy champions and suggest adaptations
    const recommendations = [];
    
    // This would be enhanced with actual enemy champion analysis
    recommendations.push({
      situation: "Against heavy AP",
      items: adaptations.antiAP,
      reasoning: "Build magic resist to survive burst"
    });

    return recommendations;
  }
}

export default DynamicItemService;