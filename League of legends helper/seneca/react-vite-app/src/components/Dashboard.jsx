import { useState, useEffect, useRef } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import TwitchChatClient from '../services/TwitchChatClient'
import SentimentAnalyzer from '../services/CleanEnhancedSentimentAnalyzer'
import './Dashboard.css'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement)

const Dashboard = ({ channelData, onBack, onLeagueFeatures, onDataTest }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState([])
  const [stats, setStats] = useState({
    total: 0,
    positive: 0,
    neutral: 0,
    negative: 0,
    toxic: 0,
    messagesPerMinute: 0
  })
  const [recentMessages, setRecentMessages] = useState([])
  const [searchFilter, setSearchFilter] = useState('')
  const [sentimentFilter, setSentimentFilter] = useState('all')
  const [showModeration, setShowModeration] = useState(false)
  const [blockedUsers, setBlockedUsers] = useState(new Set())
  const [timelineData, setTimelineData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Positive',
        data: [],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.1
      },
      {
        label: 'Neutral',
        data: [],
        borderColor: '#6b7280',
        backgroundColor: 'rgba(107, 114, 128, 0.1)',
        tension: 0.1
      },
      {
        label: 'Negative',
        data: [],
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.1
      },
      {
        label: 'Toxic',
        data: [],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.1
      }
    ]
  })
  const [emotionData, setEmotionData] = useState({
    joy: 0, anger: 0, fear: 0, sadness: 0, surprise: 0, disgust: 0
  })
  const [demoRunning, setDemoRunning] = useState(false)
  const [advancedStats, setAdvancedStats] = useState({
    mostActiveUsers: new Map(),
    averageMessageLength: 0,
    peakActivity: { time: null, count: 0 },
    totalWords: 0,
    uniqueUsers: new Set(),
    topEmotions: [],
    sentimentTrend: 'stable' // 'improving', 'declining', 'stable'
  })
  const [sessionStartTime] = useState(new Date())
  const chatClientRef = useRef(null)
  const sentimentAnalyzer = useRef(new SentimentAnalyzer())

  useEffect(() => {
    connectToChat()
    return () => {
      if (chatClientRef.current) {
        chatClientRef.current.disconnect()
      }
    }
  }, [channelData])

  // Update average message length when stats change
  useEffect(() => {
    setAdvancedStats(prev => ({
      ...prev,
      averageMessageLength: prev.totalWords > 0 && stats.total > 0 ?
        Math.round(prev.totalWords / stats.total * 10) / 10 : 0
    }))
  }, [stats.total])

  const connectToChat = async () => {
    try {
      chatClientRef.current = new TwitchChatClient(channelData.name)

      chatClientRef.current.onMessage((messageData) => {
        const sentimentResult = sentimentAnalyzer.current.analyzeSentiment(messageData.message)

        // Debug logging
        console.log('Message:', messageData.message)
        console.log('Sentiment Result:', sentimentResult)

        const enrichedMessage = {
          ...messageData,
          sentiment: sentimentResult.sentiment,
          confidence: sentimentResult.confidence,
          emotions: sentimentResult.emotions,
          timestamp: new Date(),
          id: Date.now() + Math.random()
        }

        setMessages(prev => [...prev, enrichedMessage])
        setRecentMessages(prev => [enrichedMessage, ...prev.slice(0, 49)]) // Keep last 50

        // Update emotion data
        if (sentimentResult.emotions) {
          setEmotionData(prev => {
            const newData = { ...prev }
            Object.entries(sentimentResult.emotions).forEach(([emotion, score]) => {
              if (score > 0.3) { // Only count significant emotions
                newData[emotion] = (newData[emotion] || 0) + score
              }
            })
            return newData
          })
        }

        setStats(prev => {
          const newStats = {
            total: prev.total + 1,
            positive: prev.positive + (sentimentResult.sentiment === 'positive' ? 1 : 0),
            neutral: prev.neutral + (sentimentResult.sentiment === 'neutral' ? 1 : 0),
            negative: prev.negative + (sentimentResult.sentiment === 'negative' ? 1 : 0),
            toxic: prev.toxic + (sentimentResult.sentiment === 'toxic' ? 1 : 0),
            messagesPerMinute: calculateMessagesPerMinute(prev.total + 1)
          }

          console.log('Stats updated:', newStats)
          console.log('Sentiment was:', sentimentResult.sentiment)
          return newStats
        })
        // Update timeline
        updateTimeline(sentimentResult.sentiment)

        // Update advanced statistics
        setAdvancedStats(prevAdvanced => {
          const newAdvanced = { ...prevAdvanced }

          // Update most active users
          const userCount = newAdvanced.mostActiveUsers.get(enrichedMessage.username) || 0
          newAdvanced.mostActiveUsers.set(enrichedMessage.username, userCount + 1)

          // Update unique users
          newAdvanced.uniqueUsers.add(enrichedMessage.username)

          // Calculate average message length
          const wordCount = enrichedMessage.message.split(' ').length
          newAdvanced.totalWords += wordCount

          // Update top emotions
          if (sentimentResult.emotions) {
            const topEmotion = Object.entries(sentimentResult.emotions)
              .reduce((max, [emotion, score]) => score > max.score ? { emotion, score } : max, { emotion: '', score: 0 })

            if (topEmotion.score > 0.3) {
              const existingIndex = newAdvanced.topEmotions.findIndex(e => e.emotion === topEmotion.emotion)
              if (existingIndex >= 0) {
                newAdvanced.topEmotions[existingIndex].count++
              } else {
                newAdvanced.topEmotions.push({ ...topEmotion, count: 1 })
              }
              newAdvanced.topEmotions.sort((a, b) => b.count - a.count).slice(0, 5)
            }
          }

          return newAdvanced
        })
      })

      await chatClientRef.current.connect()
      setIsConnected(true)
    } catch (error) {
      console.error('Failed to connect to chat:', error)
    }
  }

  const calculateMessagesPerMinute = (totalMessages) => {
    // Simple calculation - in real app you'd track time windows
    return Math.round(totalMessages / Math.max(1, (Date.now() - (channelData.connectedAt?.getTime() || Date.now())) / 60000))
  }

  const updateTimeline = (sentiment) => {
    const now = new Date()
    const timeLabel = now.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    })

    setTimelineData(prev => {
      // Keep only last 20 data points
      const maxPoints = 20

      let newLabels = [...prev.labels]
      let newDatasets = prev.datasets.map(dataset => ({ ...dataset, data: [...dataset.data] }))

      // Add new time label if it doesn't exist
      if (!newLabels.includes(timeLabel)) {
        newLabels.push(timeLabel)

        // Initialize all datasets with 0 for this time point
        newDatasets.forEach(dataset => {
          dataset.data.push(0)
        })

        // Trim to max points
        if (newLabels.length > maxPoints) {
          newLabels = newLabels.slice(-maxPoints)
          newDatasets.forEach(dataset => {
            dataset.data = dataset.data.slice(-maxPoints)
          })
        }
      }

      // Increment the count for the current sentiment
      const currentIndex = newLabels.indexOf(timeLabel)
      if (currentIndex !== -1) {
        const sentimentIndex = {
          'positive': 0,
          'neutral': 1,
          'negative': 2,
          'toxic': 3
        }[sentiment]

        if (sentimentIndex !== undefined) {
          newDatasets[sentimentIndex].data[currentIndex]++
        }
      }

      return {
        labels: newLabels,
        datasets: newDatasets
      }
    })
  }

  const blockUser = (username) => {
    setBlockedUsers(prev => new Set([...prev, username]))
  }

  const unblockUser = (username) => {
    setBlockedUsers(prev => {
      const newSet = new Set(prev)
      newSet.delete(username)
      return newSet
    })
  }

  const filteredMessages = recentMessages.filter(msg => {
    // Apply search filter
    if (searchFilter && !msg.message.toLowerCase().includes(searchFilter.toLowerCase()) &&
      !msg.username.toLowerCase().includes(searchFilter.toLowerCase())) {
      return false
    }

    // Apply sentiment filter
    if (sentimentFilter !== 'all' && msg.sentiment !== sentimentFilter) {
      return false
    }

    // Filter blocked users
    if (blockedUsers.has(msg.username)) {
      return false
    }

    return true
  })

  const exportChatLog = () => {
    const dataStr = JSON.stringify(recentMessages, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `chat-log-${channelData.name}-${new Date().toISOString()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const toggleDemoMessages = () => {
    if (chatClientRef.current) {
      if (demoRunning) {
        chatClientRef.current.stopDemoMessages()
        setDemoRunning(false)
      } else {
        chatClientRef.current.startDemoMessages()
        setDemoRunning(true)
      }
    }
  }

  const sentimentChartData = {
    labels: ['Positive', 'Neutral', 'Negative', 'Toxic'],
    datasets: [{
      data: [stats.positive, stats.neutral, stats.negative, stats.toxic],
      backgroundColor: ['#10b981', '#6b7280', '#f59e0b', '#ef4444'],
      borderWidth: 0
    }]
  }

  const emotionChartData = {
    labels: ['Joy', 'Anger', 'Fear', 'Sadness', 'Surprise', 'Disgust'],
    datasets: [{
      label: 'Emotion Intensity',
      data: [
        emotionData.joy, emotionData.anger, emotionData.fear,
        emotionData.sadness, emotionData.surprise, emotionData.disgust
      ],
      backgroundColor: [
        '#fbbf24', '#ef4444', '#8b5cf6',
        '#3b82f6', '#06d6a0', '#f97316'
      ],
      borderRadius: 4
    }]
  }

  const activityChartData = {
    labels: ['Last 10min', 'Last 20min', 'Last 30min', 'Last 40min', 'Last 50min', 'Last 60min'],
    datasets: [{
      label: 'Messages',
      data: [45, 67, 23, 89, 34, 56], // Mock data - in real app calculate from messages
      backgroundColor: 'rgba(102, 126, 234, 0.8)',
      borderRadius: 4
    }]
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#10b981'
      case 'negative': return '#f59e0b'
      case 'toxic': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '😊'
      case 'negative': return '😞'
      case 'toxic': return '😠'
      default: return '😐'
    }
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <button onClick={onBack} className="back-button">
            ← Back
          </button>
          <button onClick={onLeagueFeatures} className="league-button">
            🎮 League Features
          </button>
          <div className="channel-info">
            <h1>Monitoring: {channelData.name}</h1>
            <div className="connection-status">
              <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
              {isConnected ? 'Connected' : 'Connecting...'}
            </div>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-card">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Total Messages</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.messagesPerMinute}</span>
            <span className="stat-label">Messages/min</span>
          </div>
          <div className="stat-card negative-tracker">
            <span className="stat-value" style={{ color: '#f59e0b' }}>{stats.negative}</span>
            <span className="stat-label">Negative</span>
          </div>
          <div className="stat-card toxic-tracker">
            <span className="stat-value" style={{ color: '#ef4444' }}>{stats.toxic}</span>
            <span className="stat-label">Toxic</span>
          </div>
          <div className="stat-card">
            <span className="stat-value" style={{ color: '#a855f7' }}>
              {advancedStats.uniqueUsers.size > 999 ? '999+' : advancedStats.uniqueUsers.size}
            </span>
            <span className="stat-label">Unique Users</span>
          </div>
          <div className="stat-card">
            <span className="stat-value" style={{ color: '#06b6d4' }}>{Math.round(advancedStats.averageMessageLength)}</span>
            <span className="stat-label">Avg Words</span>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="advanced-stats-section">
          <div className="stats-grid">
            <div className="stat-box">
              <h4>Most Active Users</h4>
              <div className="user-list">
                {Array.from(advancedStats.mostActiveUsers.entries())
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([username, count]) => (
                    <div key={username} className="user-stat">
                      <span className="username-stat">{username}</span>
                      <span className="count-stat">{count}</span>
                    </div>
                  ))}
              </div>
            </div>

            <div className="stat-box">
              <h4>Top Emotions</h4>
              <div className="emotion-list">
                {advancedStats.topEmotions.slice(0, 5).map((emotion, index) => (
                  <div key={index} className="emotion-stat">
                    <span className="emotion-name">{emotion.emotion}</span>
                    <span className="emotion-count">{emotion.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="stat-box">
              <h4>Session Stats</h4>
              <div className="session-stats">
                <div className="session-stat">
                  <span>Duration</span>
                  <span>{Math.round((Date.now() - sessionStartTime.getTime()) / 60000)}m</span>
                </div>
                <div className="session-stat">
                  <span>Total Words</span>
                  <span>{advancedStats.totalWords}</span>
                </div>
                <div className="session-stat">
                  <span>Sentiment Trend</span>
                  <span className={`trend-${advancedStats.sentimentTrend}`}>
                    {advancedStats.sentimentTrend}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Top Statistics Cards */}
        <div className="top-stats-grid">
          <div className="top-stat-card positive">
            <div className="stat-icon">
              <div className="pulse-icon positive-pulse">📈</div>
            </div>
            <div className="stat-info">
              <div className="stat-title">Positive Sentiment</div>
              <div className="stat-main-value">{Math.round((stats.positive / Math.max(stats.total, 1)) * 100)}%</div>
              <div className="stat-change positive-change">+5%</div>
            </div>
          </div>

          <div className="top-stat-card toxic">
            <div className="stat-icon">
              <div className="pulse-icon toxic-pulse">⚠️</div>
            </div>
            <div className="stat-info">
              <div className="stat-title">Toxic Content</div>
              <div className="stat-main-value">{Math.round((stats.toxic / Math.max(stats.total, 1)) * 100)}%</div>
              <div className="stat-change negative-change">-8%</div>
            </div>
          </div>

          <div className="top-stat-card active">
            <div className="stat-icon">
              <div className="pulse-icon active-pulse">👥</div>
            </div>
            <div className="stat-info">
              <div className="stat-title">Active Users</div>
              <div className="stat-main-value">{Math.min(stats.total + 42, 999)}</div>
              <div className="stat-change positive-change">+23%</div>
            </div>
          </div>
        </div>

        {/* Enhanced Monitoring Controls */}
        <div className="monitoring-controls">
          <div className="control-section">
            <div className="search-controls">
              <input
                type="text"
                placeholder="Search messages or users..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="search-input"
              />
              <select
                value={sentimentFilter}
                onChange={(e) => setSentimentFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Sentiments</option>
                <option value="positive">Positive Only</option>
                <option value="neutral">Neutral Only</option>
                <option value="negative">Negative Only</option>
                <option value="toxic">Toxic Only</option>
              </select>
            </div>
            <div className="action-controls">
              <button
                onClick={() => setShowModeration(!showModeration)}
                className={`control-btn ${showModeration ? 'active' : ''}`}
              >
                🛡️ Moderation
              </button>
              <button
                onClick={toggleDemoMessages}
                className={`control-btn ${demoRunning ? 'active' : ''}`}
              >
                {demoRunning ? '⏹️ Stop Demo' : '▶️ Start Demo'}
              </button>
              <button onClick={exportChatLog} className="control-btn">
                💾 Export Log
              </button>
            </div>
          </div>
        </div>

        <div className="charts-section">
          <div className="chart-card sentiment-timeline">
            <h3>Sentiment Timeline</h3>
            <div className="chart-container">
              <Line
                data={timelineData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: {
                        color: '#c4b5fd',
                        usePointStyle: true,
                        padding: 20
                      }
                    }
                  },
                  scales: {
                    x: {
                      grid: {
                        color: 'rgba(168, 85, 247, 0.1)'
                      },
                      ticks: {
                        color: '#c4b5fd'
                      }
                    },
                    y: {
                      beginAtZero: true,
                      grid: {
                        color: 'rgba(168, 85, 247, 0.1)'
                      },
                      ticks: {
                        color: '#c4b5fd'
                      }
                    }
                  }
                }}
              />
            </div>
          </div>

          <div className="chart-card">
            <h3>Sentiment Distribution</h3>
            <div className="chart-container">
              <Doughnut
                data={sentimentChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: {
                        color: '#c4b5fd',
                        usePointStyle: true,
                        padding: 20
                      }
                    }
                  }
                }}
              />
            </div>
          </div>

          <div className="chart-card">
            <h3>Emotion Analysis</h3>
            <div className="chart-container">
              <Bar
                data={emotionChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false }
                  },
                  scales: {
                    x: {
                      ticks: { color: '#c4b5fd' },
                      grid: { color: 'rgba(196, 181, 253, 0.1)' }
                    },
                    y: {
                      ticks: { color: '#c4b5fd' },
                      grid: { color: 'rgba(196, 181, 253, 0.1)' }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>

        <div className="live-feed-section">
          <div className="sentiment-summary">
            <div className="sentiment-card positive">
              <div className="sentiment-icon">😊</div>
              <div className="sentiment-count">{stats.positive}</div>
              <div className="sentiment-label">Positive</div>
            </div>
            <div className="sentiment-card neutral">
              <div className="sentiment-icon">😐</div>
              <div className="sentiment-count">{stats.neutral}</div>
              <div className="sentiment-label">Neutral</div>
            </div>
            <div className="sentiment-card negative">
              <div className="sentiment-icon">😞</div>
              <div className="sentiment-count">{stats.negative}</div>
              <div className="sentiment-label">Negative</div>
            </div>
            <div className="sentiment-card toxic">
              <div className="sentiment-icon">😠</div>
              <div className="sentiment-count">{stats.toxic}</div>
              <div className="sentiment-label">Toxic</div>
            </div>
          </div>

          <div className="live-messages">
            <h3>Live Chat Feed</h3>
            <div className="messages-container">
              {filteredMessages.length === 0 ? (
                <div className="no-messages">
                  {searchFilter || sentimentFilter !== 'all' ? 'No messages match your filters' :
                    isConnected ? 'Waiting for messages...' : 'Connecting to chat...'}
                </div>
              ) : (
                filteredMessages.map(message => (
                  <div key={message.id} className={`message-item ${message.sentiment} ${blockedUsers.has(message.username) ? 'blocked' : ''}`}>
                    <div className="message-header">
                      <span className="username">{message.username}</span>
                      <span
                        className="sentiment-badge"
                        style={{ backgroundColor: getSentimentColor(message.sentiment) }}
                      >
                        {getSentimentIcon(message.sentiment)} {message.sentiment}
                      </span>
                      {message.confidence && (
                        <span className="confidence-score">
                          {(message.confidence * 100).toFixed(1)}%
                        </span>
                      )}
                      <span className="timestamp">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {showModeration && (
                        <div className="moderation-controls">
                          {blockedUsers.has(message.username) ? (
                            <button
                              onClick={() => unblockUser(message.username)}
                              className="unblock-btn"
                              title="Unblock user"
                            >
                              🔓
                            </button>
                          ) : (
                            <button
                              onClick={() => blockUser(message.username)}
                              className="block-btn"
                              title="Block user"
                            >
                              🚫
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="message-content">{message.message}</div>
                    {message.emotions && showModeration && (
                      <div className="emotion-tags">
                        {Object.entries(message.emotions)
                          .filter(([, score]) => score > 0.3)
                          .map(([emotion, score]) => (
                            <span key={emotion} className={`emotion-tag ${emotion}`}>
                              {emotion} {(score * 100).toFixed(0)}%
                            </span>
                          ))
                        }
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
