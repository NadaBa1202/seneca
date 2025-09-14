import { useState } from 'react'

const ApiTest = () => {
  const [result, setResult] = useState('')
  const [error, setError] = useState('')

  const testApi = async () => {
    try {
      const response = await fetch('https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Doublelift/NA1', {
        headers: {
          'X-Riot-Token': 'RGAPI-8994cf2c-4239-4033-b040-20e200c43151'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      setResult(JSON.stringify(data, null, 2))
      setError('')
    } catch (err) {
      setError(err.message)
      setResult('')
    }
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>API Test</h2>
      <button onClick={testApi}>Test Riot API</button>
      {error && <div style={{ color: 'red', marginTop: '10px' }}>Error: {error}</div>}
      {result && <pre style={{ background: '#f5f5f5', padding: '10px', marginTop: '10px' }}>{result}</pre>}
    </div>
  )
}

export default ApiTest