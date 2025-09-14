import { useState } from 'react'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'
import Chatbot from './components/Chatbot'
import LeagueFeaturesV2 from './components/LeagueFeaturesV2'
import TestDragontailData from './components/TestDragontailData'
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

  const handleLeagueFeatures = () => {
    setCurrentView('league')
  }

  const handleDataTest = () => {
    setCurrentView('test')
  }

  const handleBackToDashboard = () => {
    setCurrentView('dashboard')
  }

  return (
    <div className="app">
      {currentView === 'landing' ? (
        <LandingPage onChannelConnect={handleChannelConnect} />
      ) : currentView === 'dashboard' ? (
        <Dashboard 
          channelData={channelData} 
          onBack={handleBackToLanding}
          onLeagueFeatures={handleLeagueFeatures}
          onDataTest={handleDataTest}
        />
      ) : currentView === 'league' ? (
        <LeagueFeaturesV2 onBack={handleBackToDashboard} />
      ) : currentView === 'test' ? (
        <TestDragontailData onBack={handleBackToDashboard} />
      ) : null}
      <Chatbot />
    </div>
  )
}

export default App
