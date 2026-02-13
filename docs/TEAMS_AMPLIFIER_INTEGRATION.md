# Microsoft Teams Extensibility Patterns & Amplifier Integration

**Author:** Analysis for Amplifier Teams integration  
**Date:** 2026-02-09  
**Status:** Design & Planning Phase

---

## Table of Contents

1. [Microsoft Teams Extensibility Patterns](#part-1-microsoft-teams-extensibility-patterns)
2. [Amplifier + Teams Integration Vision](#part-2-amplifier--teams-integration-vision)
3. [Implementation Roadmap](#part-3-implementation-roadmap)
4. [Key Design Decisions](#part-4-key-design-decisions)
5. [How to Build It](#part-5-how-to-build-it)
6. [Summary & Recommendations](#summary--recommendations)

---

## Part 1: Microsoft Teams Extensibility Patterns

Microsoft Teams provides several well-established extensibility patterns that both 1P (first-party) and 3P (third-party) developers follow to integrate their tools into Teams:

### 🤖 1. Bots (Conversational AI)

**What it is:** Conversational interfaces built on Azure Bot Framework that can participate in 1:1 chats, group chats, and channels.

**Key capabilities:**
- Send/receive messages with rich formatting
- Proactive messaging (notifications)
- Adaptive Cards for interactive UI
- Integration with Bot Framework SDK (C#, Node.js, Python)

**Examples:** ChatGPT bot, GitHub bot, Polly (polls), service desk bots

**Pattern for others:** Any service that benefits from conversational interaction can be a bot. Bot Framework provides the infrastructure; you focus on conversation logic.

---

### 💬 2. Message Extensions

**What it is:** Commands accessible from the compose box or command bar that search external systems or trigger actions.

**Two implementation approaches:**
- **API-based:** Simpler, requires only an OpenAPI spec describing your API
- **Bot-based:** More flexible, built on Bot Framework for complex logic

**Types:**
- **Search commands:** Query external systems (e.g., "search Jira tickets")
- **Action commands:** Trigger workflows (e.g., "create incident")
- **Link unfurling:** Expand URLs into rich previews automatically

**Examples:** Jira search, GitHub issue creation, ServiceNow ticket lookup

**Pattern for others:** If your tool has search/action capabilities users need during conversations, build a message extension. API-based is the modern, low-code path.

---

### 📑 3. Tabs (Embedded Web Experiences)

**What it is:** Full web applications embedded directly in Teams.

**Types:**
- **Personal tabs:** User's private workspace (dashboards, settings)
- **Channel/Group tabs:** Shared team workspaces
- **Meeting tabs:** Context available during meetings

**Examples:** Planner boards, Power BI dashboards, Miro whiteboards, custom LOB apps

**Pattern for others:** If you have an existing web app, wrap it as a Teams tab for seamless in-context access. Teams provides SSO, theming, and context APIs.

---

### 🔔 4. Webhooks & Connectors

**What it is:** Simple HTTP-based integration for sending/receiving notifications.

**Types:**
- **Incoming webhooks:** External systems POST to Teams (super simple)
- **Outgoing webhooks:** Teams POSTs to your service when @mentioned
- **Office 365 Connectors:** Richer notification cards with actions

**Examples:** Azure DevOps pipelines, GitHub commits, monitoring alerts

**Pattern for others:** Fastest path to Teams integration. No auth complexity, just POST JSON to a webhook URL.

---

### 🧠 5. Declarative Agents (New!)

**What it is:** The future of Microsoft 365 Copilot extensibility. Define agents using JSON manifests with:
- Instructions (system prompts)
- Actions (APIs to call)
- Knowledge (RAG over documents/Graph Connectors)

**Key insight:** No code required for basic agents. Natural language instructions + API specs = functional agent.

**Examples:** Custom Copilot agents for HR policies, IT helpdesk, sales intelligence

**Pattern for others:** If you're building AI-powered assistants, declarative agents are Microsoft's recommended path. They work across Teams, Outlook, M365 Chat.

---

### 🎴 6. Adaptive Cards

**What it is:** Cross-platform UI framework for rich, interactive cards (JSON-based).

**Capabilities:**
- Rich formatting (images, tables, lists)
- Input controls (text, dropdowns, date pickers)
- Actions (buttons that POST back to your service)
- Refresh on user action

**Used by:** Bots, message extensions, webhooks, connectors

**Pattern for others:** Don't send plain text when you can send structured data. Adaptive Cards are the lingua franca of Teams UI.

---

## Part 2: Amplifier + Teams Integration Vision

Given Amplifier's architecture and Teams' patterns, here's how we envision the integration:

### 🎯 The Core Value Proposition

**"Amplifier in Teams = AI-powered development assistant where your team already collaborates"**

- Developers ask Amplifier questions in Teams chat
- Amplifier executes code, runs agents, generates documentation
- Results appear as rich Adaptive Cards
- Session history accessible via personal tab
- Recipes shareable via message extensions

---

### 🏗️ Proposed Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Microsoft Teams Client                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Bot Chat   │  │   Message    │  │  Personal    │  │
│  │              │  │  Extensions  │  │     Tab      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
└─────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │
          │ Bot Framework    │ Bot Framework    │ HTTPS
          │ Activity         │ Invoke           │ REST API
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│  Amplifier Teams Service (Python)                       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Bot Framework Adapter (Python SDK)            │    │
│  │  - Handles Teams activity protocol             │    │
│  │  - Authentication (SSO, Azure AD)              │    │
│  │  - Adaptive Card rendering                     │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                     │
│  ┌────────────────▼───────────────────────────────┐    │
│  │  Teams Integration Layer                       │    │
│  │  - Message routing & session management        │    │
│  │  - Teams context enrichment (user, channel)    │    │
│  │  - Conversation state tracking                 │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                     │
│  ┌────────────────▼───────────────────────────────┐    │
│  │  Amplifier Core API Client                     │    │
│  │  (amplifier-app-api REST client)               │    │
│  │  - Session management                          │    │
│  │  - Message execution                           │    │
│  │  - Recipe invocation                           │    │
│  │  - Agent delegation                            │    │
│  └────────────────┬───────────────────────────────┘    │
└───────────────────┼─────────────────────────────────────┘
                    │ HTTPS REST
                    ▼
┌─────────────────────────────────────────────────────────┐
│  amplifier-app-api Service                              │
│  - Runs Amplifier sessions                              │
│  - Manages bundles, agents, recipes                     │
│  - Executes tools (filesystem, bash, web, etc.)         │
└─────────────────────────────────────────────────────────┘
```

---

### 🔧 Component Breakdown

#### 1. Bot (Primary Interface)

**User experience:**
```
User: "@Amplifier explain async/await in Python"
Bot:  [Adaptive Card with explanation + code examples]

User: "@Amplifier create a FastAPI todo app"
Bot:  [Thinking indicator]
      [Adaptive Card showing file tree + code snippets]
      "I've created 3 files. Review the implementation ↓"
      [Buttons: "Show Full Code" | "Run Tests" | "Save to GitHub"]
```

**Technical implementation:**
- Python Bot Framework SDK (`botbuilder` package)
- Handles incoming messages → creates/resumes Amplifier sessions
- Streams responses back as Adaptive Cards
- Maintains conversation state (session IDs per user/channel)

---

#### 2. Message Extensions

**A. Search Command: "Ask an Agent"**
```
User types in compose box: "@Amplifier-search what's the bug in this code?"
→ Quick search through available agents
→ Select "foundation:bug-hunter"
→ Result inserted as card in conversation
```

**B. Action Command: "Run Recipe"**
```
User clicks "..." in compose box → Amplifier → Run Recipe
→ Modal dialog: Select recipe (dropdown)
→ Fill context variables (form)
→ Execute → Result posted to channel as card
```

**C. Link Unfurling**
```
User pastes: "https://github.com/microsoft/amplifier/issues/123"
→ Amplifier bot detects GitHub URL
→ Fetches issue details via amplifier-app-api
→ Unfurls as rich card with status, labels, assignees
```

---

#### 3. Personal Tab: "Amplifier Dashboard"

**Features:**
- **Session History:** Browse past conversations, resume sessions
- **Recipe Library:** Discover and execute recipes
- **Agent Directory:** Browse available agents with descriptions
- **Settings:** Configure default bundles, API keys (if self-hosted)

**Implementation:**
- React SPA hosted separately (or within Teams service)
- Calls amplifier-app-api REST endpoints
- Teams SSO for authentication
- Deep links back to bot conversations

---

#### 4. Teams-Specific Tools

New Amplifier tools that only work in Teams context:

**`teams-context` tool:**
```python
# Provides conversation context to agents
{
  "channel": {"id": "...", "name": "engineering-general"},
  "team": {"id": "...", "name": "Platform Team"},
  "user": {"id": "...", "name": "Mark Licata", "email": "..."},
  "message_id": "...",  # For threading
}
```

**`teams-post` tool:**
```python
# Agent can post messages to channels
teams.post(
    channel_id="...",
    message="Build completed successfully!",
    card=adaptive_card_json
)
```

**`teams-files` tool:**
```python
# Access files from Teams/SharePoint
teams.files.read("Shared Documents/spec.md")
teams.files.write("Shared Documents/output.py", content)
```

---

### 📦 Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Bot Service** | Python 3.11+ | Matches Amplifier core language |
| **Bot Framework** | `botbuilder-python` SDK | Official Microsoft Teams bot SDK |
| **Web Framework** | FastAPI | Modern async Python, same as amplifier-app-api |
| **Amplifier Client** | `httpx` + `amplifier-app-api` | REST client for Amplifier backend |
| **Card Rendering** | Adaptive Cards SDK | Rich UI without custom components |
| **State Management** | Azure Table Storage or Redis | Bot conversation state persistence |
| **Authentication** | Azure AD SSO | Seamless Teams identity integration |
| **Hosting** | Azure App Service or Container Apps | Native Azure integration |
| **Tab Frontend** | React + Fluent UI | Official Microsoft Teams design system |

---

## Part 3: Implementation Roadmap

### Phase 1: Minimal Viable Bot (Week 1-2)

**Goal:** Get a basic conversational bot working in Teams

**Deliverables:**
- [ ] Bot registration in Azure
- [ ] Python Bot Framework service running
- [ ] Handle basic messages: User → Bot → amplifier-app-api → Response
- [ ] Plain text responses (no cards yet)
- [ ] Deploy to Azure App Service

**Success metric:** User can ask "@Amplifier what is Python asyncio?" and get an answer

---

### Phase 2: Rich Responses with Adaptive Cards (Week 3-4)

**Goal:** Make responses beautiful and actionable

**Deliverables:**
- [ ] Adaptive Card templates for:
  - Code explanations (syntax highlighting)
  - File trees and diffs
  - Agent delegation results
  - Error messages with suggested fixes
- [ ] Action buttons: "Show More", "Run This", "Save to Files"
- [ ] Typing indicators and streaming (progressive card updates)

**Success metric:** Responses look professional and users can take actions directly from cards

---

### Phase 3: Message Extensions (Week 5-6)

**Goal:** Enable quick access without starting a bot conversation

**Deliverables:**
- [ ] Search extension: Find and insert agent responses
- [ ] Action extension: Run recipes from compose box
- [ ] Link unfurling for GitHub, StackOverflow (via web-research agent)

**Success metric:** Users can run recipes without leaving their current conversation

---

### Phase 4: Personal Tab Dashboard (Week 7-8)

**Goal:** Provide a dedicated workspace for power users

**Deliverables:**
- [ ] React SPA with Fluent UI components
- [ ] Session history browser (filter, search, resume)
- [ ] Recipe library with favorites
- [ ] Agent directory with inline docs

**Success metric:** Users can manage their Amplifier work history and discover capabilities

---

### Phase 5: Teams-Specific Enhancements (Week 9-10)

**Goal:** Make Amplifier "Teams-native"

**Deliverables:**
- [ ] `teams-context` tool (inject channel/user info into sessions)
- [ ] `teams-post` tool (agents can post to channels)
- [ ] `teams-files` tool (read/write SharePoint files)
- [ ] Shared team recipes (channel-scoped)
- [ ] @mention support in code comments ("@Amplifier review this function")

**Success metric:** Amplifier feels like a first-class Teams citizen, not a bolt-on

---

## Part 4: Key Design Decisions

### 1. Session Management Strategy

**Option A: One session per user globally**
- ✅ Pros: Simple, continuity across conversations
- ❌ Cons: Context bleed between unrelated questions

**Option B: One session per Teams conversation**
- ✅ Pros: Context isolation, team-shared sessions in channels
- ❌ Cons: More complex state management

**Recommendation:** **Option B** - Maps cleanly to Teams' conversation model. Channel sessions enable team collaboration.

---

### 2. amplifier-app-api Integration

**Given that amplifier-app-api exists (marklicata/amplifier-app-api):**

**Architecture:**
```
Teams Bot Service → (REST) → amplifier-app-api → Amplifier Core
```

**Benefits:**
- Clean separation: Bot handles Teams protocol, API handles Amplifier logic
- amplifier-app-api can serve multiple frontends (Teams, CLI, web)
- Independent scaling and deployment

**API Design:**
```python
# Create/resume session
POST /sessions
GET  /sessions/{session_id}

# Execute message
POST /sessions/{session_id}/messages
{
  "content": "Explain asyncio",
  "context": {"teams": {...}}  # Teams-specific enrichment
}

# Stream response (SSE or WebSocket)
GET /sessions/{session_id}/stream

# Recipes
GET  /recipes
POST /recipes/{recipe_id}/execute

# Agents
GET  /agents
POST /agents/{agent_id}/invoke
```

---

### 3. Adaptive Card Strategy

**Template-driven approach:**
```python
# Card templates stored as Jinja2 templates
templates/
  code_explanation.json
  file_tree.json
  agent_result.json
  error_message.json

# Renderer
def render_card(template_name: str, data: dict) -> dict:
    template = env.get_template(f"{template_name}.json")
    return json.loads(template.render(**data))
```

**Example - Code Explanation Card:**
```json
{
  "type": "AdaptiveCard",
  "body": [
    {
      "type": "TextBlock",
      "text": "{{ title }}",
      "size": "large",
      "weight": "bolder"
    },
    {
      "type": "TextBlock",
      "text": "{{ explanation }}",
      "wrap": true
    },
    {
      "type": "Container",
      "items": [
        {
          "type": "TextBlock",
          "text": "```python\n{{ code }}\n```",
          "fontType": "monospace"
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.Submit",
      "title": "Run This Code",
      "data": {"action": "execute", "code": "{{ code }}"}
    }
  ]
}
```

---

### 4. Security & Permissions

**Key considerations:**
1. **Authentication:** Azure AD SSO from Teams → validate tokens in bot service
2. **Authorization:** User-scoped API keys for amplifier-app-api (if needed)
3. **Sandboxing:** Tool execution should respect Teams org policies
4. **Secrets:** Never expose API keys in Adaptive Cards or logs
5. **File Access:** Respect SharePoint permissions when using `teams-files` tool

**Implementation:**
- Bot validates Azure AD tokens on every request
- amplifier-app-api runs with user identity context
- Tools check permissions before execution (e.g., can user access this file?)

---

## Part 5: How to Build It

### Step-by-Step Guide

#### Step 1: Set Up Azure Resources

```bash
# Create resource group
az group create --name amplifier-teams-rg --location eastus

# Create Bot Channels Registration
az bot create \
  --name amplifier-bot \
  --resource-group amplifier-teams-rg \
  --kind registration \
  --sku F0 \
  --appid <app-id> \
  --password <app-secret>

# Create App Service for hosting
az appservice plan create \
  --name amplifier-plan \
  --resource-group amplifier-teams-rg \
  --sku B1 \
  --is-linux

az webapp create \
  --name amplifier-teams-service \
  --resource-group amplifier-teams-rg \
  --plan amplifier-plan \
  --runtime "PYTHON:3.11"
```

---

#### Step 2: Create Bot Project

```bash
# Project structure
amplifier-teams-bot/
├── bot/
│   ├── __init__.py
│   ├── adapter.py          # Bot Framework adapter
│   ├── bot.py              # Main bot logic
│   ├── cards.py            # Adaptive Card templates
│   └── amplifier_client.py # REST client for amplifier-app-api
├── api/
│   ├── __init__.py
│   └── main.py             # FastAPI app
├── config/
│   └── settings.py
├── templates/
│   └── cards/              # Adaptive Card JSON templates
├── requirements.txt
├── Dockerfile
└── app.yaml                # Teams app manifest
```

**Install dependencies:**
```bash
pip install \
  botbuilder-core \
  botbuilder-schema \
  fastapi \
  uvicorn \
  httpx \
  jinja2 \
  azure-identity
```

---

#### Step 3: Implement Core Bot Logic

**`bot/bot.py`:**
```python
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from .amplifier_client import AmplifierClient
from .cards import render_card

class AmplifierBot(ActivityHandler):
    def __init__(self, amplifier_client: AmplifierClient):
        self.client = amplifier_client
    
    async def on_message_activity(self, turn_context: TurnContext):
        # Get user message
        user_message = turn_context.activity.text
        
        # Get or create session for this conversation
        conversation_id = turn_context.activity.conversation.id
        session = await self.client.get_or_create_session(conversation_id)
        
        # Send typing indicator
        await turn_context.send_activity(Activity(type=ActivityTypes.typing))
        
        # Execute in Amplifier
        response = await self.client.execute_message(
            session_id=session.id,
            message=user_message,
            context={
                "teams": {
                    "user": turn_context.activity.from_property.name,
                    "channel": turn_context.activity.channel_id,
                }
            }
        )
        
        # Render as Adaptive Card
        card = render_card("agent_response", {
            "content": response.content,
            "session_id": session.id
        })
        
        # Send response
        await turn_context.send_activity(Activity(
            type=ActivityTypes.message,
            attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            }]
        ))
```

**`bot/amplifier_client.py`:**
```python
import httpx
from typing import Optional

class AmplifierClient:
    def __init__(self, api_base_url: str):
        self.base_url = api_base_url
        self.client = httpx.AsyncClient()
    
    async def get_or_create_session(self, conversation_id: str) -> dict:
        """Get existing session or create new one for conversation."""
        response = await self.client.post(
            f"{self.base_url}/sessions",
            json={"conversation_id": conversation_id}
        )
        return response.json()
    
    async def execute_message(
        self, 
        session_id: str, 
        message: str,
        context: Optional[dict] = None
    ) -> dict:
        """Execute a message in an Amplifier session."""
        response = await self.client.post(
            f"{self.base_url}/sessions/{session_id}/messages",
            json={
                "content": message,
                "context": context or {}
            }
        )
        return response.json()
```

---

#### Step 4: Create Teams App Manifest

**`app.yaml` (Teams manifest):**
```yaml
$schema: https://developer.microsoft.com/en-us/json-schemas/teams/v1.16/MicrosoftTeams.schema.json
manifestVersion: "1.16"
version: "1.0.0"
id: "<your-app-id>"
packageName: "com.microsoft.amplifier"
developer:
  name: "Microsoft"
  websiteUrl: "https://github.com/microsoft/amplifier"
  privacyUrl: "https://privacy.microsoft.com"
  termsOfUseUrl: "https://www.microsoft.com/en-us/legal/terms-of-use"

name:
  short: "Amplifier"
  full: "Amplifier AI Development Assistant"

description:
  short: "AI-powered development assistant in Teams"
  full: "Amplifier brings AI-powered development capabilities directly into Teams. Ask questions, generate code, run agents, and execute recipes without leaving your conversation."

icons:
  outline: "outline-icon.png"
  color: "color-icon.png"

accentColor: "#0078D4"

bots:
  - botId: "<your-bot-id>"
    scopes:
      - personal
      - team
      - groupchat
    commandLists:
      - scopes:
          - personal
          - team
          - groupchat
        commands:
          - title: "Explain code"
            description: "Ask Amplifier to explain code or concepts"
          - title: "Generate code"
            description: "Generate code from natural language"
          - title: "Run recipe"
            description: "Execute an Amplifier recipe"

messagingExtensions:
  - botId: "<your-bot-id>"
    canUpdateConfiguration: false
    commands:
      - id: "runRecipe"
        type: "action"
        title: "Run Recipe"
        description: "Execute an Amplifier recipe"
        initialRun: false
        fetchTask: true
        context:
          - compose
          - commandBox
      
      - id: "askAgent"
        type: "query"
        title: "Ask Agent"
        description: "Query an Amplifier agent"
        initialRun: true
        parameters:
          - name: "query"
            title: "Question"
            description: "What do you want to ask?"

staticTabs:
  - entityId: "dashboard"
    name: "Dashboard"
    contentUrl: "https://<your-domain>/dashboard"
    scopes:
      - personal

permissions:
  - identity
  - messageTeamMembers

validDomains:
  - "<your-domain>"
```

---

#### Step 5: Deploy and Test

```bash
# Build and deploy bot service
az webapp deployment source config-zip \
  --resource-group amplifier-teams-rg \
  --name amplifier-teams-service \
  --src amplifier-teams-bot.zip

# Upload Teams app manifest to Teams Admin Center
# or sideload for development

# Test in Teams
# 1. Install app
# 2. Start chat with Amplifier bot
# 3. Send message: "Explain Python async/await"
```

---

## Summary & Recommendations

### What Teams Offers

- **Mature extensibility patterns** (bots, tabs, message extensions)
- **Bot Framework SDK** for conversational AI
- **Adaptive Cards** for rich, interactive UI
- **Declarative agents** for future Copilot integration
- **320M+ MAU** built-in distribution

### How Amplifier Fits

- **Bot** = Primary conversational interface
- **Message Extensions** = Quick recipe/agent access
- **Personal Tab** = Session management dashboard
- **Teams-specific tools** = Native integration (files, posts, context)
- **amplifier-app-api** = Backend service layer

### Build Path

1. ✅ Start with basic bot (Week 1-2)
2. ✅ Add Adaptive Cards (Week 3-4)
3. ✅ Implement message extensions (Week 5-6)
4. ✅ Build personal tab (Week 7-8)
5. ✅ Teams-native enhancements (Week 9-10)

### Why This Will Work

- Leverages existing Teams patterns (proven by thousands of apps)
- amplifier-app-api provides clean architecture boundary
- Python Bot Framework SDK is mature and well-documented
- Adaptive Cards make results beautiful without custom UI
- Phased approach delivers value incrementally

---

## Open Questions for Discussion

1. **Session Scoping:** Do we want separate sessions per conversation, or user-global sessions with conversation context?
2. **Tool Execution Security:** How do we sandbox tool execution when running from Teams (especially `bash` and `filesystem` tools)?
3. **API Hosting:** Should amplifier-app-api run as a shared service or per-tenant deployment?
4. **Cost Model:** Free tier limits? Premium features?
5. **Teams vs. Copilot:** Start with standalone Teams bot or go straight to declarative agent for M365 Copilot?

---

## Next Steps

- [ ] Review and refine this design document
- [ ] Get buy-in from stakeholders
- [ ] Set up dev environment and Azure resources
- [ ] Implement Phase 1 MVP
- [ ] User testing and iteration

**Ready to start building?** Let's discuss the open questions and refine the approach before diving into implementation.
