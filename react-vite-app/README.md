# TwitchChatAnalyzer

A real-time Twitch chat monitoring platform that enables streamers to analyze their chat sentiment and engagement through live statistics and visualizations.

## Features

- **Real-time Chat Monitoring**: Connect to any Twitch channel and monitor chat messages as they happen
- **Sentiment Analysis**: Automatically classify messages as positive, neutral, or toxic using advanced keyword analysis
- **Live Statistics Dashboard**: View real-time charts and analytics of chat engagement
- **Modern UI**: Beautiful, responsive interface with smooth animations and transitions
- **Demo Mode**: Includes simulated chat messages for testing and demonstration

## Technologies Used

- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and development server
- **Chart.js** - Interactive charts and data visualization
- **TMI.js** - Twitch chat integration
- **CSS3** - Modern styling with gradients and animations

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd react-vite-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5174`

## Usage

1. **Connect to a Channel**: Enter a Twitch channel name or URL on the landing page
2. **Monitor Chat**: View real-time chat messages with sentiment analysis
3. **Analyze Statistics**: Check the dashboard for sentiment distribution and activity charts
4. **Track Engagement**: Monitor messages per minute and overall chat health

## Project Structure

```
src/
├── components/
│   ├── LandingPage.jsx      # Main landing page component
│   ├── LandingPage.css      # Landing page styles
│   ├── Dashboard.jsx        # Analytics dashboard
│   └── Dashboard.css        # Dashboard styles
├── services/
│   ├── TwitchChatClient.js  # Twitch chat integration
│   └── SentimentAnalyzer.js # Message sentiment analysis
├── App.jsx                  # Main application component
├── App.css                  # Global styles
└── main.jsx                 # Application entry point
```

## Sentiment Analysis

The platform uses a comprehensive sentiment analysis system that evaluates:

- **Positive indicators**: Compliments, support messages, excitement
- **Toxic indicators**: Hate speech, insults, negative language
- **Neutral indicators**: Questions, neutral statements, general chat

The analyzer considers:
- Keyword matching
- Emote usage
- Capitalization patterns
- Punctuation usage
- Context clues

## Features in Detail

### Landing Page
- Clean, modern design with gradient backgrounds
- Channel input with URL validation
- Feature showcase with animated cards
- Step-by-step usage guide

### Dashboard
- Real-time sentiment distribution (doughnut chart)
- Chat activity timeline (bar chart)
- Live message feed with sentiment badges
- Connection status indicators
- Summary statistics cards

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Future Enhancements

- User authentication with Twitch OAuth
- Historical data storage and analysis
- Advanced filtering and moderation tools
- Export functionality for reports
- Multi-channel monitoring
- Custom sentiment keyword configuration
- Integration with streaming software (OBS)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Twitch for providing the chat API
- Chart.js community for excellent charting library
- React and Vite teams for amazing development tools

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
