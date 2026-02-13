# Setup Guide - Amplifier Teams Bot

Complete step-by-step setup instructions.

## Prerequisites

- Python 3.11 or higher
- Azure account with active subscription
- Azure CLI installed (`az --version`)
- Your `amplifier-app-api` already deployed and accessible

## Step 1: Azure Bot Registration

### 1.1 Create Bot Registration

```bash
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "Your Subscription Name"

# Create resource group
az group create \
  --name amplifier-bot-rg \
  --location eastus

# Create bot registration
az bot create \
  --resource-group amplifier-bot-rg \
  --name amplifier-teams-bot \
  --kind registration \
  --app-type MultiTenant \
  --endpoint https://placeholder.com/api/messages
```

**Note:** We use a placeholder endpoint for now. We'll update it after deployment.

### 1.2 Get Bot Credentials

```bash
# Get the App ID
az bot show --resource-group amplifier-bot-rg --name amplifier-teams-bot --query appId -o tsv
```

Save this as your `MICROSOFT_APP_ID`.

### 1.3 Create App Password

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your bot: **Azure Bot Service** → **amplifier-teams-bot**
3. Go to **Configuration**
4. Click **Manage** next to Microsoft App ID
5. Go to **Certificates & secrets**
6. Click **New client secret**
7. Description: "Amplifier Teams Bot"
8. Expires: Choose your preference (recommend: 24 months)
9. Click **Add**
10. **Copy the secret VALUE immediately** (you won't see it again)

Save this as your `MICROSOFT_APP_PASSWORD`.

### 1.4 Enable Teams Channel

1. In Azure Portal, go to your bot
2. Go to **Channels**
3. Click **Teams** icon
4. Click **Apply**
5. Teams channel is now enabled

## Step 2: Local Configuration

### 2.1 Clone/Navigate to Project

```bash
cd /path/to/amplifier-extension-teams
```

### 2.2 Create Environment File

```bash
cp .env.example .env
```

### 2.3 Edit `.env` File

Open `.env` and fill in these values:

```env
# From your amplifier-app-api (you already have these)
AMPLIFIER_API_URL=https://amplifier-api.gentlebay-e0c2022c.eastus.azurecontainerapps.io
AMPLIFIER_API_KEY=app_OdblJ9aIEVblgwd40W_4NjNypLHRaFj7OZ4kCCYXdl8
AMPLIFIER_BASE_CONFIG_ID=eca3c4c5-0852-46e8-b52c-7aecc847db28
AMPLIFIER_BASE_CONFIG_NAME=chat-bundle

# From Azure Bot registration (Step 1)
MICROSOFT_APP_ID=<paste your app ID here>
MICROSOFT_APP_PASSWORD=<paste your app password here>

# Generate a new GUID for Teams app
# Use: https://guidgenerator.com or `uuidgen` command
TEAMS_APP_ID=<paste a new GUID here>

# These will be updated after deployment
BOT_SERVICE_URL=http://localhost:3978
PORT=3978
```

### 2.4 Generate Teams App ID

**Option 1:** Online
- Go to https://guidgenerator.com
- Copy the GUID (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

**Option 2:** Command line (Linux/Mac)
```bash
uuidgen
```

**Option 3:** PowerShell (Windows)
```powershell
[guid]::NewGuid().ToString()
```

Paste this as your `TEAMS_APP_ID`.

## Step 3: Install and Test Locally

### 3.1 Install Dependencies

```bash
# Using pip
pip install -e .

# Or using uv (faster, recommended)
uv pip install -e .
```

### 3.2 Test the Bot Locally

```bash
python run.py
```

You should see:
```
Starting Amplifier Teams Bot...
Amplifier API: https://amplifier-api.gentlebay-e0c2022c.eastus.azurecontainerapps.io
Bot Service URL: http://localhost:3978
INFO:     Uvicorn running on http://0.0.0.0:3978
```

### 3.3 Test Health Check

In another terminal:
```bash
curl http://localhost:3978/health
```

Should return: `{"status":"healthy"}`

## Step 4: Deploy to Azure

### 4.1 Run Deployment Script

```bash
./azure-deploy.sh
```

This will:
- Create Azure Container Registry
- Build Docker image
- Deploy to Azure Container Apps
- Output your bot's public URL

**Save the output!** It will look like:
```
Bot Messaging Endpoint: https://amplifier-teams-bot--xxxxx.eastus.azurecontainerapps.io/api/messages
```

### 4.2 Update `.env` with Deployment URL

Edit `.env` and update:
```env
BOT_SERVICE_URL=https://amplifier-teams-bot--xxxxx.eastus.azurecontainerapps.io
```

### 4.3 Update Bot Registration Endpoint

**Option 1: Azure Portal**
1. Go to your bot in Azure Portal
2. Go to **Configuration**
3. Update **Messaging endpoint** to your deployed URL (with `/api/messages`)
4. Click **Apply**

**Option 2: Azure CLI**
```bash
az bot update \
  --resource-group amplifier-bot-rg \
  --name amplifier-teams-bot \
  --endpoint "https://amplifier-teams-bot--xxxxx.eastus.azurecontainerapps.io/api/messages"
```

## Step 5: Create Teams App Package

### 5.1 Build Package

```bash
./build-package.sh
```

This creates: `amplifier-teams-bot.zip`

### 5.2 Validate Package

```bash
unzip -l amplifier-teams-bot.zip
```

Should show:
```
Archive:  amplifier-teams-bot.zip
  manifest.json
  color.png
  outline.png
```

## Step 6: Upload to Teams

### 6.1 Upload Custom App

1. Open **Microsoft Teams**
2. Click **Apps** in the left sidebar
3. Click **Manage your apps** (bottom left)
4. Click **Upload an app** → **Upload a custom app**
5. Select `amplifier-teams-bot.zip`
6. Click **Add** to install for yourself

### 6.2 Optional: Upload to Organization

If you're an admin and want to share with your organization:

1. Go to [Teams Admin Center](https://admin.teams.microsoft.com)
2. Navigate to **Teams apps** → **Manage apps**
3. Click **Upload new app**
4. Upload `amplifier-teams-bot.zip`
5. Configure availability policies as needed

## Step 7: Test the Bot

### 7.1 Start a Chat

1. In Teams, find "Amplifier" in your apps
2. Click to open
3. Send a message: **"Hello, can you help me with Python?"**

### 7.2 Expected Behavior

You should see:
1. Your message appears
2. Bot shows "typing..." indicator
3. Amplifier's response appears

**First message** creates a new Amplifier session.  
**Follow-up messages** use the same session (preserves context).

### 7.3 Test Context Preservation

```
You: "What is async/await in Python?"
Bot: [explains async/await]

You: "Show me an example"
Bot: [provides example, remembering the previous context]
```

## Step 8: Monitoring and Debugging

### 8.1 View Active Sessions

```bash
curl https://your-bot-url.azurecontainerapps.io/api/sessions
```

Shows all active Teams ↔ Amplifier session mappings.

### 8.2 View Logs

```bash
# Container Apps logs
az containerapp logs show \
  --name amplifier-teams-bot \
  --resource-group amplifier-bot-rg \
  --follow

# Bot registration logs
az bot show \
  --resource-group amplifier-bot-rg \
  --name amplifier-teams-bot
```

### 8.3 Test Messaging Endpoint

```bash
# Health check
curl https://your-bot-url.azurecontainerapps.io/health

# Active sessions
curl https://your-bot-url.azurecontainerapps.io/api/sessions
```

## Troubleshooting

### Issue: Bot doesn't respond

**Check:**
```bash
# 1. Is service running?
curl https://your-bot-url.azurecontainerapps.io/health

# 2. Are credentials correct?
echo $MICROSOFT_APP_ID
echo $MICROSOFT_APP_PASSWORD  # Should not be empty

# 3. Is endpoint registered?
az bot show --resource-group amplifier-bot-rg --name amplifier-teams-bot --query "properties.endpoint"
```

### Issue: "Authentication failed"

**Fix:**
1. Verify `MICROSOFT_APP_ID` matches Azure bot registration
2. Regenerate `MICROSOFT_APP_PASSWORD` if unsure
3. Redeploy with correct credentials

### Issue: "Amplifier API error"

**Check:**
```bash
# Test API directly
curl -H "X-API-Key: $AMPLIFIER_API_KEY" \
  $AMPLIFIER_API_URL/configs/$AMPLIFIER_BASE_CONFIG_ID
```

If this fails, check your Amplifier API configuration.

### Issue: Package upload fails

**Fix:**
1. Validate manifest: `python3 -m json.tool appPackage/build/manifest.json`
2. Check file size: `du -h amplifier-teams-bot.zip` (should be < 10MB)
3. Ensure icons exist: `ls appPackage/icons/`

## Next Steps

✅ **Your bot is ready!**

**Optional enhancements:**
- [ ] Add adaptive cards for rich responses
- [ ] Implement file upload handling
- [ ] Add session persistence (database)
- [ ] Set up Application Insights monitoring
- [ ] Create CI/CD pipeline for auto-deployment

## Getting Help

- **Bot issues**: Check Azure Bot Service logs in portal
- **Deployment issues**: Check Container Apps logs
- **Amplifier issues**: Check amplifier-app-api logs
- **Teams issues**: Check Teams admin center

**Still stuck?** Create an issue in the repository with:
- Error messages
- Bot logs
- Steps to reproduce
