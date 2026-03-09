# AI Sahayak - Architecture Diagrams

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph Users["👥 Users"]
        Retailer[Kirana Owner<br/>MSME Owner]
    end
    
    subgraph Client["Client Layer"]
        Web[Web App<br/>React + Vite<br/>Port 5173]
        Mobile[Mobile Browser<br/>Responsive UI]
        WhatsApp[WhatsApp<br/>Business API]
    end
    
    subgraph AppServices["Application Services"]
        Frontend[Frontend Service<br/>React + TypeScript<br/>Tailwind CSS]
        AgentBackend[Agent Backend<br/>FastAPI + LangGraph<br/>Port 8000]
        DashBackend[Dashboard Backend<br/>Flask + Python<br/>Port 8001]
    end
    
    subgraph AWS["AWS Cloud Services"]
        direction TB
        
        subgraph AI["AI/ML Services"]
            Bedrock[Amazon Bedrock<br/>Nova Lite<br/>Chat & Reasoning]
            SageMaker[Amazon SageMaker<br/>DeepAR<br/>Demand Forecasting]
        end
        
        subgraph Automation["Automation Services"]
            EventBridge[Amazon EventBridge<br/>Scheduled Rules<br/>Every 30 min]
            Lambda[AWS Lambda<br/>Alert Handler<br/>Festival Orchestrator]
            Calendar[SSM Change Calendar<br/>Events & Deadlines]
        end
        
        subgraph Data["Data Services"]
            DynamoDB[Amazon DynamoDB<br/>User Profiles<br/>Alerts & State]
            S3[Amazon S3<br/>Panchang/Calendars<br/>Historical Data]
        end
        
        subgraph Auth["Security"]
            Cognito[Amazon Cognito<br/>User Authentication<br/>JWT Tokens]
        end
        
        subgraph Voice["Voice Services"]
            Transcribe[Amazon Transcribe<br/>Speech-to-Text]
            Polly[Amazon Polly<br/>Text-to-Speech]
        end
    end
    
    Retailer --> Web
    Retailer --> Mobile
    Retailer --> WhatsApp
    
    Web --> Frontend
    Mobile --> Frontend
    WhatsApp --> AgentBackend
    
    Frontend --> AgentBackend
    Frontend --> DashBackend
    
    AgentBackend --> Bedrock
    AgentBackend --> DynamoDB
    AgentBackend --> Cognito
    AgentBackend --> Transcribe
    AgentBackend --> Polly
    
    DashBackend --> SageMaker
    DashBackend --> Bedrock
    DashBackend --> S3
    
    EventBridge --> Lambda
    Calendar --> Lambda
    Lambda --> AgentBackend
    Lambda --> DashBackend
    Lambda --> Bedrock
    Lambda --> DynamoDB
    Lambda --> S3
    
    style Users fill:#4caf50,color:#fff
    style Client fill:#e3f2fd
    style AppServices fill:#fff3e0
    style AWS fill:#ff9800,color:#fff
    style AI fill:#2196f3,color:#fff
    style Automation fill:#ff5722,color:#fff
    style Data fill:#4caf50,color:#fff
    style Auth fill:#9c27b0,color:#fff
    style Voice fill:#f3e5f5
```

---

## 2. Detailed Component Architecture

```mermaid
flowchart LR
    subgraph User["User Interface"]
        Browser[Web Browser<br/>Chrome/Safari]
        WA[WhatsApp]
    end
    
    subgraph Frontend["Frontend (Port 5173)"]
        Landing[Landing Page]
        Onboard[Onboarding Chat]
        Dashboard[Dashboard Home]
        MyDay[My Day Chat]
        Control[Control Centre<br/>iframe]
    end
    
    subgraph AgentAPI["Agent Backend (Port 8000)"]
        ChatAPI[/v1/chat<br/>Chat Endpoint]
        AlertAPI[/v1/alerts<br/>Alert Management]
        WebhookAPI[/v1/webhook<br/>WhatsApp Handler]
        ProfileAPI[/v1/profile<br/>User Profile]
        TTSAPI[/v1/tts<br/>Voice Output]
        
        LangGraph[LangGraph Engine<br/>Multi-Agent System]
        
        SalesAgent[Sales Agent]
        InvAgent[Inventory Agent]
        PriceAgent[Pricing Agent]
        ForecastAgent[Forecast Agent]
        AlertAgent[Alert Prefs Agent]
    end
    
    subgraph DashAPI["Dashboard API (Port 8001)"]
        KPIRoute[/api/kpis<br/>Business Metrics]
        ForecastRoute[/api/forecast<br/>Demand Prediction]
        PriceRoute[/api/price<br/>Price Analysis]
        WhatIfRoute[/api/whatif<br/>Simulator]
        StatusRoute[/api/model-status<br/>Health Check]
    end
    
    Browser --> Landing
    Landing --> Onboard
    Onboard --> Dashboard
    Dashboard --> MyDay
    Dashboard --> Control
    
    MyDay --> ChatAPI
    MyDay --> AlertAPI
    MyDay --> TTSAPI
    
    Control --> KPIRoute
    Control --> ForecastRoute
    Control --> PriceRoute
    Control --> WhatIfRoute
    
    ChatAPI --> LangGraph
    LangGraph --> SalesAgent
    LangGraph --> InvAgent
    LangGraph --> PriceAgent
    LangGraph --> ForecastAgent
    LangGraph --> AlertAgent
    
    WA --> WebhookAPI
    WebhookAPI --> LangGraph
    
    style User fill:#4caf50,color:#fff
    style Frontend fill:#e3f2fd
    style AgentAPI fill:#fff3e0
    style DashAPI fill:#f3e5f5
    style LangGraph fill:#2196f3,color:#fff
```

---

## 3. Proactive Alert Architecture

```mermaid
flowchart TB
    subgraph Trigger["Alert Triggers"]
        EB[Amazon EventBridge<br/>Cron: rate(30 minutes)]
        Manual[Manual Invoke<br/>Testing]
    end
    
    subgraph Lambda["Lambda Function"]
        Handler[alerts_handler.py]
        
        CheckTime[Check Current Time<br/>IST]
        GetUsers[Get All Users<br/>from DynamoDB]
        FilterUsers[Filter by<br/>alert_time_hour_ist]
        
        FetchCal[Fetch Calendar<br/>from S3]
        FetchNews[Fetch RSS News<br/>GST, Commodities]
        CheckEvents{Upcoming<br/>Events?}
        
        GetProfile[Get User Profile<br/>City, State, Business]
        GetKPIs[Get Business KPIs<br/>Dashboard API]
        GetForecast[Get Demand Forecast<br/>SageMaker]
        
        GenAlert[Generate Alert<br/>Bedrock Nova Lite]
        FormatAlert[Format Hinglish<br/>Message]
    end
    
    subgraph Delivery["Alert Delivery"]
        Webhook[POST to Backend<br/>/v1/alerts/incoming]
        Store[Store in DynamoDB<br/>alerts table]
        Push[Push to Frontend<br/>SSE/WebSocket]
        WADeliver[Send to WhatsApp<br/>Business API]
    end
    
    subgraph UserView["User Sees Alert"]
        MyDayUI[My Day Chat<br/>Alert Card]
        WAChat[WhatsApp<br/>Message]
    end
    
    EB --> Handler
    Manual --> Handler
    
    Handler --> CheckTime
    CheckTime --> GetUsers
    GetUsers --> FilterUsers
    
    FilterUsers --> FetchCal
    FetchCal --> FetchNews
    FetchNews --> CheckEvents
    
    CheckEvents -->|Yes| GetProfile
    CheckEvents -->|No| End1([No Alert])
    
    GetProfile --> GetKPIs
    GetKPIs --> GetForecast
    GetForecast --> GenAlert
    
    GenAlert --> FormatAlert
    FormatAlert --> Webhook
    
    Webhook --> Store
    Store --> Push
    Store --> WADeliver
    
    Push --> MyDayUI
    WADeliver --> WAChat
    
    style Trigger fill:#ff9800,color:#fff
    style Lambda fill:#4caf50,color:#fff
    style Delivery fill:#2196f3,color:#fff
    style UserView fill:#9c27b0,color:#fff
```

---

## 4. Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input["Data Input"]
        UserQuery[User Query<br/>"Sales kaisa hai?"]
        VoiceInput[Voice Input<br/>Transcribe]
        AlertTrigger[Alert Trigger<br/>EventBridge]
    end
    
    subgraph Processing["Data Processing"]
        LangGraph[LangGraph Router<br/>Intent Detection]
        
        Tools[Agent Tools]
        DashTool[Dashboard Tool<br/>Live KPIs]
        DBTool[DynamoDB Tool<br/>User Data]
        BedrockTool[Bedrock Tool<br/>AI Analysis]
        SageMakerTool[SageMaker Tool<br/>Forecasting]
    end
    
    subgraph DataSources["Data Sources"]
        DynamoDB[(DynamoDB<br/>Users, Stores, State)]
        S3[(S3<br/>Historical Data)]
        DashAPI[Dashboard API<br/>Real-time KPIs]
    end
    
    subgraph AI["AI Processing"]
        Bedrock[Bedrock Nova Lite<br/>Reasoning]
        SageMaker[SageMaker DeepAR<br/>Forecasting]
    end
    
    subgraph Output["Data Output"]
        Response[Hinglish Response]
        VoiceOutput[Voice Output<br/>Polly]
        Alert[Alert Notification]
        Chart[Chart Data<br/>Dashboard API]
    end
    
    UserQuery --> LangGraph
    VoiceInput --> LangGraph
    AlertTrigger --> LangGraph
    
    LangGraph --> Tools
    
    Tools --> DashTool
    Tools --> DBTool
    Tools --> BedrockTool
    Tools --> SageMakerTool
    
    DashTool --> DashAPI
    DBTool --> DynamoDB
    BedrockTool --> Bedrock
    SageMakerTool --> SageMaker
    
    DashAPI --> S3
    
    Bedrock --> Response
    Bedrock --> Alert
    SageMaker --> Chart
    Response --> VoiceOutput
    
    style Input fill:#e3f2fd
    style Processing fill:#fff3e0
    style DataSources fill:#4caf50,color:#fff
    style AI fill:#2196f3,color:#fff
    style Output fill:#9c27b0,color:#fff
```

---

## 5. Security Architecture

```mermaid
flowchart TB
    subgraph Public["Public Internet"]
        User[User Device]
    end
    
    subgraph Edge["Edge Layer"]
        HTTPS[HTTPS/TLS<br/>Encryption]
        CORS[CORS Policy<br/>Origin Control]
    end
    
    subgraph Auth["Authentication Layer"]
        Cognito[Amazon Cognito<br/>User Pools]
        JWT[JWT Token<br/>Validation]
        Session[Session<br/>Management]
    end
    
    subgraph App["Application Layer"]
        Frontend[Frontend<br/>Public Access]
        Backend[Backend APIs<br/>Protected]
    end
    
    subgraph Data["Data Layer"]
        DynamoDB[DynamoDB<br/>Encryption at Rest]
        S3[S3<br/>Bucket Policies]
    end
    
    subgraph IAM["IAM & Permissions"]
        LambdaRole[Lambda Execution<br/>Role]
        EC2Role[EC2 Instance<br/>Role]
        Policies[IAM Policies<br/>Least Privilege]
    end
    
    User --> HTTPS
    HTTPS --> CORS
    CORS --> Cognito
    
    Cognito --> JWT
    JWT --> Session
    Session --> Frontend
    Session --> Backend
    
    Backend --> DynamoDB
    Backend --> S3
    
    LambdaRole --> DynamoDB
    LambdaRole --> S3
    EC2Role --> Backend
    
    Policies --> LambdaRole
    Policies --> EC2Role
    
    style Public fill:#e3f2fd
    style Edge fill:#fff3e0
    style Auth fill:#9c27b0,color:#fff
    style App fill:#4caf50,color:#fff
    style Data fill:#2196f3,color:#fff
    style IAM fill:#ff9800,color:#fff
```

---

## 6. Deployment Architecture

```mermaid
flowchart TB
    subgraph Dev["Development"]
        LocalDev[Local Development<br/>./start.sh<br/>4 services]
    end
    
    subgraph AWS["AWS Cloud"]
        subgraph Compute["Compute"]
            EC2[EC2 Instance<br/>t3.medium<br/>Ubuntu 22.04]
            SystemD[systemd Services<br/>4 processes]
        end
        
        subgraph Network["Networking"]
            VPC[VPC<br/>Private Subnet]
            SG[Security Groups<br/>Ports: 5173, 8000, 8001]
            ELB[Load Balancer<br/>Optional]
        end
        
        subgraph Storage["Storage"]
            EBS[EBS Volume<br/>App + Data]
            S3Deploy[S3<br/>Static Assets]
        end
        
        subgraph Managed["Managed Services"]
            Cognito2[Cognito]
            DynamoDB2[DynamoDB]
            Lambda2[Lambda]
            Bedrock2[Bedrock]
            SageMaker2[SageMaker]
        end
    end
    
    subgraph CI["CI/CD (Future)"]
        GitHub[GitHub<br/>Source Control]
        Actions[GitHub Actions<br/>Build & Deploy]
    end
    
    LocalDev --> GitHub
    GitHub --> Actions
    Actions --> EC2
    
    EC2 --> SystemD
    SystemD --> VPC
    VPC --> SG
    SG --> ELB
    
    EC2 --> EBS
    EC2 --> S3Deploy
    
    SystemD --> Cognito2
    SystemD --> DynamoDB2
    Lambda2 --> SystemD
    SystemD --> Bedrock2
    SystemD --> SageMaker2
    
    style Dev fill:#e3f2fd
    style Compute fill:#fff3e0
    style Network fill:#4caf50,color:#fff
    style Storage fill:#2196f3,color:#fff
    style Managed fill:#ff9800,color:#fff
    style CI fill:#9c27b0,color:#fff
```

---

## 7. Scalability Architecture

```mermaid
flowchart TB
    subgraph Current["Current Scale<br/>(5 Retailers)"]
        Single[Single EC2<br/>Instance]
        Local[Local Data<br/>Processing]
    end
    
    subgraph Future["Future Scale<br/>(1,000+ Retailers)"]
        subgraph LoadBalance["Load Balancing"]
            ALB[Application<br/>Load Balancer]
            Multi[Multiple EC2<br/>Instances]
        end
        
        subgraph Caching["Caching Layer"]
            ElastiCache[ElastiCache<br/>Redis]
            CDN[CloudFront<br/>CDN]
        end
        
        subgraph DataScale["Data Scaling"]
            DynamoScale[DynamoDB<br/>Auto-scaling]
            S3Scale[S3<br/>Unlimited]
        end
        
        subgraph Compute["Compute Scaling"]
            ASG[Auto Scaling<br/>Group]
            Lambda3[Lambda<br/>Concurrent]
        end
    end
    
    Current --> Future
    
    ALB --> Multi
    Multi --> ElastiCache
    Multi --> CDN
    
    Multi --> DynamoScale
    Multi --> S3Scale
    
    ASG --> Multi
    Lambda3 --> Multi
    
    style Current fill:#e3f2fd
    style Future fill:#4caf50,color:#fff
    style LoadBalance fill:#ff9800,color:#fff
    style Caching fill:#2196f3,color:#fff
    style DataScale fill:#9c27b0,color:#fff
    style Compute fill:#fff3e0
```

---

## 8. AWS Service Integration Map

```mermaid
mindmap
  root((AI Sahayak<br/>Architecture))
    Frontend
      React App
      Vite Build
      Tailwind CSS
      Cognito Auth
    Backend
      FastAPI
      LangGraph
      Flask API
      systemd
    AI/ML
      Bedrock Nova Lite
        Chat
        Reasoning
        Insights
      SageMaker DeepAR
        Forecasting
        Training
        Endpoints
    Automation
      EventBridge
        Scheduled Rules
        Event Patterns
      Lambda
        Alert Handler
        Orchestrator
      SSM Calendar
        Events
        Deadlines
    Data
      DynamoDB
        Users
        Stores
        Alerts
        State
      S3
        Calendars
        Historical Data
    Voice
      Transcribe
        Speech to Text
      Polly
        Text to Speech
    Integration
      WhatsApp API
```

---

## Architecture Layers Explained

### Layer 1: User Interface
- **Web App**: React-based responsive UI
- **Mobile**: Mobile-optimized views
- **WhatsApp**: Alternative channel for alerts

### Layer 2: Application Services
- **Frontend Service**: React + TypeScript (Port 5173)
- **Agent Backend**: FastAPI + LangGraph (Port 8000)
- **Dashboard Backend**: Flask + Python (Port 8001)

### Layer 3: AWS AI/ML Services
- **Bedrock**: Chat understanding and response generation
- **SageMaker**: Demand forecasting with DeepAR

### Layer 4: Automation Services
- **EventBridge**: Scheduled triggers every 30 minutes
- **Lambda**: Serverless alert processing
- **SSM Calendar**: Event and deadline management

### Layer 5: Data Services
- **DynamoDB**: User profiles, store data, alert preferences, conversation state (low latency)
- **S3**: Panchang/calendars, static data, historical records
- *(MongoDB is optional/deprecated in this codebase.)*

### Layer 6: Security & Auth
- **Cognito**: User authentication and JWT tokens
- **IAM**: Role-based access control
- **Encryption**: At rest and in transit

### Layer 7: Voice Services
- **Transcribe**: Convert speech to text (Hinglish)
- **Polly**: Convert text to speech (voice responses)

---

## Key Architecture Decisions

### 1. Microservices Approach
**Why**: Separation of concerns, independent scaling
- Frontend service (UI)
- Agent backend (Chat + AI)
- Dashboard backend (Analytics)
- Lambda functions (Alerts)

### 2. Event-Driven Architecture
**Why**: Proactive intelligence, not just reactive
- EventBridge triggers Lambda on schedule
- Lambda generates alerts based on calendar
- Alerts pushed to users automatically

### 3. Serverless Components
**Why**: Cost optimization, auto-scaling
- Lambda for alert processing
- DynamoDB for user data
- S3 for static storage
- Cognito for authentication

### 4. Multi-Agent System
**Why**: Specialized handling per domain
- Sales agent for revenue queries
- Inventory agent for stock queries
- Pricing agent for price optimization
- Forecast agent for demand prediction

### 5. Data Store Strategy
**Why**: Single primary store for simplicity and latency
- DynamoDB: User profiles, alert preferences, conversation/session state
- S3: Panchang, calendars, historical data

---

## Data Flow Examples

### Example 1: User Asks Question
```
User: "Sales kaisa hai?"
  ↓
Frontend → Agent Backend (/v1/chat)
  ↓
LangGraph → Sales Agent
  ↓
Dashboard Tool → Dashboard API (/api/kpis)
  ↓
DynamoDB → Fetch user's store data
  ↓
Bedrock → Generate Hinglish response
  ↓
Response: "Aaj ka sales ₹15,240 hai, kal se 12% zyada!"
```

### Example 2: Proactive Alert
```
EventBridge (2:00 PM IST)
  ↓
Lambda: alerts_handler
  ↓
Check DynamoDB: Users with alert_time = 14:00
  ↓
Fetch S3: Calendar shows Diwali in 3 days
  ↓
Dashboard API: Get current stock levels
  ↓
SageMaker: Get demand forecast
  ↓
Bedrock: Generate alert message
  ↓
POST to Backend: /v1/alerts/incoming
  ↓
Store in DynamoDB + Push to Frontend
  ↓
User sees: "Diwali 3 din mein! Mithai demand 40% badhega"
```

---

## Performance Characteristics

### Latency Targets
- Chat response: < 2 seconds
- Forecast generation: < 5 seconds
- Alert delivery: < 30 seconds
- Dashboard load: < 1 second
- API calls: < 500ms

### Throughput
- Concurrent users: 100+
- Messages/second: 50+
- Alerts/day: 10,000+
- Forecasts/day: 1,000+

### Availability
- Target: 99.9% uptime
- Bedrock SLA: 99.9%
- DynamoDB SLA: 99.99%
- Lambda SLA: 99.95%

---

## Cost Architecture

### Monthly Cost Breakdown (100 users)
```
Amazon Bedrock:     $50  (chat + reasoning)
SageMaker DeepAR:   $100 (forecasting endpoints)
Lambda:             $10  (alert processing)
DynamoDB:           $25  (user data)
S3:                 $5   (storage)
EventBridge:        $2   (scheduled rules)
Cognito:            $3   (authentication)
EC2:                $30  (t3.medium)
────────────────────────
Total:              ~$225/month
Per user:           ~$2.25/month
```

### Cost Optimization Strategies
1. Serverless-first (pay per use)
2. DynamoDB on-demand pricing
3. S3 lifecycle policies
4. Lambda memory optimization
5. Bedrock batch processing

---

## Presentation Summary

### For Judges - Key Architecture Highlights:

1. ✅ **10 AWS Services** - Comprehensive cloud integration
2. ✅ **Event-Driven** - Proactive, not reactive
3. ✅ **Microservices** - Scalable, maintainable
4. ✅ **Serverless** - Cost-effective, auto-scaling
5. ✅ **Multi-Agent AI** - Specialized intelligence
6. ✅ **Real-time** - Fast responses, live data
7. ✅ **Secure** - Cognito + encryption + IAM
8. ✅ **Scalable** - 5 → 1,000+ retailers ready

### One-Liner:
"AI Sahayak uses a modern, event-driven microservices architecture on AWS, combining Bedrock AI, SageMaker ML, and serverless automation to deliver proactive business intelligence to Indian MSMEs."

---

## Diagram Usage Tips

### For PowerPoint:
1. **Diagram 1** (High-Level) - Overall system view
2. **Diagram 3** (Proactive Alert) - Shows the "wow" factor
3. **Diagram 4** (Data Flow) - Shows intelligence
4. **Diagram 8** (Service Map) - Shows AWS integration

### Rendering:
- Use https://mermaid.live/ to export as PNG/SVG
- Or use Mermaid extension in VS Code
- High resolution for presentation

### Key Points to Emphasize:
- Event-driven proactive alerts
- Multi-agent AI system
- Serverless cost optimization
- Scalable architecture
- Comprehensive AWS integration
