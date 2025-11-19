# Rekindle.ai System Workflow Diagram

## Visual Architecture Map

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React App<br/>Landing Page / Dashboard]
        Chat[AIAgentWidget<br/>Chat Interface]
        Voice[Web Speech API<br/>Voice Input]
    end

    subgraph "API Gateway"
        API[FastAPI Server<br/>JWT Auth, Rate Limiting]
        WS[WebSocket<br/>Agent Activity]
    end

    subgraph "REX Orchestrator"
        REX[REX Main<br/>execute_command]
        Parser[CommandParser<br/>Regex + Intent]
        Perms[PermissionsManager<br/>Login + Package]
        Exec[ActionExecutor<br/>Delegation + Retry]
        Agg[ResultAggregator<br/>Response Formatting]
    end

    subgraph "Sentience Engine"
        State[StateManager<br/>Persistent State]
        Intent[IntentEngine<br/>Goal Alignment]
        Persona[PersonaAdapter<br/>Tone Adjustment]
        Intro[IntrospectionLoop<br/>Self-Review]
        Heal[SelfHealingLogic<br/>Error Recovery]
    end

    subgraph "Orchestration Service"
        OS[OrchestrationService<br/>Crew Coordinator]
        FC[FullCampaignCrew<br/>18 Agents]
        DL[DeadLeadReactivationCrew<br/>9 Agents]
        ICP[AutoICPCrew<br/>4 Agents]
        MI[MasterIntelligenceAgent<br/>Director]
    end

    subgraph "Agent Categories"
        Intel[Intelligence Agents<br/>Research, ICP, Scoring, Sourcing]
        Content[Content Agents<br/>Writer, Subject, FollowUp, Objection, Engagement]
        Safety[Safety Agents<br/>Compliance, Quality, RateLimit]
        Sync[Sync Agents<br/>Tracker, Synchronizer]
        Revenue[Revenue Agents<br/>MeetingBooker, Billing]
        Opt[Optimization Agents<br/>ABTest, Domain, Calendar, Competitor, Personalization]
        Infra[Infrastructure Agents<br/>EmailWarmup, Nurturing, ChurnPrevention]
        Analytics[Analytics Agents<br/>Market, Performance]
    end

    subgraph "Communication Layer"
        Bus[AgentCommunicationBus<br/>Event Pub/Sub]
        Monitor[Monitoring System<br/>Metrics + Alerts]
        Log[Agent Logging<br/>Execution Tracking]
    end

    subgraph "Message Queue"
        Redis[(Redis Queue<br/>BullMQ)]
        Worker[Node Worker<br/>SendGrid/Twilio]
    end

    subgraph "External Services"
        OpenAI[OpenAI GPT-5.1<br/>Instant/Thinking]
        SendGrid[SendGrid<br/>Email]
        Twilio[Twilio<br/>SMS/WhatsApp]
        LinkedIn[LinkedIn MCP<br/>Research]
    end

    subgraph "Data Layer"
        Supabase[(Supabase PostgreSQL<br/>RLS Enabled)]
        Tables[Tables:<br/>leads, campaigns, messages<br/>chat_history, rex_state, profiles]
    end

    %% User Flow - Logged In
    UI -->|User Command| Chat
    Chat -->|POST /api/v1/agent/chat| API
    Voice -->|Transcription| Chat
    
    %% API to REX
    API -->|JWT Auth| REX
    API -->|Background Tasks| OS
    
    %% REX Flow
    REX -->|Parse| Parser
    REX -->|Check| Perms
    REX -->|Execute| Exec
    REX -->|Aggregate| Agg
    REX -->|Process| Sentience
    
    %% Sentience Components
    Sentience --> State
    Sentience --> Intent
    Sentience --> Persona
    Sentience --> Intro
    Sentience --> Heal
    
    %% Permissions Check
    Perms -->|Query| Supabase
    
    %% Execution Flow
    Exec -->|Delegate| OS
    Exec -->|Retry Logic| Heal
    
    %% Orchestration to Crews
    OS --> FC
    OS --> DL
    OS --> ICP
    OS --> MI
    
    %% Crews to Agents
    FC --> Intel
    FC --> Content
    FC --> Safety
    FC --> Sync
    FC --> Revenue
    FC --> Opt
    FC --> Infra
    FC --> Analytics
    
    DL --> Intel
    DL --> Content
    DL --> Safety
    DL --> Sync
    
    ICP --> Intel
    
    %% Agent Communication
    Intel --> Bus
    Content --> Bus
    Safety --> Bus
    Sync --> Bus
    Revenue --> Bus
    Opt --> Bus
    Infra --> Bus
    Analytics --> Bus
    
    Bus --> Monitor
    Bus --> Log
    
    %% Agents to External Services
    Intel --> OpenAI
    Intel --> LinkedIn
    Content --> OpenAI
    Safety --> OpenAI
    
    %% Message Queue Flow
    Content -->|Queue Messages| Redis
    Redis -->|Process Jobs| Worker
    Worker -->|Send| SendGrid
    Worker -->|Send| Twilio
    Worker -->|Update| Supabase
    
    %% Data Access
    REX -->|Query| Supabase
    OS -->|Query| Supabase
    Intel -->|Query| Supabase
    Content -->|Query| Supabase
    Safety -->|Query| Supabase
    Sync -->|Query| Supabase
    Revenue -->|Query| Supabase
    Opt -->|Query| Supabase
    Infra -->|Query| Supabase
    Analytics -->|Query| Supabase
    
    %% Response Flow
    Agg -->|Response| API
    API -->|JSON| Chat
    Chat -->|Display| UI
    
    %% WebSocket
    Monitor -->|Broadcast| WS
    WS -->|Real-time| Chat
    
    %% Styling
    classDef frontend fill:#e1f5ff
    classDef api fill:#fff4e1
    classDef rex fill:#ffe1f5
    classDef sentience fill:#f5e1ff
    classDef orchestration fill:#e1ffe1
    classDef agents fill:#ffe1e1
    classDef communication fill:#ffffe1
    classDef queue fill:#e1ffff
    classDef external fill:#f5f5f5
    classDef data fill:#e1e1ff
    
    class UI,Chat,Voice frontend
    class API,WS api
    class REX,Parser,Perms,Exec,Agg rex
    class State,Intent,Persona,Intro,Heal sentience
    class OS,FC,DL,ICP,MI orchestration
    class Intel,Content,Safety,Sync,Revenue,Opt,Infra,Analytics agents
    class Bus,Monitor,Log communication
    class Redis,Worker queue
    class OpenAI,SendGrid,Twilio,LinkedIn external
    class Supabase,Tables data
```

## Detailed Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Chat
    participant API
    participant REX
    participant Parser
    participant Perms
    participant Exec
    participant OS
    participant Crew
    participant Agent
    participant Queue
    participant Worker
    participant Agg
    participant Sentience
    participant DB

    User->>Chat: "Launch campaign"
    Chat->>API: POST /api/v1/agent/chat
    API->>DB: Load conversation history
    DB-->>API: History
    
    API->>REX: execute_command(message)
    
    REX->>Parser: parse(message)
    Parser-->>REX: {action: "launch_campaign", entities: {...}}
    
    REX->>Perms: check_user_state(user_id)
    Perms->>DB: Query user profile
    DB-->>Perms: {is_logged_in: true, package: "professional"}
    Perms-->>REX: {is_logged_in: true, package: "professional"}
    
    REX->>Perms: can_execute_action(user_id, "launch_campaign")
    Perms-->>REX: {allowed: true}
    
    REX->>Exec: execute(user_id, parsed_command)
    
    Exec->>OS: run_full_campaign(user_id, lead_ids)
    OS->>Crew: run_campaign_for_lead(lead_id)
    
    Crew->>Agent: score_lead(lead_id)
    Agent->>DB: Query lead data
    DB-->>Agent: Lead data
    Agent->>OpenAI: GPT-5.1 Thinking
    OpenAI-->>Agent: Score
    Agent-->>Crew: Score result
    
    Crew->>Agent: research_lead(lead_id)
    Agent->>LinkedIn: Research
    LinkedIn-->>Agent: Research data
    Agent-->>Crew: Research result
    
    Crew->>Agent: generate_sequence(lead_id)
    Agent->>OpenAI: GPT-5.1
    OpenAI-->>Agent: Messages
    Agent-->>Crew: Sequence
    
    Crew->>Agent: check_compliance(messages)
    Agent-->>Crew: Approved
    
    Crew->>Queue: Add message jobs
    Queue-->>Crew: Queued
    
    Crew-->>OS: {status: "campaign_started", messages_queued: 5}
    OS-->>Exec: Campaign result
    
    Worker->>Queue: Process job
    Queue-->>Worker: Message job
    Worker->>SendGrid: Send email
    SendGrid-->>Worker: Delivery status
    Worker->>DB: Update message status
    Worker-->>Queue: Job complete
    
    Exec-->>REX: {success: true, message: "Campaign launched."}
    
    REX->>Agg: aggregate(execution_result)
    Agg-->>REX: "Campaign launched."
    
    REX->>Sentience: process_response(draft, context)
    Sentience->>Persona: adapt(context)
    Persona-->>Sentience: {tone: "confident", warmth: 0.7}
    Sentience->>Intro: refine(draft)
    Intro->>OpenAI: GPT-5.1 Thinking (self-review)
    OpenAI-->>Intro: Refined response
    Intro-->>Sentience: Refined
    Sentience->>State: update("last_user_intent", action)
    State->>DB: Save state
    Sentience-->>REX: Refined response
    
    REX->>DB: Save conversation history
    REX-->>API: {response: "Campaign launched.", success: true}
    
    API->>DB: Save conversation
    API-->>Chat: JSON response
    Chat->>User: Display "Campaign launched."
```

## Permission & Package Flow

```mermaid
flowchart TD
    Start[User Sends Command] --> CheckAuth{User Logged In?}
    
    CheckAuth -->|No| GuestFlow[Guest Flow]
    GuestFlow --> ParseGuest[Parse Command]
    ParseGuest --> IsAction{Action Detected?}
    IsAction -->|Yes| RequireLogin[Return: 'Please log in to access this feature.']
    IsAction -->|No| Conversational[Return: Conversational response about Rekindle.ai]
    
    CheckAuth -->|Yes| LoggedInFlow[Logged-In Flow]
    LoggedInFlow --> GetPackage[Query User Package from DB]
    GetPackage --> PackageType{Package Type?}
    
    PackageType -->|free| FreeCheck{Action Allowed?}
    FreeCheck -->|No| UpgradeMessage[Return: 'This feature is not included in your package. Upgrade to access.']
    FreeCheck -->|Yes| Execute[Execute Action]
    
    PackageType -->|starter| StarterCheck{Action Allowed?}
    StarterCheck -->|No| UpgradeMessage
    StarterCheck -->|Yes| Execute
    
    PackageType -->|professional| ProCheck{Action Allowed?}
    ProCheck -->|No| UpgradeMessage
    ProCheck -->|Yes| Execute
    
    PackageType -->|enterprise| Execute
    
    Execute --> PermissionCheck[Check Permission]
    PermissionCheck --> Allowed{Allowed?}
    Allowed -->|No| UpgradeMessage
    Allowed -->|Yes| RunAction[Run Action via OrchestrationService]
    RunAction --> ReturnSuccess[Return: Action confirmation]
    
    RequireLogin --> End[End]
    Conversational --> End
    UpgradeMessage --> End
    ReturnSuccess --> End
```

## Multi-Channel Message Flow

```mermaid
flowchart LR
    Agent[Content Agent<br/>Generates Message] --> Queue[Redis Queue<br/>BullMQ]
    
    Queue --> Worker[Node Worker<br/>Concurrency: 10]
    
    Worker --> Channel{Channel Type?}
    
    Channel -->|email| SendGrid[SendGrid API<br/>Email Delivery]
    Channel -->|sms| TwilioSMS[Twilio API<br/>SMS Delivery]
    Channel -->|whatsapp| TwilioWA[Twilio API<br/>WhatsApp Delivery]
    Channel -->|push| PushService[Push Notification<br/>Service]
    Channel -->|voicemail| VoiceService[Voicemail<br/>Service]
    
    SendGrid --> Status1[Delivery Status]
    TwilioSMS --> Status2[Delivery Status]
    TwilioWA --> Status3[Delivery Status]
    PushService --> Status4[Delivery Status]
    VoiceService --> Status5[Delivery Status]
    
    Status1 --> DB[(Supabase<br/>Update Message Status)]
    Status2 --> DB
    Status3 --> DB
    Status4 --> DB
    Status5 --> DB
    
    DB --> Tracker[TrackerAgent<br/>Track Engagement]
    Tracker --> Analyzer[EngagementAnalyzerAgent<br/>Analyze Performance]
```

## Agent Communication Bus Flow

```mermaid
graph TB
    Agent1[Agent 1<br/>ResearcherAgent] -->|Broadcast| Bus[AgentCommunicationBus<br/>Event Pub/Sub]
    Agent2[Agent 2<br/>WriterAgent] -->|Broadcast| Bus
    Agent3[Agent 3<br/>ComplianceAgent] -->|Broadcast| Bus
    
    Bus -->|LEAD_RESEARCHED| Sub1[Subscriber 1<br/>WriterAgent]
    Bus -->|MESSAGE_GENERATED| Sub2[Subscriber 2<br/>ComplianceAgent]
    Bus -->|TRIGGER_DETECTED| Sub3[Subscriber 3<br/>DeadLeadReactivationAgent]
    
    Bus --> History[Event History<br/>Last 1000 Events]
    Bus --> Context[Shared Context<br/>Cross-Agent Memory]
    
    Bus --> Monitor[Monitoring System<br/>Track Events]
    Monitor --> Alerts[Alert on Errors<br/>Track Performance]
```

## State Persistence Flow

```mermaid
flowchart TD
    REX[REX Execution] --> Sentience[SentienceEngine]
    
    Sentience --> State[StateManager]
    
    State --> CheckDB{Database<br/>Available?}
    
    CheckDB -->|Yes| DB[(Supabase<br/>rex_state table)]
    CheckDB -->|No| File[Local JSON File<br/>rex_state_{user_id}.json]
    
    State --> Load[Load State]
    Load --> DB
    Load --> File
    
    State --> Update[Update State]
    Update --> Save[Save State]
    Save --> DB
    Save --> File
    
    State --> StateData[State Data:<br/>- mood<br/>- confidence<br/>- warmth<br/>- goals<br/>- interaction_count<br/>- success_rate]
    
    StateData --> Persona[PersonaAdapter<br/>Uses State]
    StateData --> Intent[IntentEngine<br/>Uses Goals]
```

---

## Legend

- **Blue (Frontend):** User-facing components
- **Yellow (API):** API gateway and WebSocket
- **Pink (REX):** Primary orchestrator components
- **Purple (Sentience):** Sentience engine modules
- **Green (Orchestration):** Crew coordination
- **Red (Agents):** Specialized agent categories
- **Light Yellow (Communication):** Inter-agent communication
- **Cyan (Queue):** Message queue system
- **Gray (External):** Third-party services
- **Light Blue (Data):** Database layer

---

*End of Diagram*

