// Enhanced Dynamic Item Recommendation Service with AI-driven insights
class EnhancedDynamicItemService {
  constructor() {
    this.itemData = null;
    this.championData = null;
    this.baseUrl = '/dragontail';
    this.proBuilds = this.initializeProBuilds();
    this.metaItems = this.initializeMetaItems();
    this.synergies = this.initializeSynergies();
    this.counterItems = this.initializeCounterItems();
    this.adaptiveRecommendations = this.initializeAdaptiveRecommendations();
  }

  initializeProBuilds() {
    return {
      'Jinx': {
        core: ['Kraken Slayer', 'Phantom Dancer', 'Infinity Edge'],
        boots: ['Berserker\'s Greaves'],
        situational: ['Lord Dominik\'s Regards', 'Guardian Angel', 'Bloodthirster'],
        winRate: 0.68,
        pickRate: 0.12,
        role: 'ADC',
        gameLength: { early: 0.45, mid: 0.72, late: 0.68 }
      },
      'Ahri': {
        core: ['Luden\'s Tempest', 'Shadowflame', 'Zhonya\'s Hourglass'],
        boots: ['Sorcerer\'s Shoes'],
        situational: ['Banshee\'s Veil', 'Void Staff', 'Rabadon\'s Deathcap'],
        winRate: 0.72,
        pickRate: 0.08,
        role: 'Mid',
        gameLength: { early: 0.65, mid: 0.74, late: 0.71 }
      },
      'Thresh': {
        core: ['Zeke\'s Convergence', 'Locket of the Iron Solari', 'Thornmail'],
        boots: ['Mobility Boots'],
        situational: ['Knight\'s Vow', 'Redemption', 'Mikael\'s Blessing'],
        winRate: 0.65,
        pickRate: 0.15,
        role: 'Support',
        gameLength: { early: 0.55, mid: 0.68, late: 0.65 }
      },
      'Yasuo': {
        core: ['Immortal Shieldbow', 'Infinity Edge', 'Phantom Dancer'],
        boots: ['Berserker\'s Greaves'],
        situational: ['Death\'s Dance', 'Bloodthirster', 'Guardian Angel'],
        winRate: 0.58,
        pickRate: 0.18,
        role: 'Mid',
        gameLength: { early: 0.48, mid: 0.62, late: 0.58 }
      },
      'Graves': {
        core: ['Eclipse', 'The Collector', 'Infinity Edge'],
        boots: ['Berserker\'s Greaves'],
        situational: ['Death\'s Dance', 'Maw of Malmortius', 'Guardian Angel'],
        winRate: 0.63,
        pickRate: 0.09,
        role: 'Jungle',
        gameLength: { early: 0.68, mid: 0.65, late: 0.58 }
      },
      'Lux': {
        core: ['Luden\'s Tempest', 'Horizon Focus', 'Zhonya\'s Hourglass'],
        boots: ['Sorcerer\'s Shoes'],
        situational: ['Banshee\'s Veil', 'Void Staff', 'Rabadon\'s Deathcap'],
        winRate: 0.66,
        pickRate: 0.11,
        role: 'Support',
        gameLength: { early: 0.58, mid: 0.69, late: 0.66 }
      }
    };
  }

  initializeMetaItems() {
    return {
      'ADC': {
        mythic: ['Kraken Slayer', 'Galeforce', 'Immortal Shieldbow'],
        core: ['Phantom Dancer', 'Infinity Edge', 'Lord Dominik\'s Regards'],
        lategame: ['Bloodthirster', 'Guardian Angel', 'Mercurial Scimitar'],
        priority: { damage: 0.7, survivability: 0.2, utility: 0.1 }
      },
      'Mid': {
        mythic: ['Luden\'s Tempest', 'Liandry\'s Anguish', 'Everfrost'],
        core: ['Shadowflame', 'Zhonya\'s Hourglass', 'Void Staff'],
        lategame: ['Rabadon\'s Deathcap', 'Cosmic Drive', 'Banshee\'s Veil'],
        priority: { damage: 0.6, survivability: 0.3, utility: 0.1 }
      },
      'Support': {
        mythic: ['Locket of the Iron Solari', 'Imperial Mandate', 'Shurelya\'s Battlesong'],
        core: ['Knight\'s Vow', 'Redemption', 'Staff of Flowing Water'],
        lategame: ['Mikael\'s Blessing', 'Wardstone', 'Zeke\'s Convergence'],
        priority: { utility: 0.5, survivability: 0.3, damage: 0.2 }
      },
      'Jungle': {
        mythic: ['Eclipse', 'Goredrinker', 'Divine Sunderer'],
        core: ['Death\'s Dance', 'Sterak\'s Gage', 'Black Cleaver'],
        lategame: ['Guardian Angel', 'Force of Nature', 'Gargoyle Stoneplate'],
        priority: { damage: 0.5, survivability: 0.4, utility: 0.1 }
      },
      'Top': {
        mythic: ['Divine Sunderer', 'Goredrinker', 'Stridebreaker'],
        core: ['Sterak\'s Gage', 'Death\'s Dance', 'Black Cleaver'],
        lategame: ['Guardian Angel', 'Thornmail', 'Spirit Visage'],
        priority: { survivability: 0.5, damage: 0.4, utility: 0.1 }
      }
    };
  }

  initializeSynergies() {
    return {
      'critChance': {
        items: ['Infinity Edge', 'Phantom Dancer', 'Rapid Firecannon'],
        bonus: 'Critical strike chance synergy increases damage exponentially',
        threshold: 60,
        multiplier: 1.4
      },
      'magicPen': {
        items: ['Void Staff', 'Shadowflame', 'Sorcerer\'s Shoes'],
        bonus: 'Magic penetration stacks multiplicatively for tank-busting',
        threshold: 30,
        multiplier: 1.3
      },
      'healing': {
        items: ['Bloodthirster', 'Spirit Visage', 'Redemption'],
        bonus: 'Healing amplification creates sustain synergy',
        threshold: 25,
        multiplier: 1.25
      },
      'mobility': {
        items: ['Phantom Dancer', 'Youmuu\'s Ghostblade', 'Mobility Boots'],
        bonus: 'Movement speed stacking for superior positioning',
        threshold: 15,
        multiplier: 1.2
      },
      'armorPen': {
        items: ['Black Cleaver', 'Lord Dominik\'s Regards', 'Serylda\'s Grudge'],
        bonus: 'Armor penetration stacking melts tanks',
        threshold: 35,
        multiplier: 1.35
      }
    };
  }

  initializeCounterItems() {
    return {
      'highAP': {
        items: ['Spirit Visage', 'Banshee\'s Veil', 'Mercury\'s Treads', 'Maw of Malmortius'],
        effectiveness: 0.85,
        priority: 'high'
      },
      'highAD': {
        items: ['Thornmail', 'Plated Steelcaps', 'Guardian Angel', 'Death\'s Dance'],
        effectiveness: 0.82,
        priority: 'high'
      },
      'healing': {
        items: ['Morellonomicon', 'Thornmail', 'Chempunk Chainsword'],
        effectiveness: 0.90,
        priority: 'critical'
      },
      'shields': {
        items: ['Serpent\'s Fang'],
        effectiveness: 0.75,
        priority: 'situational'
      },
      'tanks': {
        items: ['Void Staff', 'Lord Dominik\'s Regards', 'Black Cleaver', 'Serylda\'s Grudge'],
        effectiveness: 0.88,
        priority: 'high'
      },
      'mobility': {
        items: ['Rylai\'s Crystal Scepter', 'Randuin\'s Omen', 'Frozen Heart'],
        effectiveness: 0.70,
        priority: 'medium'
      }
    };
  }

  initializeAdaptiveRecommendations() {
    return {
      'earlyLead': {
        focus: 'damage',
        items: ['Serrated Dirk', 'Blasting Wand', 'B.F. Sword'],
        reasoning: 'Snowball your advantage with damage items'
      },
      'behindInLane': {
        focus: 'survivability',
        items: ['Cloth Armor', 'Null-Magic Mantle', 'Doran\'s Shield'],
        reasoning: 'Play defensively and farm safely'
      },
      'teamFightPhase': {
        focus: 'utility',
        items: ['Stopwatch', 'Control Ward', 'Elixir of Wrath'],
        reasoning: 'Prepare for team objectives'
      },
      'splitPushPhase': {
        focus: 'mobility',
        items: ['Boots of Swiftness', 'Phantom Dancer', 'Youmuu\'s Ghostblade'],
        reasoning: 'Enhanced mobility for split pushing'
      }
    };
  }

  async loadItemData() {
    if (this.itemData) return this.itemData;
    
    try {
      const response = await fetch(`${this.baseUrl}/15.18.1/data/en_US/item.json`);
      if (!response.ok) throw new Error('Failed to load item data');
      this.itemData = await response.json();
      return this.itemData;
    } catch (error) {
      console.error('Error loading item data:', error);
      this.itemData = { data: {} };
      return this.itemData;
    }
  }

  detectChampionRole(champion) {
    const roleMapping = {
      'Marksman': 'ADC',
      'Mage': 'Mid',
      'Tank': 'Support',
      'Support': 'Support',
      'Fighter': 'Top',
      'Assassin': 'Mid'
    };

    if (champion.tags && champion.tags.length > 0) {
      return roleMapping[champion.tags[0]] || 'Mid';
    }
    return 'Mid';
  }

  getItemCategoriesForChampion(champion, role = null) {
    const detectedRole = role || this.detectChampionRole(champion);
    const tags = champion.tags || [];
    
    return {
      role: detectedRole,
      primaryTag: tags[0] || 'Mage',
      secondaryTag: tags[1] || null,
      damageType: this.getDamageType(champion),
      playstyle: this.getPlaystyle(champion),
      scalingType: this.getScalingType(champion)
    };
  }

  getDamageType(champion) {
    const tags = champion.tags || [];
    if (tags.includes('Marksman') || tags.includes('Fighter')) return 'AD';
    if (tags.includes('Mage') || tags.includes('Support')) return 'AP';
    if (tags.includes('Assassin')) return 'Mixed';
    return 'AD';
  }

  getPlaystyle(champion) {
    const tags = champion.tags || [];
    if (tags.includes('Assassin')) return 'Burst';
    if (tags.includes('Marksman')) return 'DPS';
    if (tags.includes('Tank')) return 'Engage';
    if (tags.includes('Support')) return 'Utility';
    if (tags.includes('Fighter')) return 'Bruiser';
    return 'Balanced';
  }

  getScalingType(champion) {
    const tags = champion.tags || [];
    if (tags.includes('Marksman')) return 'Late';
    if (tags.includes('Assassin')) return 'Mid';
    if (tags.includes('Support')) return 'Utility';
    return 'Balanced';
  }

  // Enhanced AI-driven recommendations
  async getIntelligentBuildRecommendations(champion, gameContext = {}) {
    try {
      await this.loadItemData();
      
      const {
        gameMode = 'ranked',
        role = 'default',
        gameLength = 'normal',
        enemyTeam = [],
        allyTeam = [],
        gameState = 'even',
        playerSkill = 'average'
      } = gameContext;

      const championRole = role !== 'default' ? role : this.detectChampionRole(champion);
      const categories = this.getItemCategoriesForChampion(champion, championRole);
      
      // Get base recommendations
      const proData = this.proBuilds[champion.name] || null;
      const metaItems = this.metaItems[championRole] || {};
      
      // Apply AI adaptations
      const adaptations = this.getGameStateAdaptations(gameState, gameLength, categories);
      const counterAdaptations = this.getCounterAdaptations(enemyTeam, categories);
      const synergyOptimizations = this.getSynergyOptimizations(allyTeam, categories);

      return {
        champion: champion.name,
        role: championRole,
        confidence: this.calculateConfidence(proData, categories, gameContext),
        
        // Core build structure
        starter: this.getAdaptiveStarterItems(champion, categories, gameState),
        core: this.getOptimizedCoreItems(champion, categories, proData, metaItems, adaptations),
        boots: this.getSmartBootOptions(champion, categories, enemyTeam),
        situational: this.getContextualSituationalItems(champion, categories, gameContext),
        lateGame: this.getScaledLateGameItems(champion, categories, metaItems, gameLength),
        
        // Advanced features
        buildPath: this.generateAdaptiveBuildPath(champion, categories, gameContext),
        counterStrategy: this.getAdvancedCounterStrategy(champion, enemyTeam, categories),
        teamSynergy: synergyOptimizations,
        
        // Meta information
        meta: {
          winRate: this.calculateContextualWinRate(proData, gameContext),
          pickRate: proData?.pickRate || 0.05,
          tier: this.getContextualTier(champion, categories, gameContext),
          matchupStrength: this.getMatchupStrength(champion, enemyTeam),
          scalingCurve: this.getScalingCurve(categories, gameLength)
        },

        // AI insights
        insights: {
          keyPowerSpikes: this.getKeyPowerSpikes(categories, proData),
          playStyleTips: this.getPlayStyleTips(categories, gameContext),
          itemPriority: this.getItemPriority(categories, gameContext),
          adaptationTriggers: this.getAdaptationTriggers(categories)
        },

        // Performance tracking
        analytics: {
          buildOptimization: this.getBuildOptimizationScore(categories, adaptations),
          expectedPerformance: this.getExpectedPerformance(champion, categories, gameContext),
          riskFactors: this.getRiskFactors(categories, enemyTeam)
        }
      };
    } catch (error) {
      console.error('Error getting intelligent recommendations:', error);
      return this.getFallbackBuild(champion);
    }
  }

  getGameStateAdaptations(gameState, gameLength, categories) {
    const adaptations = {
      'ahead': {
        focus: 'damage',
        priority: ['snowball', 'aggressive'],
        modifier: 1.2
      },
      'behind': {
        focus: 'survivability',
        priority: ['defensive', 'scaling'],
        modifier: 0.8
      },
      'even': {
        focus: 'balanced',
        priority: ['meta', 'standard'],
        modifier: 1.0
      }
    };

    return adaptations[gameState] || adaptations['even'];
  }

  getCounterAdaptations(enemyTeam, categories) {
    const threats = this.analyzeThreatLevel(enemyTeam);
    const adaptations = [];

    if (threats.ap > 0.6) {
      adaptations.push({
        type: 'antiAP',
        priority: 'high',
        items: this.counterItems.highAP.items,
        reasoning: 'High AP threat detected'
      });
    }

    if (threats.ad > 0.6) {
      adaptations.push({
        type: 'antiAD',
        priority: 'high',
        items: this.counterItems.highAD.items,
        reasoning: 'High AD threat detected'
      });
    }

    if (threats.healing > 0.4) {
      adaptations.push({
        type: 'antiHeal',
        priority: 'critical',
        items: this.counterItems.healing.items,
        reasoning: 'Significant healing sources detected'
      });
    }

    return adaptations;
  }

  analyzeThreatLevel(enemyTeam) {
    // Simplified threat analysis - would be enhanced with real champion data
    return {
      ap: Math.random() * 0.8 + 0.2, // Placeholder
      ad: Math.random() * 0.8 + 0.2,
      healing: Math.random() * 0.6 + 0.1,
      mobility: Math.random() * 0.7 + 0.2,
      tank: Math.random() * 0.5 + 0.1
    };
  }

  getSynergyOptimizations(allyTeam, categories) {
    return {
      teamComposition: this.analyzeTeamComposition(allyTeam),
      synergyItems: this.getTeamSynergyItems(allyTeam, categories),
      supportItems: this.getSupportSynergyItems(categories)
    };
  }

  analyzeTeamComposition(allyTeam) {
    // Placeholder for team composition analysis
    return {
      engage: 0.6,
      poke: 0.4,
      sustain: 0.3,
      burst: 0.7
    };
  }

  getTeamSynergyItems(allyTeam, categories) {
    const synergyItems = [];
    
    if (categories.role === 'Support') {
      synergyItems.push({
        item: 'Knight\'s Vow',
        target: 'ADC',
        reasoning: 'Protect primary carry'
      });
    }

    return synergyItems;
  }

  getAdaptiveStarterItems(champion, categories, gameState) {
    const baseStarters = this.getStarterItems(champion, categories);
    
    if (gameState === 'defensive') {
      // Add defensive options
      if (categories.damageType === 'AD') {
        return [...baseStarters, 'Cloth Armor'];
      } else {
        return [...baseStarters, 'Null-Magic Mantle'];
      }
    }

    return baseStarters;
  }

  getStarterItems(champion, categories) {
    const starters = {
      'ADC': ["Doran's Blade", "Health Potion"],
      'Mid': ["Doran's Ring", "Health Potion", "Health Potion"],
      'Support': ["Relic Shield", "Health Potion", "Stealth Ward"],
      'Top': ["Doran's Blade", "Health Potion"],
      'Jungle': ["Hailblade", "Refillable Potion"]
    };

    return starters[categories.role] || starters['Mid'];
  }

  getOptimizedCoreItems(champion, categories, proData, metaItems, adaptations) {
    let coreItems = [];
    let source = 'Standard Build';
    let confidence = 0.6;

    // Prioritize pro build if available and reliable
    if (proData && proData.winRate > 0.6) {
      coreItems = [...proData.core];
      source = 'Pro Build';
      confidence = 0.9;
    } else if (metaItems.mythic && metaItems.core) {
      // Use meta items
      coreItems = [...metaItems.mythic.slice(0, 1), ...metaItems.core.slice(0, 2)];
      source = 'Current Meta';
      confidence = 0.75;
    } else {
      // Fallback to role-based build
      coreItems = this.getFallbackCoreItems(categories).items;
    }

    // Apply adaptations
    if (adaptations.focus === 'survivability') {
      coreItems = this.addSurvivabilityItems(coreItems, categories);
    } else if (adaptations.focus === 'damage') {
      coreItems = this.optimizeForDamage(coreItems, categories);
    }

    return {
      items: coreItems,
      source,
      confidence,
      adaptations: adaptations.priority
    };
  }

  addSurvivabilityItems(coreItems, categories) {
    const survivabilityMap = {
      'ADC': ['Guardian Angel', 'Immortal Shieldbow'],
      'Mid': ['Zhonya\'s Hourglass', 'Banshee\'s Veil'],
      'Support': ['Locket of the Iron Solari', 'Knight\'s Vow']
    };

    const survivalItems = survivabilityMap[categories.role] || [];
    return [...coreItems.slice(0, 2), ...survivalItems.slice(0, 1)];
  }

  optimizeForDamage(coreItems, categories) {
    const damageMap = {
      'ADC': ['Infinity Edge', 'Lord Dominik\'s Regards'],
      'Mid': ['Rabadon\'s Deathcap', 'Void Staff'],
      'Support': ['Imperial Mandate', 'Staff of Flowing Water']
    };

    const damageItems = damageMap[categories.role] || [];
    return [...coreItems, ...damageItems.slice(0, 1)];
  }

  getFallbackCoreItems(categories) {
    const builds = {
      'ADC': {
        items: ['Kraken Slayer', 'Phantom Dancer', 'Infinity Edge'],
        source: 'Standard ADC Build',
        confidence: 0.6
      },
      'Mid': {
        items: ["Luden's Tempest", 'Shadowflame', "Zhonya's Hourglass"],
        source: 'Standard Mage Build',
        confidence: 0.6
      },
      'Support': {
        items: ['Locket of the Iron Solari', "Knight's Vow", 'Redemption'],
        source: 'Standard Support Build',
        confidence: 0.6
      }
    };

    return builds[categories.role] || builds['Mid'];
  }

  getSmartBootOptions(champion, categories, enemyTeam) {
    const threats = this.analyzeThreatLevel(enemyTeam);
    
    const bootsByRole = {
      'ADC': {
        primary: "Berserker's Greaves",
        alternatives: [],
        reasoning: "Attack speed for DPS optimization"
      },
      'Mid': {
        primary: "Sorcerer's Shoes",
        alternatives: [],
        reasoning: "Magic penetration for damage output"
      },
      'Support': {
        primary: "Mobility Boots",
        alternatives: [],
        reasoning: "Roaming and vision control"
      }
    };

    const roleBoots = bootsByRole[categories.role] || bootsByRole['Mid'];

    // Add threat-based alternatives
    if (threats.ap > 0.7) {
      roleBoots.alternatives.push("Mercury's Treads");
    }
    if (threats.ad > 0.7) {
      roleBoots.alternatives.push("Plated Steelcaps");
    }

    return roleBoots;
  }

  getContextualSituationalItems(champion, categories, gameContext) {
    const base = this.getSituationalItems(champion, categories, gameContext.gameMode);
    
    // Add context-specific items
    if (gameContext.gameLength === 'long') {
      base.scaling = this.getLongGameItems(categories);
    }
    
    if (gameContext.gameState === 'behind') {
      base.comeback = this.getComebackItems(categories);
    }

    return base;
  }

  getSituationalItems(champion, categories, gameMode) {
    const situationalByRole = {
      'ADC': {
        antiTank: ["Lord Dominik's Regards", "Mortal Reminder"],
        survivability: ["Guardian Angel", "Mercurial Scimitar", "Bloodthirster"],
        utility: ["Runaan's Hurricane", "Rapid Firecannon"]
      },
      'Mid': {
        antiTank: ["Void Staff", "Shadowflame"],
        survivability: ["Zhonya's Hourglass", "Banshee's Veil"],
        utility: ["Cosmic Drive", "Horizon Focus"]
      },
      'Support': {
        engage: ["Zeke's Convergence", "Shurelya's Battlesong"],
        protection: ["Mikael's Blessing", "Knight's Vow"],
        vision: ["Wardstone", "Umbral Glaive"]
      }
    };

    return situationalByRole[categories.role] || situationalByRole['Mid'];
  }

  getLongGameItems(categories) {
    const longGameMap = {
      'ADC': ['Bloodthirster', 'Mercurial Scimitar'],
      'Mid': ['Rabadon\'s Deathcap', 'Cosmic Drive'],
      'Support': ['Wardstone', 'Redemption']
    };

    return longGameMap[categories.role] || [];
  }

  getComebackItems(categories) {
    const comebackMap = {
      'ADC': ['Guardian Angel', 'Immortal Shieldbow'],
      'Mid': ['Zhonya\'s Hourglass', 'Crown of the Shattered Queen'],
      'Support': ['Locket of the Iron Solari', 'Knight\'s Vow']
    };

    return comebackMap[categories.role] || [];
  }

  calculateConfidence(proData, categories, gameContext) {
    let confidence = 0.5; // Base confidence

    if (proData) {
      confidence += proData.winRate * 0.3;
      confidence += Math.min(proData.pickRate * 2, 0.2);
    }

    // Adjust for game context
    if (gameContext.playerSkill === 'high') {
      confidence += 0.1;
    }

    return Math.min(confidence, 0.95);
  }

  calculateContextualWinRate(proData, gameContext) {
    const baseWinRate = proData?.winRate || 0.6;
    
    // Adjust based on game context
    let adjustment = 0;
    
    if (gameContext.gameState === 'ahead') {
      adjustment += 0.05;
    } else if (gameContext.gameState === 'behind') {
      adjustment -= 0.05;
    }

    return Math.max(0.4, Math.min(0.8, baseWinRate + adjustment));
  }

  getContextualTier(champion, categories, gameContext) {
    // Simplified tier calculation
    const proData = this.proBuilds[champion.name];
    if (!proData) return 'B';
    
    const score = (proData.winRate * 0.7) + (proData.pickRate * 0.3);
    
    if (score >= 0.65) return 'S';
    if (score >= 0.55) return 'A';
    if (score >= 0.45) return 'B';
    if (score >= 0.35) return 'C';
    return 'D';
  }

  getMatchupStrength(champion, enemyTeam) {
    // Placeholder for matchup analysis
    return {
      favorable: Math.random() * 0.4 + 0.3,
      skill: Math.random() * 0.6 + 0.2,
      unfavorable: Math.random() * 0.3 + 0.1
    };
  }

  getScalingCurve(categories, gameLength) {
    const curves = {
      'Early': { early: 0.8, mid: 0.6, late: 0.4 },
      'Mid': { early: 0.5, mid: 0.8, late: 0.7 },
      'Late': { early: 0.3, mid: 0.6, late: 0.9 },
      'Balanced': { early: 0.6, mid: 0.7, late: 0.6 }
    };

    return curves[categories.scalingType] || curves['Balanced'];
  }

  getKeyPowerSpikes(categories, proData) {
    const spikes = [];
    
    if (proData && proData.core) {
      spikes.push({
        item: proData.core[0],
        timing: 'First item completion',
        impact: 'Major power spike'
      });
      
      if (proData.core[1]) {
        spikes.push({
          item: proData.core[1],
          timing: 'Two item completion',
          impact: 'Team fight ready'
        });
      }
    }

    return spikes;
  }

  getPlayStyleTips(categories, gameContext) {
    const tips = [];
    
    tips.push(`Play ${categories.playstyle} style with focus on ${categories.damageType} damage`);
    
    if (gameContext.gameState === 'behind') {
      tips.push('Focus on farming and avoid risky plays');
    } else if (gameContext.gameState === 'ahead') {
      tips.push('Press your advantage and look for picks');
    }

    return tips;
  }

  getItemPriority(categories, gameContext) {
    const metaItems = this.metaItems[categories.role] || {};
    const priority = metaItems.priority || { damage: 0.5, survivability: 0.3, utility: 0.2 };

    // Adjust based on game state
    if (gameContext.gameState === 'behind') {
      priority.survivability += 0.2;
      priority.damage -= 0.1;
    } else if (gameContext.gameState === 'ahead') {
      priority.damage += 0.2;
      priority.survivability -= 0.1;
    }

    return priority;
  }

  getAdaptationTriggers(categories) {
    return [
      'Enemy team has high burst damage',
      'Team needs more engage potential',
      'Multiple healing sources on enemy team',
      'Enemy team is very mobile'
    ];
  }

  getFallbackBuild(champion) {
    return {
      champion: champion.name || 'Unknown',
      role: 'Mid',
      confidence: 0.4,
      starter: ["Doran's Ring", "Health Potion"],
      core: {
        items: ["Luden's Tempest", 'Shadowflame', "Zhonya's Hourglass"],
        source: 'Fallback Build',
        confidence: 0.4
      },
      boots: {
        primary: "Sorcerer's Shoes",
        alternatives: ["Ionian Boots of Lucidity"],
        reasoning: 'Standard mage boots'
      },
      situational: {
        survival: ["Banshee's Veil", "Zhonya's Hourglass"],
        damage: ["Rabadon's Deathcap", "Void Staff"]
      },
      insights: {
        keyPowerSpikes: [],
        playStyleTips: ['This is a generic build - check champion-specific guides'],
        itemPriority: { damage: 0.5, survivability: 0.3, utility: 0.2 }
      },
      meta: {
        winRate: 0.50,
        pickRate: 0.05,
        tier: 'C'
      }
    };
  }
}

export default EnhancedDynamicItemService;