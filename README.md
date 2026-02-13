# Amplifier Teams Bot

**Direct chat integration with Amplifier** - Users chat with Amplifier directly in Teams, powered by your `amplifier-app-api` backend.

## Architecture

```
User in Teams → Teams Bot (this service) → amplifier-app-api
                     ↓
           Session Mapping Layer
           (Teams conversation ↔ Amplifier session)
```

**What this does:**
- Maps each Teams conversation to an Amplifier session
- Forwards user messages to your Amplifier API
- Returns Amplifier's responses to Teams
- Maintains conversation context across messages

## Quick Start

### 1. Register Azure Bot

First, create a bot registration in Azure:

```bash
# Login to Azure
az login

# Create resource group
az group create --name amplifier-bot-rg --location eastus

# Create bot registration
az bot create \
  --resource-group amplifier-bot-rg \
  --name amplifier-teams-bot \
  --kind registration \
  --app-type MultiTenant \
  --endpoint https://your-url-here/api/messages
```

**Save these values** - you'll need them for `.env`:
- **App ID**: From bot registration (MICROSOFT_APP_ID)
- **App Password**: Create in bot's Configuration → Manage Password (MICROSOFT_APP_PASSWORD)
- **App GUID**: The Teams App ID (TEAMS_APP_ID) - generate one at https://guidgenerator.com

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# Edit .env with your values
```

Required values:
```env
# From your amplifier-app-api
AMPLIFIER_API_URL=https://amplifier-api.gentlebay-e0c2022c.eastus.azurecontainerapps.io
AMPLIFIER_API_KEY=app_your_api_key_here
AMPLIFIER_BASE_CONFIG_ID=your-config-id
AMPLIFIER_BASE_CONFIG_NAME=chat-bundle

# From Azure Bot registration (step 1)
MICROSOFT_APP_ID=your-bot-app-id
MICROSOFT_APP_PASSWORD=your-bot-password
TEAMS_APP_ID=your-generated-guid

# Will be set after deployment
BOT_SERVICE_URL=https://your-deployed-url.azurecontainerapps.io
```

### 3. Install Dependencies

```bash
# Using pip
pip install -e .

# Or using uv (faster)
uv pip install -e .
```

### 4. Test Locally

```bash
# Run the bot
python run.py

# The bot will be available at http://localhost:3978
```

To test with Teams locally, you need a tunnel (ngrok, VS Code tunnel, etc.):

```bash
# Example with ngrok
ngrok http 3978

# Update bot endpoint in Azure Portal to:
# https://your-ngrok-url.ngrok.io/api/messages
```

### 5. Deploy to Azure

The easiest way is Azure Container Apps:

```bash
# Deploy (will build, push, and deploy)
./azure-deploy.sh

# This outputs your bot's messaging endpoint URL
# Update it in Azure Bot registration
```

**Manual deployment alternatives:**
- Azure App Service (see `docs/DEPLOY_APP_SERVICE.md`)
- Azure Container Instances
- Any hosting platform that supports Docker

### 6. Build and Upload Teams Package

```bash
# Build the app package
./build-package.sh

# This creates: amplifier-teams-bot.zip
```

**Upload to Teams:**
1. Go to Teams → Apps → Manage your apps
2. Click "Upload an app" → "Upload a custom app"
3. Select `amplifier-teams-bot.zip`
4. Install the bot

### 7. Test in Teams

1. Open the Amplifier bot in Teams
2. Send a message: "Hello, can you help me with Python?"
3. The bot will:
   - Create an Amplifier session
   - Forward your message
   - Return Amplifier's response

Each Teams conversation maintains its own Amplifier session for context.

## Project Structure

```
amplifier-extension-teams/
├── src/bot/
│   ├── main.py              # FastAPI app & webhook endpoint
│   ├── handlers.py          # Message handling logic
│   ├── amplifier_client.py  # Amplifier API client
│   ├── bot_adapter.py       # Teams Bot Framework client
│   ├── session_manager.py   # Conversation ↔ Session mapping
│   ├── models.py            # Data models
│   └── config.py            # Configuration
├── appPackage/
│   ├── manifest.json        # Teams app manifest
│   └── icons/               # App icons
├── run.py                   # Local development server
├── Dockerfile               # Container image
├── azure-deploy.sh          # Azure deployment script
└── build-package.sh         # Build Teams app package
```

## How It Works

### Session Mapping

Each Teams conversation gets its own Amplifier session:

```python
# First message in conversation
User: "Help me with async code"
  ↓
Bot creates new Amplifier session
  ↓
Maps: teams_conversation_123 → amplifier_session_xyz
  ↓
Forwards message to Amplifier
  ↓
Returns response to Teams

# Subsequent messages
User: "Show me an example"
  ↓
Bot finds existing mapping
  ↓
Uses same Amplifier session (preserves context)
  ↓
Forwards to Amplifier
  ↓
Returns response
```

### Message Flow

```
1. Teams sends activity to /api/messages
2. Bot parses Teams activity
3. Bot looks up/creates session mapping
4. Bot sends typing indicator (optional)
5. Bot forwards message to Amplifier API
6. Amplifier processes with full context
7. Bot receives response
8. Bot sends response back to Teams
```

### Session Lifecycle

- **Created**: First message in a Teams conversation
- **Active**: Messages within `SESSION_TIMEOUT_MINUTES` (default: 60)
- **Expired**: Cleaned up automatically after timeout
- **Metadata**: Each session tagged with Teams user/conversation IDs

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AMPLIFIER_API_URL` | Your Amplifier API base URL | Yes | - |
| `AMPLIFIER_API_KEY` | API key for authentication | Yes | - |
| `AMPLIFIER_BASE_CONFIG_ID` | Config ID for sessions | Yes | - |
| `AMPLIFIER_BASE_CONFIG_NAME` | Config name | No | `chat-bundle` |
| `MICROSOFT_APP_ID` | Bot app ID from Azure | Yes | - |
| `MICROSOFT_APP_PASSWORD` | Bot app password | Yes | - |
| `MICROSOFT_APP_TYPE` | Bot app type | No | `MultiTenant` |
| `BOT_SERVICE_URL` | Public bot URL | No | `http://localhost:3978` |
| `PORT` | Port to listen on | No | `3978` |
| `SESSION_TIMEOUT_MINUTES` | Session expiry time | No | `60` |
| `MAX_SESSIONS_PER_USER` | Max concurrent sessions | No | `10` |

### Bot Manifest

Edit `appPackage/manifest.json` to customize:
- Bot name and description
- Bot commands
- Supported scopes (personal, team, groupchat)
- Icons

## API Endpoints

### Webhook
- `POST /api/messages` - Teams Bot Framework webhook (handles all activities)

### Health & Status
- `GET /` - Health check + active session count
  ```bash
  curl https://your-bot-url/
  ```
- `GET /health` - Simple health status
  ```bash
  curl https://your-bot-url/health
  ```

### Session Management (for debugging)
- `GET /api/sessions` - List all active sessions
  ```bash
  curl https://your-bot-url/api/sessions
  ```
- `DELETE /api/sessions/{conversation_id}` - Delete a specific session
  ```bash
  curl -X DELETE https://your-bot-url/api/sessions/19:meeting_xyz
  ```

See [Testing the Deployment](#testing-the-deployment) for detailed testing examples.

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format
ruff format .

# Lint
ruff check .

# Type check (if using pyright)
pyright src/
```

### Local Development with Hot Reload

```bash
python run.py
# Changes to src/ will auto-reload
```

## Deployment

### Azure Container Apps (Recommended)

```bash
./azure-deploy.sh
```

**Pros:**
- Automatic scaling
- Easy deployment
- Built-in HTTPS
- Pay-per-use pricing

### Azure App Service

```bash
# Build image
docker build -t amplifier-teams-bot .

# Push to registry
az acr build --registry myregistry --image amplifier-teams-bot .

# Create App Service
az webapp create \
  --resource-group my-rg \
  --plan my-plan \
  --name amplifier-teams-bot \
  --deployment-container-image-name myregistry.azurecr.io/amplifier-teams-bot:latest
```

### Other Platforms

The bot is a standard Python FastAPI app. Deploy anywhere that supports:
- Python 3.11+
- Docker (optional)
- HTTPS endpoint (required by Teams)

## Testing the Deployment

After deploying, verify your bot is running correctly:

### Quick Health Check

```bash
# Check if bot is running
curl https://your-bot-url.azurecontainerapps.io/health

# Expected response:
# {"status":"healthy"}
```

### Detailed Status Check

```bash
# Get full status including active sessions
curl https://your-bot-url.azurecontainerapps.io/

# Expected response:
# {
#   "status": "running",
#   "service": "amplifier-teams-bot",
#   "version": "0.1.0",
#   "active_sessions": 0
# }
```

### Monitor Active Sessions

```bash
# List all active conversations
curl https://your-bot-url.azurecontainerapps.io/api/sessions

# Expected response:
# {
#   "total_sessions": 2,
#   "sessions": [
#     {
#       "conversation_id": "19:...",
#       "amplifier_session_id": "abc123",
#       "user_id": "29:...",
#       "message_count": 5,
#       "last_activity": "2026-02-13T15:30:00"
#     }
#   ]
# }
```

### Check Azure Container Logs

```bash
# Follow live logs
az containerapp logs show \
  --name amplifier-teams-bot \
  --resource-group amplifier-rg \
  --follow

# Get recent logs (last 50 lines)
az containerapp logs show \
  --name amplifier-teams-bot \
  --resource-group amplifier-rg \
  --tail 50 \
  --follow false
```

### Test with PowerShell (Windows)

```powershell
# Health check
Invoke-RestMethod -Uri "https://your-bot-url.azurecontainerapps.io/health"

# Get status
Invoke-RestMethod -Uri "https://your-bot-url.azurecontainerapps.io/" | ConvertTo-Json

# List sessions
Invoke-RestMethod -Uri "https://your-bot-url.azurecontainerapps.io/api/sessions" | ConvertTo-Json
```

### Testing the Teams Webhook

The `/api/messages` endpoint is the main webhook for Teams. It requires:
- Valid Teams Bot Framework activity JSON
- Proper authentication headers

**To test end-to-end:**
1. Install the bot in Teams (see step 6 above)
2. Send a message to the bot in Teams
3. Check logs to see the message processing
4. Monitor sessions endpoint to see active conversations

## Troubleshooting

### Bot not responding in Teams

**Check:**
1. Is the bot service running? (`GET /health` should return 200)
2. Is the messaging endpoint correct in Azure Bot registration?
3. Are the `MICROSOFT_APP_ID` and `MICROSOFT_APP_PASSWORD` correct?
4. Check bot logs for errors

### Authentication errors

**Error:** 401/403 from Bot Framework API

**Fix:**
- Verify `MICROSOFT_APP_ID` and `MICROSOFT_APP_PASSWORD` match Azure registration
- Check bot type is `MultiTenant` if using that configuration

### Amplifier API errors

**Error:** 500/401 from Amplifier API

**Fix:**
- Verify `AMPLIFIER_API_URL` is correct
- Check `AMPLIFIER_API_KEY` is valid
- Ensure `AMPLIFIER_BASE_CONFIG_ID` exists
- Check Amplifier API logs

### Session mapping issues

**Symptom:** Bot loses context between messages

**Fix:**
- Check session timeout isn't too short
- Verify session manager is running (check startup logs)
- Use `GET /api/sessions` to see active sessions

### Deployment issues

**Error:** Container fails to start

**Fix:**
- Check environment variables are set
- Verify dependencies installed (`pip install -e .`)
- Check logs: `az containerapp logs show -n amplifier-teams-bot -g my-rg`

## Contributing

This is a thin integration layer between Teams and Amplifier. Contributions welcome:

- Better error handling
- Session persistence (currently in-memory)
- Adaptive cards support
- File upload handling
- Conversation update handling

## License

MIT License - Same as Amplifier

## Support

- **Issues**: Create issue in the amplifier-extension-teams repo
- **Discussions**: Use GitHub Discussions
- **Amplifier Core**: See main [Amplifier repository](https://github.com/microsoft/amplifier)
