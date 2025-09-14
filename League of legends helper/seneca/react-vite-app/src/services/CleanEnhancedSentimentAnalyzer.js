class EnhancedSentimentAnalyzer {
  constructor() {
    this.positiveWords = [
      'good', 'great', 'awesome', 'amazing', 'fantastic', 'excellent', 'wonderful',
      'love', 'like', 'enjoy', 'fun', 'nice', 'cool', 'sweet', 'epic', 'legendary',
      'poggers', 'pog', 'hype', 'wp', 'gg', 'nice play', 'clutch', 'insane',
      'sick', 'crazy good', 'perfect', 'beautiful', 'incredible', 'outstanding'
    ]

    this.negativeWords = [
      'bad', 'terrible', 'awful', 'horrible', 'hate', 'suck', 'worst', 'stupid',
      'dumb', 'trash', 'garbage', 'noob', 'fail', 'pathetic', 'useless', 'lame'
    ]

    this.toxicKeywords = [
      'toxic', 'troll', 'grief', 'int', 'feeding', 'report', 'ban', 'kick',
      'uninstall', 'delete game', 'go next', 'ff15', 'surrender', 'rage quit'
    ]

    this.profanityWords = [
      'damn', 'hell', 'crap', 'wtf', 'omg', 'ffs', 'bs'
    ]

    this.emotionKeywords = {
      joy: ['happy', 'excited', 'joy', 'celebration', 'laugh', 'smile', 'fun', 'amazing', 'awesome', 'poggers'],
      anger: ['angry', 'mad', 'rage', 'furious', 'pissed', 'annoyed', 'frustrated', 'hate', 'stupid', 'trash'],
      sadness: ['sad', 'disappointed', 'depressed', 'unhappy', 'crying', 'tears', 'upset', 'down'],
      surprise: ['wow', 'omg', 'shocked', 'surprised', 'wtf', 'no way', 'incredible', 'unbelievable'],
      fear: ['scared', 'afraid', 'worried', 'nervous', 'anxious', 'panic', 'terrified'],
      disgust: ['gross', 'disgusting', 'eww', 'yuck', 'horrible', 'awful', 'terrible']
    }
  }

  analyzeSentiment(message) {
    const sentiment = this.classifySentiment(message)
    const emotions = this.analyzeEmotions(message)
    const confidence = this.getConfidence(message)
    
    return {
      sentiment,
      emotions,
      confidence,
      timestamp: new Date()
    }
  }

  classifySentiment(text) {
    const textLower = text.toLowerCase()
    let positiveScore = 0
    let negativeScore = 0
    let neutralScore = 1 // Base neutral score

    // Check for positive words
    this.positiveWords.forEach(word => {
      if (textLower.includes(word)) {
        positiveScore += 1
      }
    })

    // Check for negative words
    this.negativeWords.forEach(word => {
      if (textLower.includes(word)) {
        negativeScore += 1
      }
    })

    // Check for toxic keywords
    this.toxicKeywords.forEach(keyword => {
      if (textLower.includes(keyword)) {
        negativeScore += 2 // Weight toxic words more heavily
      }
    })

    // Check for profanity
    this.profanityWords.forEach(word => {
      if (textLower.includes(word)) {
        negativeScore += 1.5
      }
    })

    // Check for positive gaming expressions
    if (textLower.includes('gg') || textLower.includes('wp') || textLower.includes('nice')) {
      positiveScore += 1
    }

    // Calculate final sentiment
    const totalScore = positiveScore + neutralScore + negativeScore
    
    if (totalScore === 0) {
      return 'neutral'
    }

    if (negativeScore > positiveScore && negativeScore > 2) {
      return 'toxic'
    } else if (negativeScore > positiveScore && negativeScore > 0) {
      return 'negative'
    } else if (positiveScore > negativeScore) {
      return 'positive'
    } else {
      return 'neutral'
    }
  }

  analyzeEmotions(text) {
    const textLower = text.toLowerCase()
    const emotions = {
      joy: 0,
      anger: 0,
      sadness: 0,
      surprise: 0,
      fear: 0,
      disgust: 0
    }

    Object.keys(this.emotionKeywords).forEach(emotion => {
      this.emotionKeywords[emotion].forEach(keyword => {
        if (textLower.includes(keyword)) {
          emotions[emotion] += 0.3
        }
      })
    })

    // Normalize emotions
    const maxEmotion = Math.max(...Object.values(emotions))
    if (maxEmotion > 0) {
      Object.keys(emotions).forEach(emotion => {
        emotions[emotion] = emotions[emotion] / maxEmotion
      })
    }

    return emotions
  }

  analyzeEmotion(text) {
    const emotions = this.analyzeEmotions(text)
    const maxEmotion = Object.keys(emotions).reduce((a, b) => emotions[a] > emotions[b] ? a : b)
    return emotions[maxEmotion] > 0.1 ? maxEmotion : 'neutral'
  }

  getConfidence(message) {
    const indicators = this.countSentimentIndicators(message.toLowerCase())
    let confidence
    
    if (indicators <= 1) {
      confidence = 0.3 + (indicators * 0.2)
    } else if (indicators <= 3) {
      confidence = 0.6 + ((indicators - 1) * 0.15)
    } else {
      confidence = 0.85 + Math.min((indicators - 3) * 0.05, 0.1)
    }
    
    return Math.min(confidence, 0.95)
  }

  countSentimentIndicators(text) {
    let count = 0
    
    this.positiveWords.concat(this.negativeWords, this.toxicKeywords, this.profanityWords).forEach(word => {
      if (text.includes(word.toLowerCase())) {
        count++
      }
    })

    return count
  }

  // Legacy method for compatibility
  analyze(message) {
    return this.classifySentiment(message)
  }
}

export default EnhancedSentimentAnalyzer