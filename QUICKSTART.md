# Quick Start - 5 Minutes to Teams Bot

## Prerequisites
- Azure account
- Your amplifier-app-api running
- 5 minutes

## Step 1: Register Bot (1 min)

```bash
az bot create \
  --resource-group amplifier-bot-rg \
  --name amplifier-teams-bot \
  --kind registration \
  --app-type MultiTenant \
  --endpoint https://placeholder.com/api/messages

# Get App ID
az bot show --resource-group amplifier-bot-rg --name amplifier-teams-bot --query appId -o tsv
```

Create password: Portal → Bot → Configuration → Manage → New client secret

## Step 2: Configure (1 min)

```bash
cp .env.example .env
# Edit .env with your values
```

## Step 3: Deploy (2 min)

```bash
./azure-deploy.sh
# Copy the output URL
```

Update bot endpoint in Azure Portal with the URL.

## Step 4: Upload to Teams (1 min)

```bash
./build-package.sh
```

Teams → Apps → Upload custom app → Select `amplifier-teams-bot.zip`

## Done! 🎉

Test: Open Amplifier in Teams and send "Hello!"

**Full guide**: See `SETUP.md` for detailed instructions.
