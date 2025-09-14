const path = require('path')
const fs = require('fs')

console.log('Current directory:', __dirname)
console.log('Looking for dragontail at:', path.join(__dirname, '../../15.18.1/data/en_US/champion.json'))
console.log('File exists:', fs.existsSync(path.join(__dirname, '../../15.18.1/data/en_US/champion.json')))

// Try different path patterns
const paths = [
  '../15.18.1/data/en_US/champion.json',
  '../../15.18.1/data/en_US/champion.json',
  '../../../15.18.1/data/en_US/champion.json',
  '../../../../15.18.1/data/en_US/champion.json'
]

paths.forEach(testPath => {
  const fullPath = path.join(__dirname, testPath)
  console.log(`Testing: ${testPath} -> ${fullPath} -> exists: ${fs.existsSync(fullPath)}`)
})