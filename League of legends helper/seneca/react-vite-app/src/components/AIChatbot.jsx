import React, { useState, useRef, useEffect } from 'react';
import './AIChatbot.css';

const AIChatbot = ({ champion, onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: `Hello! I'm your League of Legends AI assistant. I can help you with questions about ${champion?.name || 'any champion'}, builds, strategies, and gameplay tips. What would you like to know?`,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Enhanced League of Legends knowledge base
  const leagueKnowledge = {
    champions: {
      'jinx': {
        role: 'ADC',
        difficulty: 'Medium',
        tips: [
          'Focus on positioning - Jinx is very immobile',
          'Use Switcheroo! to toggle between rocket and minigun',
          'Save your Flash for escapes, not engages',
          'Build crit items for late game scaling'
        ],
        counters: ['Zed', 'Yasuo', 'Fizz'],
        synergies: ['Thresh', 'Lulu', 'Braum']
      },
      'ahri': {
        role: 'Mid',
        difficulty: 'Medium',
        tips: [
          'Use Spirit Rush to reposition in fights',
          'Land Charm for guaranteed kill combos',
          'Roam after pushing waves',
          'Build magic penetration against tanks'
        ],
        counters: ['Yasuo', 'Fizz', 'Zed'],
        synergies: ['Jarvan IV', 'Sejuani', 'Amumu']
      },
      'thresh': {
        role: 'Support',
        difficulty: 'High',
        tips: [
          'Land hooks to engage fights',
          'Use lantern to save teammates',
          'Collect souls to scale',
          'Ward bushes for hook opportunities'
        ],
        counters: ['Morgana', 'Sivir', 'Ezreal'],
        synergies: ['Jinx', 'Caitlyn', 'Ashe']
      }
    },
    items: {
      'kraken slayer': {
        role: ['ADC'],
        description: 'Mythic item providing true damage',
        when: 'Against tanky teams or for raw DPS',
        synergy: ['Phantom Dancer', 'Infinity Edge']
      },
      'ludens tempest': {
        role: ['Mid'],
        description: 'Mythic item for burst mages',
        when: 'For waveclear and poke damage',
        synergy: ['Shadowflame', 'Horizon Focus']
      }
    },
    strategies: {
      'laning': [
        'Farm consistently - aim for 6-8 CS per minute',
        'Trade when enemy abilities are on cooldown',
        'Ward river bush to avoid ganks',
        'Control minion waves to your advantage'
      ],
      'teamfighting': [
        'Position safely in the backline',
        'Focus the closest target you can safely hit',
        'Save defensive abilities for assassins',
        'Follow up on team engage'
      ]
    }
  };

  const generateResponse = (userMessage) => {
    const message = userMessage.toLowerCase();
    
    // Champion-specific responses
    if (champion && message.includes(champion.name.toLowerCase())) {
      const champData = leagueKnowledge.champions[champion.name.toLowerCase()];
      if (champData) {
        if (message.includes('tip') || message.includes('how')) {
          return `Here are some tips for ${champion.name}:\n\n${champData.tips.map(tip => `• ${tip}`).join('\n')}\n\nRole: ${champData.role} | Difficulty: ${champData.difficulty}`;
        }
        if (message.includes('counter') || message.includes('against')) {
          return `${champion.name} struggles against: ${champData.counters.join(', ')}\n\nTip: Play safe and farm when facing these champions. Wait for jungle help or team fights.`;
        }
        if (message.includes('synergy') || message.includes('with')) {
          return `${champion.name} works well with: ${champData.synergies.join(', ')}\n\nThese champions complement ${champion.name}'s playstyle and can set up plays together.`;
        }
      }
    }

    // Item-related responses
    if (message.includes('item') || message.includes('build')) {
      if (message.includes('kraken') || message.includes('adc')) {
        return 'For ADC builds, I recommend:\n\n• **Kraken Slayer** - Best for DPS and tank killing\n• **Galeforce** - For mobility and outplay potential\n• **Immortal Shieldbow** - Against burst damage\n\nFollow up with crit items like Phantom Dancer and Infinity Edge.';
      }
      if (message.includes('mage') || message.includes('ap')) {
        return 'For Mage builds, consider:\n\n• **Luden\'s Tempest** - Burst and waveclear\n• **Liandry\'s Anguish** - Against tanky teams\n• **Everfrost** - For utility and CC\n\nCore items: Shadowflame, Zhonya\'s Hourglass, Void Staff';
      }
      return 'I can help with builds! What role or champion are you building for? I have recommendations for ADC, Mid, Support, and other roles.';
    }

    // Strategy responses
    if (message.includes('lane') || message.includes('farm')) {
      return 'Laning tips:\n\n' + leagueKnowledge.strategies.laning.map(tip => `• ${tip}`).join('\n') + '\n\nRemember: CSing is more important than trading in most cases!';
    }

    if (message.includes('team') || message.includes('fight')) {
      return 'Team fighting tips:\n\n' + leagueKnowledge.strategies.teamfighting.map(tip => `• ${tip}`).join('\n') + '\n\nStay alive and deal consistent damage!';
    }

    // Role-specific advice
    if (message.includes('adc')) {
      return 'ADC tips:\n\n• Position safely behind your team\n• Focus on farming early game\n• Build crit items for late game scaling\n• Kite backwards while dealing damage\n• Let your support engage first';
    }

    if (message.includes('support')) {
      return 'Support tips:\n\n• Ward key areas for vision control\n• Protect your ADC in lane\n• Roam when your ADC is safe\n• Buy control wards every back\n• Engage when your team is ready';
    }

    if (message.includes('mid')) {
      return 'Mid lane tips:\n\n• Control the river with wards\n• Roam to help other lanes\n• Farm efficiently and trade smartly\n• Take Teleport for map presence\n• Focus on scaling and team fights';
    }

    // Meta questions
    if (message.includes('meta') || message.includes('strong')) {
      return 'Current meta champions by role:\n\n• **ADC**: Jinx, Caitlyn, Ashe\n• **Mid**: Ahri, Yasuo, Syndra\n• **Support**: Thresh, Lux, Nautilus\n• **Jungle**: Graves, Lee Sin, Elise\n• **Top**: Garen, Darius, Fiora\n\nRemember: Skill matters more than meta!';
    }

    // Runes questions
    if (message.includes('rune') || message.includes('keystone')) {
      return 'Popular keystones by role:\n\n• **ADC**: Lethal Tempo, Fleet Footwork\n• **Mage**: Electrocute, Comet, Phase Rush\n• **Support**: Aftershock, Guardian, Electrocute\n• **Assassin**: Electrocute, Conqueror\n• **Tank**: Aftershock, Grasp\n\nChoose based on your champion and playstyle!';
    }

    // General help responses
    if (message.includes('help') || message.includes('what')) {
      return 'I can help you with:\n\n• **Champion guides** - Tips, counters, synergies\n• **Item builds** - Core items, situational builds\n• **Strategies** - Laning, team fighting, macro play\n• **Meta advice** - Current strong picks\n• **Runes** - Keystone recommendations\n\nJust ask me anything about League of Legends!';
    }

    // Default responses
    const defaultResponses = [
      'That\'s an interesting question! Could you be more specific about what aspect of League you\'d like help with?',
      'I\'d love to help! Are you asking about a specific champion, item build, or strategy?',
      'Let me help you with that! Could you clarify if you\'re looking for champion tips, build advice, or gameplay strategies?',
      'Great question! I have knowledge about champions, items, strategies, and the current meta. What would you like to know more about?'
    ];

    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI thinking time
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

    const botResponse = {
      id: Date.now() + 1,
      type: 'bot',
      content: generateResponse(inputMessage),
      timestamp: new Date()
    };

    setIsTyping(false);
    setMessages(prev => [...prev, botResponse]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .split('\n')
      .map((line, index) => {
        if (line.startsWith('• ')) {
          return <li key={index} className="message-list-item">{line.substring(2)}</li>;
        }
        if (line.includes('**') && line.includes('**')) {
          const parts = line.split('**');
          return (
            <p key={index} className="message-paragraph">
              {parts.map((part, i) => 
                i % 2 === 1 ? <strong key={i}>{part}</strong> : part
              )}
            </p>
          );
        }
        return line ? <p key={index} className="message-paragraph">{line}</p> : <br key={index} />;
      });
  };

  return (
    <div className="ai-chatbot">
      <div className="chatbot-header">
        <div className="chatbot-title">
          <div className="ai-avatar">🤖</div>
          <div>
            <h3>League AI Assistant</h3>
            <span className="status-indicator">● Online</span>
          </div>
        </div>
        <button onClick={onClose} className="close-button">×</button>
      </div>

      <div className="chatbot-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-avatar">
              {message.type === 'bot' ? '🤖' : '👤'}
            </div>
            <div className="message-content">
              <div className="message-text">
                {formatMessage(message.content)}
              </div>
              <div className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message bot">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chatbot-input">
        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about League champions, builds, strategies..."
            className="message-input"
            rows="1"
          />
          <button 
            onClick={handleSendMessage}
            disabled={!inputMessage.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
        <div className="quick-questions">
          <button 
            onClick={() => setInputMessage('What are some tips for ' + (champion?.name || 'playing ADC') + '?')}
            className="quick-question"
          >
            Champion Tips
          </button>
          <button 
            onClick={() => setInputMessage('What items should I build?')}
            className="quick-question"
          >
            Item Builds
          </button>
          <button 
            onClick={() => setInputMessage('How do I team fight better?')}
            className="quick-question"
          >
            Team Fighting
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChatbot;