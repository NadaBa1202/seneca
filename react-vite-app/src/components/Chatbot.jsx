import { useState, useRef, useEffect } from 'react'
import './Chatbot.css'

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I'm your Chat.GG assistant. I can help you understand your stream analytics, explain sentiment analysis, or answer questions about your chat data. How can I help you today?",
      isBot: true,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const generateBotResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase()
    
    // Predefined responses based on keywords
    if (lowerMessage.includes('sentiment') || lowerMessage.includes('analysis')) {
      return "Sentiment analysis classifies chat messages into three categories: Positive (compliments, support), Neutral (questions, general chat), and Toxic (hate speech, insults). Our AI analyzes keywords, emotes, capitalization, and context to determine sentiment."
    }
    
    if (lowerMessage.includes('toxic') || lowerMessage.includes('moderation')) {
      return "Toxic content detection helps you identify harmful messages in your chat. We look for hate speech, insults, and negative language patterns. You can use this data to improve moderation and create a healthier chat environment."
    }
    
    if (lowerMessage.includes('statistics') || lowerMessage.includes('stats') || lowerMessage.includes('data')) {
      return "Your statistics show real-time chat activity including messages per minute, sentiment distribution, and engagement trends. The charts help you understand your audience's mood and participation levels throughout your stream."
    }
    
    if (lowerMessage.includes('chart') || lowerMessage.includes('graph')) {
      return "The dashboard includes sentiment distribution (doughnut chart) and activity timeline (bar chart). These visualizations help you quickly understand chat patterns and viewer engagement over time."
    }
    
    if (lowerMessage.includes('twitch') || lowerMessage.includes('stream')) {
      return "Chat.GG connects to Twitch chat using TMI.js to monitor live messages. Simply enter any Twitch channel name or URL to start analyzing chat sentiment and engagement in real-time."
    }
    
    if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
      return "I can help you with: Understanding sentiment analysis, explaining statistics, interpreting charts, moderation tips, and general questions about Chat.GG features. What would you like to know more about?"
    }
    
    if (lowerMessage.includes('positive') || lowerMessage.includes('good')) {
      return "Positive sentiment includes compliments, support messages, excitement, and encouraging words. High positive sentiment indicates an engaged and supportive community. Look for trends in positive spikes during exciting stream moments!"
    }
    
    if (lowerMessage.includes('neutral')) {
      return "Neutral messages are typically questions, general chat, or informational content. They're the backbone of healthy chat interaction and often indicate active viewer engagement without strong emotional content."
    }
    
    // Default responses for unmatched queries
    const defaultResponses = [
      "That's an interesting question! Could you be more specific about what aspect of Chat.GG you'd like to know about?",
      "I'd be happy to help! Try asking about sentiment analysis, statistics, charts, or moderation features.",
      "Great question! I can explain how our analytics work, help interpret your data, or provide tips for better chat management.",
      "I'm here to help with Chat.GG! Ask me about sentiment analysis, toxicity detection, or how to use the dashboard effectively."
    ]
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)]
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      isBot: false,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    // Simulate typing delay
    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        text: generateBotResponse(inputValue),
        isBot: true,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, botResponse])
      setIsTyping(false)
    }, 1000 + Math.random() * 1000) // 1-2 second delay
  }

  return (
    <>
      {/* Floating Chat Icon */}
      <div 
        className={`chatbot-icon ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? '' : '💬'}
      </div>

      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-title">
              <span className="bot-avatar">🤖</span>
              Chat.GG Assistant
            </div>
            <button 
              className="close-button"
              onClick={() => setIsOpen(false)}
            >
              ✕
            </button>
          </div>
          
          <div className="chatbot-messages">
            {messages.map(message => (
              <div 
                key={message.id} 
                className={`message ${message.isBot ? 'bot-message' : 'user-message'}`}
              >
                <div className="message-content">
                  {message.text}
                </div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message bot-message typing">
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
          
          <form onSubmit={handleSendMessage} className="chatbot-input">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me about your chat analytics..."
              className="message-input"
            />
            <button type="submit" className="send-button">
              ➤
            </button>
          </form>
        </div>
      )}
    </>
  )
}

export default Chatbot
