#!/bin/bash
set -e

echo "📦 Building Amplifier Teams Bot Package"
echo "========================================"
echo ""

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example and configure it first."
    exit 1
fi

# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Verify required variables
if [ -z "$TEAMS_APP_ID" ] || [ -z "$MICROSOFT_APP_ID" ]; then
    echo "❌ Missing required environment variables"
    echo "   Required: TEAMS_APP_ID, MICROSOFT_APP_ID"
    exit 1
fi

echo "Configuration:"
echo "  App ID: $TEAMS_APP_ID"
echo "  Bot ID: $MICROSOFT_APP_ID"
echo ""

# Create build directory
mkdir -p appPackage/build
cd appPackage/build

# Clean previous build
rm -f * 2>/dev/null || true

# Copy files
cp ../manifest.json .
cp ../icons/color.png .
cp ../icons/outline.png .

# Replace placeholders
sed -i "s/{{TEAMS_APP_ID}}/$TEAMS_APP_ID/g" manifest.json
sed -i "s/{{MICROSOFT_APP_ID}}/$MICROSOFT_APP_ID/g" manifest.json

# Validate JSON
echo "Validating manifest..."
python3 -m json.tool manifest.json > /dev/null && echo "  ✓ manifest.json is valid"

# Verify icons
test -f color.png && echo "  ✓ color.png exists"
test -f outline.png && echo "  ✓ outline.png exists"

# Create zip
echo ""
echo "Creating package..."
zip -q ../../amplifier-teams-bot.zip manifest.json color.png outline.png

cd ../..

echo ""
echo "✅ Package created: amplifier-teams-bot.zip"
unzip -l amplifier-teams-bot.zip
echo ""
echo "Ready to upload to Teams!"
