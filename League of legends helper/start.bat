@echo off
setlocal enabledelayedexpansion

REM League of Legends Assistant - Quick Start Script for Windows
REM This script sets up and runs the application for development or production

echo 🎮 League of Legends Assistant - Quick Start
echo ==============================================

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% == 0 (
    docker-compose --version >nul 2>&1
    if %errorlevel% == 0 (
        echo ✅ Docker and Docker Compose found
        set USE_DOCKER=true
    ) else (
        echo ⚠️  Docker Compose not found, using Node.js deployment
        set USE_DOCKER=false
    )
) else (
    echo ⚠️  Docker not found, using Node.js deployment
    set USE_DOCKER=false
)

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file from example...
    copy .env.example .env >nul
    echo ⚠️  Please edit .env file and add your RIOT_API_KEY before continuing
    echo    Get your key from: https://developer.riotgames.com/
    pause
)

REM Check if API key is set
findstr /C:"your-riot-api-key-here" .env >nul
if %errorlevel% == 0 (
    echo ❌ Please set your RIOT_API_KEY in .env file
    pause
    exit /b 1
)

echo ✅ Environment configuration found

if "%USE_DOCKER%"=="true" (
    echo 🐳 Starting with Docker...
    
    echo Choose deployment type:
    echo 1^) Development ^(app only^)
    echo 2^) Production ^(with nginx reverse proxy^)
    set /p DEPLOY_TYPE="Enter choice (1 or 2): "
    
    if "!DEPLOY_TYPE!"=="2" (
        echo 🚀 Starting production deployment...
        docker-compose --profile production up -d
        echo ✅ Application started!
        echo    Frontend: http://localhost ^(port 80^)
        echo    API: http://localhost:3001
    ) else (
        echo 🔧 Starting development deployment...
        docker-compose up -d
        echo ✅ Application started!
        echo    Frontend: http://localhost:3000
        echo    API: http://localhost:3001
    )
    
    echo.
    echo 📊 To view logs: docker-compose logs -f
    echo 🛑 To stop: docker-compose down
    
) else (
    echo 📦 Starting with Node.js...
    
    REM Check if Node.js is installed
    node --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Node.js not found. Please install Node.js 16+ and try again
        pause
        exit /b 1
    )
    
    for /f %%i in ('node --version') do echo ✅ Node.js found: %%i
    
    REM Install dependencies
    if not exist "node_modules" (
        echo 📦 Installing dependencies...
        npm install
    )
    
    if not exist "seneca\react-vite-app\node_modules" (
        echo 📦 Installing React app dependencies...
        cd "seneca\react-vite-app"
        npm install
        cd ..\..
    )
    
    REM Build React app
    echo 🔨 Building React app...
    cd "seneca\react-vite-app"
    npm run build
    cd ..\..
    
    echo 🚀 Starting services...
    
    REM Start proxy server in background
    echo Starting API proxy server...
    start "Proxy Server" node proxy-server.js
    
    REM Start React app server
    echo Starting React app...
    cd "seneca\react-vite-app"
    start "React App" npx serve -s dist -l 3000
    cd ..\..
    
    echo ✅ Application started!
    echo    Frontend: http://localhost:3000
    echo    API: http://localhost:3001
    echo.
    echo 🛑 Close the terminal windows to stop the services
)

echo.
echo 🎉 Setup complete! Visit the application in your browser.
pause