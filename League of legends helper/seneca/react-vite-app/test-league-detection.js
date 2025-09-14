// Test script to verify League detection functionality
// This simulates League-related chat messages to trigger detection

import LeagueDetectionService from '../src/services/LeagueDetectionService.js'

const testLeagueDetection = () => {
  console.log('🧪 Testing League Detection Service...')
  
  const detectionService = new LeagueDetectionService()
  
  // Setup detection callback
  detectionService.onDetectionChange((isDetected) => {
    console.log(`🎮 League Detection Status: ${isDetected ? '✅ ACTIVE' : '❌ INACTIVE'}`)
  })
  
  // Test messages that should trigger League detection
  const leagueMessages = [
    { user: 'TestUser1', message: 'yasuo is so broken' },
    { user: 'TestUser2', message: 'going for baron steal!' },
    { user: 'TestUser3', message: 'nice pentakill dude' },
    { user: 'TestUser4', message: '5/2/8 on jinx' },
    { user: 'TestUser5', message: 'need to ward dragon' },
    { user: 'TestUser6', message: 'ff at 15' },
    { user: 'TestUser7', message: 'team diff gg' },
    { user: 'TestUser8', message: 'buying infinity edge' },
    { user: 'TestUser9', message: 'mid lane ganked again' },
    { user: 'TestUser10', message: 'jungle diff tbh' }
  ]
  
  // Test messages that should NOT trigger League detection
  const nonLeagueMessages = [
    { user: 'TestUser1', message: 'hello chat' },
    { user: 'TestUser2', message: 'how is everyone doing?' },
    { user: 'TestUser3', message: 'loving this stream' },
    { user: 'TestUser4', message: 'what time is it?' },
    { user: 'TestUser5', message: 'great gameplay!' }
  ]
  
  console.log('\n📝 Testing League-related messages...')
  leagueMessages.forEach((msg, index) => {
    setTimeout(() => {
      const analysis = detectionService.analyzeMessage(msg.message, msg.user)
      console.log(`${index + 1}. "${msg.message}" - Confidence: ${(analysis.confidence * 100).toFixed(1)}% | Keywords: [${analysis.keywords.join(', ')}]`)
    }, index * 100) // Small delay between messages
  })
  
  // Wait a bit then test non-League messages
  setTimeout(() => {
    console.log('\n📝 Testing non-League messages...')
    nonLeagueMessages.forEach((msg, index) => {
      setTimeout(() => {
        const analysis = detectionService.analyzeMessage(msg.message, msg.user)
        console.log(`${index + 1}. "${msg.message}" - Confidence: ${(analysis.confidence * 100).toFixed(1)}%`)
      }, index * 100)
    })
  }, leagueMessages.length * 100 + 500)
  
  // Check detection status after all messages
  setTimeout(() => {
    console.log('\n📊 Final Detection Status:')
    const status = detectionService.getDetectionStatus()
    console.log(`- League Detected: ${status.isLeagueDetected}`)
    console.log(`- Current Confidence: ${(status.confidence * 100).toFixed(1)}%`)
    console.log(`- Recent Activity: ${status.recentActivity.leagueMessages}/${status.recentActivity.totalMessages} League messages`)
    
    if (status.recentActivity.topKeywords.length > 0) {
      console.log('- Top Keywords:', status.recentActivity.topKeywords.map(k => `${k.keyword}(${k.count})`).join(', '))
    }
  }, (leagueMessages.length + nonLeagueMessages.length) * 100 + 1000)
}

// Test manual trigger
const testManualTrigger = () => {
  console.log('\n🎯 Testing manual League detection trigger...')
  
  const detectionService = new LeagueDetectionService()
  
  detectionService.onDetectionChange((isDetected) => {
    console.log(`🔧 Manual Detection Status: ${isDetected ? '✅ ENABLED' : '❌ DISABLED'}`)
  })
  
  // Force enable
  console.log('Forcing League detection ON...')
  detectionService.forceLeagueDetection(true)
  
  setTimeout(() => {
    console.log('Forcing League detection OFF...')
    detectionService.forceLeagueDetection(false)
  }, 2000)
}

// Run tests
console.log('🚀 Starting League Detection Tests\n')
testLeagueDetection()

setTimeout(() => {
  testManualTrigger()
}, 5000)

export { testLeagueDetection, testManualTrigger }