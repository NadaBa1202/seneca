#!/bin/bash

# League of Legends Assistant - Quick Start Script
# This script sets up and runs the application for development or production

set -e  # Exit on any error

echo "🎮 League of Legends Assistant - Quick Start"
echo "=============================================="

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker and Docker Compose found"
    USE_DOCKER=true
else
    echo "⚠️  Docker not found, using Node.js deployment"
    USE_DOCKER=false
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your RIOT_API_KEY before continuing"
    echo "   Get your key from: https://developer.riotgames.com/"
    read -p "Press Enter when you've added your API key..."
fi

# Check if API key is set
if grep -q "your-riot-api-key-here" .env; then
    echo "❌ Please set your RIOT_API_KEY in .env file"
    exit 1
fi

echo "✅ Environment configuration found"

if [ "$USE_DOCKER" = true ]; then
    echo "🐳 Starting with Docker..."
    
    # Ask for deployment type
    echo "Choose deployment type:"
    echo "1) Development (app only)"
    echo "2) Production (with nginx reverse proxy)"
    read -p "Enter choice (1 or 2): " DEPLOY_TYPE
    
    if [ "$DEPLOY_TYPE" = "2" ]; then
        echo "🚀 Starting production deployment..."
        docker-compose --profile production up -d
        echo "✅ Application started!"
        echo "   Frontend: http://localhost (port 80)"
        echo "   API: http://localhost:3001"
    else
        echo "🔧 Starting development deployment..."
        docker-compose up -d
        echo "✅ Application started!"
        echo "   Frontend: http://localhost:3000"
        echo "   API: http://localhost:3001"
    fi
    
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
    
else
    echo "📦 Starting with Node.js..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js not found. Please install Node.js 16+ and try again"
        exit 1
    fi
    
    echo "✅ Node.js found: $(node --version)"
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install
    fi
    
    if [ ! -d "seneca/react-vite-app/node_modules" ]; then
        echo "📦 Installing React app dependencies..."
        cd "seneca/react-vite-app"
        npm install
        cd ../..
    fi
    
    # Build React app
    echo "🔨 Building React app..."
    cd "seneca/react-vite-app"
    npm run build
    cd ../..
    
    echo "🚀 Starting services..."
    
    # Start proxy server in background
    echo "Starting API proxy server..."
    node proxy-server.js &
    PROXY_PID=$!
    
    # Start React app server
    echo "Starting React app..."
    cd "seneca/react-vite-app"
    npx serve -s dist -l 3000 &
    REACT_PID=$!
    cd ../..
    
    echo "✅ Application started!"
    echo "   Frontend: http://localhost:3000"
    echo "   API: http://localhost:3001"
    echo ""
    echo "🛑 To stop, press Ctrl+C"
    
    # Wait for Ctrl+C
    trap "echo 'Stopping services...'; kill $PROXY_PID $REACT_PID 2>/dev/null; exit" INT
    wait
fi

echo ""
echo "🎉 Setup complete! Visit the application in your browser."