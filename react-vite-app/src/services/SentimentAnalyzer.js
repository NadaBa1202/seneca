class SentimentAnalyzer {
  constructor() {
    // Positive keywords and phrases
    this.positiveKeywords = [
      'amazing', 'awesome', 'great', 'excellent', 'fantastic', 'wonderful', 'love', 'best',
      'good', 'nice', 'cool', 'perfect', 'brilliant', 'outstanding', 'incredible', 'superb',
      'thank you', 'thanks', 'appreciate', 'grateful', 'happy', 'excited', 'enjoy',
      'beautiful', 'impressive', 'skilled', 'talented', 'pro', 'legend', 'king', 'queen',
      'follow', 'sub', 'subscribe', 'support', 'donation', 'bits', 'pog', 'poggers',
      'hype', 'lit', 'fire', 'epic', 'clutch', 'insane', 'mad skills', 'godlike'
    ]

    // Toxic/negative keywords and phrases
    this.toxicKeywords = [
      'hate', 'suck', 'terrible', 'awful', 'worst', 'bad', 'stupid', 'dumb', 'idiot',
      'noob', 'trash', 'garbage', 'pathetic', 'loser', 'fail', 'failure', 'useless',
      'annoying', 'boring', 'lame', 'cringe', 'toxic', 'cancer', 'kill yourself',
      'kys', 'die', 'death', 'murder', 'violence', 'threat', 'attack', 'destroy',
      'rekt', 'owned', 'pwned', 'scrub', 'ez', 'easy', 'git gud', 'uninstall',
      'quit', 'leave', 'stop', 'delete', 'remove', 'ban', 'report', 'mute'
    ]

    // Neutral indicators
    this.neutralKeywords = [
      'what', 'how', 'when', 'where', 'why', 'who', 'question', 'ask', 'tell',
      'explain', 'show', 'help', 'tutorial', 'guide', 'tip', 'advice', 'suggestion',
      'maybe', 'perhaps', 'probably', 'might', 'could', 'would', 'should',
      'ok', 'okay', 'fine', 'sure', 'yes', 'no', 'true', 'false', 'right', 'wrong'
    ]

    // Emote patterns that indicate sentiment
    this.positiveEmotes = ['😊', '😄', '😃', '😁', '🙂', '😍', '🥰', '😘', '👍', '👏', '🎉', '❤️', '💖', '🔥', '💯']
    this.negativeEmotes = ['😠', '😡', '🤬', '😤', '😒', '🙄', '😢', '😭', '💔', '👎', '🖕']
    this.neutralEmotes = ['😐', '😑', '🤔', '😕', '😬', '🤷', '❓', '❔']
  }

  analyze(message) {
    if (!message || typeof message !== 'string') {
      return 'neutral'
    }

    const text = message.toLowerCase()
    let positiveScore = 0
    let negativeScore = 0
    let neutralScore = 0

    // Check for positive keywords
    this.positiveKeywords.forEach(keyword => {
      if (text.includes(keyword)) {
        positiveScore += 1
      }
    })

    // Check for toxic keywords
    this.toxicKeywords.forEach(keyword => {
      if (text.includes(keyword)) {
        negativeScore += 2 // Weight toxic words more heavily
      }
    })

    // Check for neutral keywords
    this.neutralKeywords.forEach(keyword => {
      if (text.includes(keyword)) {
        neutralScore += 0.5
      }
    })

    // Check for emotes
    this.positiveEmotes.forEach(emote => {
      if (message.includes(emote)) {
        positiveScore += 1
      }
    })

    this.negativeEmotes.forEach(emote => {
      if (message.includes(emote)) {
        negativeScore += 1.5
      }
    })

    this.neutralEmotes.forEach(emote => {
      if (message.includes(emote)) {
        neutralScore += 0.5
      }
    })

    // Check for caps (might indicate excitement or anger)
    const capsRatio = (message.match(/[A-Z]/g) || []).length / message.length
    if (capsRatio > 0.6 && message.length > 3) {
      // High caps ratio - could be positive excitement or negative anger
      if (positiveScore > negativeScore) {
        positiveScore += 1
      } else {
        negativeScore += 1
      }
    }

    // Check for excessive punctuation
    const exclamationCount = (message.match(/!/g) || []).length
    const questionCount = (message.match(/\?/g) || []).length
    
    if (exclamationCount > 1) {
      if (positiveScore > negativeScore) {
        positiveScore += 0.5
      } else {
        negativeScore += 0.5
      }
    }

    if (questionCount > 0) {
      neutralScore += 0.5
    }

    // Determine final sentiment
    const totalScore = positiveScore + negativeScore + neutralScore
    
    if (totalScore === 0) {
      return 'neutral'
    }

    if (negativeScore > positiveScore && negativeScore > neutralScore) {
      return 'toxic'
    } else if (positiveScore > negativeScore && positiveScore > neutralScore) {
      return 'positive'
    } else {
      return 'neutral'
    }
  }

  // Get sentiment confidence score (0-1)
  getConfidence(message) {
    const sentiment = this.analyze(message)
    const text = message.toLowerCase()
    
    let matchCount = 0
    let totalWords = text.split(' ').length

    if (sentiment === 'positive') {
      this.positiveKeywords.forEach(keyword => {
        if (text.includes(keyword)) matchCount++
      })
    } else if (sentiment === 'toxic') {
      this.toxicKeywords.forEach(keyword => {
        if (text.includes(keyword)) matchCount++
      })
    } else {
      this.neutralKeywords.forEach(keyword => {
        if (text.includes(keyword)) matchCount++
      })
    }

    return Math.min(matchCount / Math.max(totalWords, 1), 1)
  }
}

export default SentimentAnalyzer
