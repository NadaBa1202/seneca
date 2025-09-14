import tmi from 'tmi.js'

class TwitchChatClient {
  constructor(channelName) {
    this.channelName = channelName
    this.client = null
    this.messageCallback = null
    this.isConnected = false
    this.demoRunning = false
    this.demoInterval = null
  }

  async connect() {
    try {
      this.client = new tmi.Client({
        options: { debug: false },
        connection: {
          reconnect: true,
          secure: true
        },
        channels: [this.channelName]
      })

      this.client.on('message', (channel, tags, message, self) => {
        if (self) return // Ignore messages from the bot itself

        const messageData = {
          username: tags['display-name'] || tags.username,
          message: message,
          userId: tags['user-id'],
          color: tags.color,
          badges: tags.badges,
          emotes: tags.emotes,
          timestamp: new Date(parseInt(tags['tmi-sent-ts']))
        }

        if (this.messageCallback) {
          this.messageCallback(messageData)
        }
      })

      this.client.on('connected', () => {
        this.isConnected = true
        console.log(`Connected to ${this.channelName}'s chat`)
      })

      this.client.on('disconnected', () => {
        this.isConnected = false
        console.log('Disconnected from chat')
      })

      await this.client.connect()
      
      // Don't auto-start demo messages - wait for manual trigger
      
    } catch (error) {
      console.error('Failed to connect to Twitch chat:', error)
      throw error
    }
  }

  onMessage(callback) {
    this.messageCallback = callback
  }

  disconnect() {
    if (this.client) {
      this.client.disconnect()
      this.isConnected = false
    }
    if (this.demoInterval) {
      clearTimeout(this.demoInterval)
      this.demoInterval = null
    }
  }

  // Demo message generator for testing
  startDemoMessages() {
    if (this.demoRunning) return // Already running

    this.demoRunning = true
    const demoMessages = [
      // Positive gaming messages
      { username: 'ProGamer2024', message: 'That combo was absolutely insane! You\'re a legend!' },
      { username: 'LeagueExpert', message: 'Perfect positioning in that teamfight, well played!' },
      { username: 'SupportMain', message: 'Your vision control is on point this game' },
      { username: 'RankClimber', message: 'Can you share your build path? Looking to improve my gameplay' },
      { username: 'ViewerFan', message: 'This is the best educational stream I\'ve watched!' },
      { username: 'ChatModerator', message: 'Great calls everyone, let\'s keep the positive energy!' },
      
      // Neutral/informational messages
      { username: 'NewViewer123', message: 'What rank are you currently? Just started watching' },
      { username: 'CasualPlayer', message: 'Which champion would you recommend for beginners?' },
      { username: 'RegularWatcher', message: 'What\'s your favorite role to play in ranked?' },
      { username: 'LearningJungle', message: 'Could you explain your jungle path for this game?' },
      { username: 'ChatHelper', message: 'For new viewers: streamer is currently Diamond 2' },
      
      // Slightly negative but constructive
      { username: 'CriticalViewer', message: 'You could have played that fight more defensively' },
      { username: 'AnalyticalFan', message: 'I think rushing that item might not be optimal here' },
      { username: 'HonestFeedback', message: 'Your macro play is good but mechanics need work' },
      
      // Toxic messages (realistic but mild for demo)
      { username: 'TrollUser42', message: 'This gameplay is trash, uninstall the game' },
      { username: 'FlameWarrior', message: 'Worst ADC I\'ve ever seen, you\'re hardstuck for a reason' },
      { username: 'ToxicViewer', message: 'Stop feeding and maybe you\'ll win a game' },
      
      // Enthusiastic gaming content
      { username: 'HypeViewer', message: 'POGGERS that outplay was incredible!!!' },
      { username: 'EmoteSpammer', message: 'Kappa Kappa Kappa that baron steal tho' },
      { username: 'SkillWatcher', message: 'Your Yasuo mechanics are getting so much better!' },
      { username: 'TeamFightFan', message: 'Late game teamfights are always so intense!' },
      { username: 'MetaDiscussion', message: 'What do you think about the new patch changes?' },
      
      // Engaging questions
      { username: 'InteractiveViewer', message: 'Should we group for dragon or split push?' },
      { username: 'StrategyFan', message: 'Why did you choose that rune setup for this matchup?' },
      { username: 'ItemBuildCurious', message: 'When do you build defensive items vs full damage?' }
    ]

    let messageIndex = 0
    const sendDemoMessage = () => {
      if (!this.demoRunning) return // Stop if demo was stopped

      if (this.messageCallback) {
        // Randomly select from different message types for variety
        const randomMessage = demoMessages[Math.floor(Math.random() * demoMessages.length)]
        const messageData = {
          username: randomMessage.username,
          message: randomMessage.message,
          userId: `demo_${messageIndex}`,
          color: '#' + Math.floor(Math.random()*16777215).toString(16),
          badges: Math.random() > 0.7 ? { subscriber: '1' } : null, // Some users have badges
          emotes: null,
          timestamp: new Date()
        }
        
        this.messageCallback(messageData)
        messageIndex++
        
        // Variable timing for more realistic chat flow
        let nextDelay
        if (Math.random() > 0.8) {
          // Burst of messages (teamfight moment)
          nextDelay = Math.random() * 500 + 300 // 300-800ms
        } else {
          // Normal chat flow
          nextDelay = Math.random() * 4000 + 1500 // 1.5-5.5 seconds
        }
        
        this.demoInterval = setTimeout(sendDemoMessage, nextDelay)
      }
    }

    // Start demo messages after a short delay
    console.log('Starting demo chat messages...')
    this.demoInterval = setTimeout(sendDemoMessage, 1000)
  }

  stopDemoMessages() {
    this.demoRunning = false
    if (this.demoInterval) {
      clearTimeout(this.demoInterval)
      this.demoInterval = null
    }
  }

  isDemoRunning() {
    return this.demoRunning
  }
}

export default TwitchChatClient
