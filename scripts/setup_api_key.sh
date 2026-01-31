#!/bin/bash
# Setup script for Gemini API Key

set -e

echo "🔑 RestoPilotAI - Gemini API Key Setup"
echo "===================================="
echo ""

# Check if .env exists
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env already exists"
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
else
    echo "Creating backend/.env from template..."
    cp backend/.env.example backend/.env
fi

echo ""
echo "📝 Please enter your Gemini API Key"
echo "   Get one at: https://aistudio.google.com/apikey"
echo ""
read -p "API Key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Update .env file
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" backend/.env
else
    # Linux
    sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$api_key/" backend/.env
fi

echo ""
echo "✅ API key configured successfully!"
echo ""
echo "Next steps:"
echo "  1. Install dependencies: make setup"
echo "  2. Run the application: make run"
echo ""
