import { useState, useEffect, useRef } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'
import TwitchChatClient from '../services/TwitchChatClient'
import SentimentAnalyzer from '../services/SentimentAnalyzer'
import './Dashboard.css'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

const Dashboard = ({ channelData, onBack }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState([])
  const [stats, setStats] = useState({
    total: 0,
    positive: 0,
    neutral: 0,
    toxic: 0,
    messagesPerMinute: 0
  })
  const [recentMessages, setRecentMessages] = useState([])
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

  const connectToChat = async () => {
    try {
      chatClientRef.current = new TwitchChatClient(channelData.name)
      
      chatClientRef.current.onMessage((messageData) => {
        const sentiment = sentimentAnalyzer.current.analyze(messageData.message)
        const enrichedMessage = {
          ...messageData,
          sentiment,
          timestamp: new Date(),
          id: Date.now() + Math.random()
        }
        
        setMessages(prev => [...prev, enrichedMessage])
        setRecentMessages(prev => [enrichedMessage, ...prev.slice(0, 49)]) // Keep last 50
        
        setStats(prev => ({
          total: prev.total + 1,
          positive: prev.positive + (sentiment === 'positive' ? 1 : 0),
          neutral: prev.neutral + (sentiment === 'neutral' ? 1 : 0),
          toxic: prev.toxic + (sentiment === 'toxic' ? 1 : 0),
          messagesPerMinute: calculateMessagesPerMinute(prev.total + 1)
        }))
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

  const sentimentChartData = {
    labels: ['Positive', 'Neutral', 'Toxic'],
    datasets: [{
      data: [stats.positive, stats.neutral, stats.toxic],
      backgroundColor: ['#10b981', '#6b7280', '#ef4444'],
      borderWidth: 0
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
      case 'toxic': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '😊'
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
        </div>
      </header>

      <div className="dashboard-content">
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

        <div className="charts-section">
          <div className="chart-card sentiment-timeline">
            <h3>Sentiment Timeline</h3>
            <div className="chart-container">
              <Bar 
                data={{
                  labels: ['14:00', '14:15', '14:30', '14:45', '15:00', '15:15', '15:30', '15:45'],
                  datasets: [
                    {
                      label: 'Positive Content',
                      data: [45, 67, 23, 89, 34, 56, 78, 92],
                      backgroundColor: '#10b981',
                      borderRadius: 4,
                      stack: 'Stack 0',
                    },
                    {
                      label: 'Toxic Content',
                      data: [5, 8, 3, 12, 4, 7, 9, 11],
                      backgroundColor: '#ef4444',
                      borderRadius: 4,
                      stack: 'Stack 0',
                    }
                  ]
                }}
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
                      stacked: true,
                      grid: {
                        color: 'rgba(168, 85, 247, 0.1)'
                      },
                      ticks: {
                        color: '#c4b5fd'
                      }
                    },
                    y: {
                      stacked: true,
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
            <div className="sentiment-card toxic">
              <div className="sentiment-icon">😠</div>
              <div className="sentiment-count">{stats.toxic}</div>
              <div className="sentiment-label">Toxic</div>
            </div>
          </div>

          <div className="live-messages">
            <h3>Live Chat Feed</h3>
            <div className="messages-container">
              {recentMessages.length === 0 ? (
                <div className="no-messages">
                  {isConnected ? 'Waiting for messages...' : 'Connecting to chat...'}
                </div>
              ) : (
                recentMessages.map(message => (
                  <div key={message.id} className="message-item">
                    <div className="message-header">
                      <span className="username">{message.username}</span>
                      <span 
                        className="sentiment-badge"
                        style={{ backgroundColor: getSentimentColor(message.sentiment) }}
                      >
                        {getSentimentIcon(message.sentiment)} {message.sentiment}
                      </span>
                      <span className="timestamp">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="message-content">{message.message}</div>
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
