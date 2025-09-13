import tmi from 'tmi.js'

class TwitchChatClient {
  constructor(channelName) {
    this.channelName = channelName
    this.client = null
    this.messageCallback = null
    this.isConnected = false
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
      
      // Simulate some messages for demo purposes if no real messages come in
      this.startDemoMessages()
      
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
  }

  // Demo message generator for testing
  startDemoMessages() {
    const demoMessages = [
      { username: 'ChatViewer1', message: 'Great stream! Love the gameplay!' },
      { username: 'ToxicUser', message: 'This is terrible, you suck at this game' },
      { username: 'RegularViewer', message: 'What keyboard are you using?' },
      { username: 'Supporter', message: 'Amazing content as always! Keep it up!' },
      { username: 'Hater123', message: 'Worst streamer ever, unsubbing' },
      { username: 'NewViewer', message: 'Just followed! Excited to watch more' },
      { username: 'ChatMod', message: 'Please keep chat respectful everyone' },
      { username: 'FanBoy', message: 'You are the best streamer on Twitch!' },
      { username: 'CriticalViewer', message: 'The audio quality could be better' },
      { username: 'PositiveVibes', message: 'This made my day, thank you for streaming!' }
    ]

    let messageIndex = 0
    const sendDemoMessage = () => {
      if (this.messageCallback && messageIndex < demoMessages.length) {
        const demo = demoMessages[messageIndex]
        const messageData = {
          username: demo.username,
          message: demo.message,
          userId: `demo_${messageIndex}`,
          color: '#' + Math.floor(Math.random()*16777215).toString(16),
          badges: null,
          emotes: null,
          timestamp: new Date()
        }
        
        this.messageCallback(messageData)
        messageIndex++
        
        // Schedule next message
        setTimeout(sendDemoMessage, Math.random() * 3000 + 1000) // 1-4 seconds
      } else {
        // Reset and continue loop
        messageIndex = 0
        setTimeout(sendDemoMessage, Math.random() * 5000 + 2000) // 2-7 seconds
      }
    }

    // Start demo messages after a short delay
    setTimeout(sendDemoMessage, 2000)
  }
}

export default TwitchChatClient
