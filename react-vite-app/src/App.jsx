import { useState } from 'react'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'
import Chatbot from './components/Chatbot'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('landing')
  const [channelData, setChannelData] = useState(null)

  const handleChannelConnect = (channel) => {
    setChannelData(channel)
    setCurrentView('dashboard')
  }

  const handleBackToLanding = () => {
    setCurrentView('landing')
    setChannelData(null)
  }

  return (
    <div className="app">
      {currentView === 'landing' ? (
        <LandingPage onChannelConnect={handleChannelConnect} />
      ) : (
        <Dashboard 
          channelData={channelData} 
          onBack={handleBackToLanding}
        />
      )}
      <Chatbot />
    </div>
  )
}

export default App
