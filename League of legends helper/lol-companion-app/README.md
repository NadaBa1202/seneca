# League of Legends Companion App

A comprehensive, AI-powered companion application for League of Legends built with Python and Streamlit. This application provides real-time match tracking, advanced analytics, AI-powered Q&A, and professional match analysis.

## 🚀 Features

### Core Features
- **🔴 Live Match Tracking**: Real-time tracking of ongoing matches with automatic event detection
- **🤖 AI-Powered Q&A**: Natural language processing for champion abilities, strategies, and game mechanics
- **📊 Advanced Analytics**: Comprehensive performance metrics, trend analysis, and predictive modeling
- **🏆 Professional Matches**: LCS, LEC, LCK, LPL, and international tournament tracking
- **💬 Sentiment Analysis**: Chat and social media sentiment analysis
- **📤 Data Export**: Multiple export formats (CSV, JSON, PDF) with comprehensive reports

### Technical Features
- **Async/Await Patterns**: Real-time data streaming and concurrent processing
- **Modular Architecture**: Clean, maintainable code with type hints and documentation
- **Caching System**: Intelligent caching for API requests and model inference
- **Error Handling**: Robust error handling and graceful degradation
- **Configuration Management**: Environment-based configuration with validation

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Riot Games API Key
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lol-companion-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env file with your Riot API key and other settings
   ```

4. **Set up Dragontail data**
   ```bash
   # Ensure Dragontail data is in the correct location
   # The app expects data in ../15.18.1/ relative to the app directory
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📋 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# Riot Games API Configuration
RIOT_API_KEY=your_riot_api_key_here
RIOT_BASE_URL=https://na1.api.riotgames.com

# Machine Learning Configuration
USE_GPU=true
QA_MODEL_NAME=deepset/roberta-base-squad2
SENTIMENT_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest

# Feature Flags
ENABLE_PRO_MATCHES=true
ENABLE_SENTIMENT_ANALYSIS=true
ENABLE_REAL_TIME_UPDATES=true
```

### API Key Setup

1. Visit [Riot Developer Portal](https://developer.riotgames.com/)
2. Create an account and generate an API key
3. Add the key to your `.env` file

## 🏗️ Architecture

### Project Structure
```
lol-companion-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── env.example           # Environment configuration template
├── README.md             # This file
└── src/
    ├── config.py         # Configuration management
    ├── api/
    │   └── riot_client.py # Riot Games API integration
    ├── data/
    │   └── dragontail.py # Dragontail data management
    ├── models/
    │   └── __init__.py   # Data models and schemas
    ├── nlp/
    │   └── __init__.py   # NLP pipeline and AI models
    └── services/
        ├── analytics.py   # Advanced analytics engine
        ├── event_detection.py # Event detection and analysis
        ├── export.py     # Data export functionality
        ├── pro_matches.py # Professional match tracking
        └── streaming.py  # Real-time data streaming
```

### Key Components

#### 1. Riot API Integration (`src/api/riot_client.py`)
- Async HTTP client with rate limiting
- Comprehensive error handling and retry logic
- Support for all major Riot API endpoints
- Automatic data parsing and validation

#### 2. Dragontail Data Manager (`src/data/dragontail.py`)
- Efficient loading and caching of static game data
- Champion, item, rune, and ability information
- Search and filtering capabilities
- Async file operations for performance

#### 3. NLP Pipeline (`src/nlp/__init__.py`)
- Question answering with BERT/RoBERTa models
- Sentiment analysis for chat and social media
- Text summarization for match highlights
- Context-aware responses using game data

#### 4. Event Detection (`src/services/event_detection.py`)
- Intelligent event classification and analysis
- Automatic highlight generation
- Real-time event streaming
- Context-aware explanations

#### 5. Analytics Engine (`src/services/analytics.py`)
- Player performance metrics and trends
- Team composition analysis
- Meta game analysis and tier lists
- Predictive modeling for match outcomes

#### 6. Export Service (`src/services/export.py`)
- Multiple export formats (CSV, JSON, PDF)
- Comprehensive report generation
- Data archiving and compression
- Customizable export options

## 🎯 Usage

### Dashboard
The main dashboard provides an overview of:
- Live match statistics
- Recent activity trends
- Top performing champions
- Key match events

### Live Match Tracker
- Enter a summoner name to track their current match
- Real-time event detection and analysis
- Automatic highlight generation
- Live statistics and performance metrics

### AI Assistant
- Ask questions about champions, abilities, and strategies
- Get explanations for game mechanics
- Receive personalized tips and advice
- Context-aware responses using current game data

### Champion Analysis
- Comprehensive champion information
- Ability explanations and tips
- Performance statistics
- Counter and synergy information

### Advanced Analytics
- Player performance analysis
- Team composition evaluation
- Meta game trends
- Predictive match outcomes

### Professional Matches
- Track LCS, LEC, LCK, LPL matches
- View upcoming schedules and results
- Analyze professional team strategies
- Monitor meta trends in competitive play

### Data Export
- Export match data in multiple formats
- Generate comprehensive analytics reports
- Create PDF reports with visualizations
- Archive and compress export files

## 🔧 Development

### Adding New Features

1. **Create new service modules** in `src/services/`
2. **Add data models** in `src/models/__init__.py`
3. **Update configuration** in `src/config.py`
4. **Add UI components** in `app.py`
5. **Update requirements** in `requirements.txt`

### Testing

```bash
# Run individual module tests
python -m pytest src/tests/

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src
```

### Code Quality

```bash
# Format code
black src/ app.py

# Sort imports
isort src/ app.py

# Type checking
mypy src/ app.py

# Linting
flake8 src/ app.py
```

## 📊 Performance

### Optimization Features
- **Async Processing**: Non-blocking operations for better responsiveness
- **Intelligent Caching**: Reduces API calls and improves performance
- **Lazy Loading**: Components load only when needed
- **Batch Processing**: Efficient handling of multiple requests
- **Memory Management**: Optimized data structures and cleanup

### Scalability
- **Modular Design**: Easy to extend and maintain
- **Configuration-Driven**: Flexible deployment options
- **Error Recovery**: Graceful handling of failures
- **Resource Management**: Efficient use of system resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for all modules and functions
- Write tests for new functionality
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Riot Games** for providing the API and game data
- **Hugging Face** for pre-trained transformer models
- **Streamlit** for the web framework
- **Community** for feedback and contributions

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the configuration guide
- Test with sample data first

## 🔮 Roadmap

### Upcoming Features
- **Twitch Integration**: Stream chat analysis and highlight detection
- **Discord Bot**: Community server integration
- **Mobile App**: React Native companion app
- **Advanced ML**: Custom model training and fine-tuning
- **Real-time Collaboration**: Multi-user features and sharing
- **API Server**: RESTful API for external integrations

### Performance Improvements
- **Database Integration**: PostgreSQL for persistent storage
- **Redis Caching**: Distributed caching system
- **Microservices**: Service-oriented architecture
- **Container Deployment**: Docker and Kubernetes support
- **CDN Integration**: Global content delivery

---

**Built with ❤️ for the League of Legends community**