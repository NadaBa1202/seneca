import { useState } from 'react'
import './LandingPage.css'

const LandingPage = ({ onChannelConnect }) => {
  const [channelInput, setChannelInput] = useState('')
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState('')

  const extractChannelName = (input) => {
    // Handle various Twitch URL formats
    if (input.includes('twitch.tv/')) {
      const match = input.match(/twitch\.tv\/([^/?]+)/)
      return match ? match[1] : null
    }
    // If it's just a channel name
    return input.trim()
  }

  const handleConnect = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!channelInput.trim()) {
      setError('Please enter a Twitch channel name or URL')
      return
    }

    const channelName = extractChannelName(channelInput)
    
    if (!channelName) {
      setError('Invalid Twitch channel URL or name')
      return
    }

    setIsConnecting(true)
    
    try {
      // Simulate connection validation
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      onChannelConnect({
        name: channelName,
        url: `https://twitch.tv/${channelName}`,
        connectedAt: new Date()
      })
    } catch (err) {
      setError('Failed to connect to channel. Please check the channel name.')
    } finally {
      setIsConnecting(false)
    }
  }

  return (
    <div className="landing-page">
      <div className="landing-container">
        <header className="landing-header">
          <div className="logo">
            {/*/<span className="logo-icon"></span>*/}
            <h1>Chat.GG</h1>
          </div>
          <p className="tagline">Monitor and analyze your Twitch chat in real-time</p>
        </header>

        <div className="features-grid">
          <div className="feature-card">
            <h3>Real-time Chat Monitoring</h3>
            <p>Connect to any Twitch channel and monitor chat messages as they happen</p>
          </div>
          <div className="feature-card">
            <h3>Sentiment Analysis</h3>
            <p>Automatically classify messages as positive, neutral, or toxic</p>
          </div>
          <div className="feature-card">
            <h3>Live Statistics</h3>
            <p>View real-time charts and analytics of your chat engagement</p>
          </div>
        </div>
        <div className="info-section">
          <h3>How it works</h3>
          <div className="steps">
            <div className="step">
              <span className="step-number">1</span>
              <p>Enter a Twitch channel name or URL</p>
            </div>
            <div className="step">
              <span className="step-number">2</span>
              <p>We connect to the live chat stream</p>
            </div>
            <div className="step">
              <span className="step-number">3</span>
              <p>View real-time analytics and sentiment analysis</p>
            </div>
          </div>
        </div>
        <div className="connect-section">
          <h2>Connect to a Twitch Channel</h2>
          <form onSubmit={handleConnect} className="connect-form">
            <div className="input-group">
              <input
                type="text"
                placeholder="Enter Twitch channel name or URL (e.g., 'ninja' or 'https://twitch.tv/ninja')"
                value={channelInput}
                onChange={(e) => setChannelInput(e.target.value)}
                className="channel-input"
                disabled={isConnecting}
              />
              <button 
                type="submit" 
                className="connect-button"
                disabled={isConnecting}
              >
                {isConnecting ? (
                  <>
                    <span className="spinner"></span>
                    Connecting...
                  </>
                ) : (
                  'Start Monitoring'
                )}
              </button>
            </div>
            {error && <div className="error-message">{error}</div>}
          </form>
        </div>

        
      </div>
    </div>
  )
}

export default LandingPage
