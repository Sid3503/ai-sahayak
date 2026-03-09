# AI Sahayak - Use Case Diagrams (Simplified)

## 1. Simple Use Case Diagram - What Users Can Do

```mermaid
flowchart LR
    subgraph Actors
        R[👤 Kirana Owner<br/>Small Shop Owner]
        A[⚡ Alert System<br/>Automated]
    end
    
    subgraph "🔔 Proactive Features<br/>(System Alerts You)"
        P1[Get Festival Alerts]
        P2[Receive Demand Predictions]
        P3[Get Price Recommendations]
        P4[Daily Business Summary]
    end
    
    subgraph "💬 Chat Features<br/>(You Ask Questions)"
        C1[Ask About Sales<br/>'Sales kaisa hai?']
        C2[Check Stock<br/>'Low stock kya hai?']
        C3[Get Price Advice<br/>'Price kya rakhun?']
        C4[See Forecast<br/>'Demand badhega?']
    end
    
    subgraph "📊 Dashboard Features<br/>(View & Analyze)"
        D1[View KPIs<br/>Revenue, Stock, Trends]
        D2[Demand Forecast<br/>Next 7 Days]
        D3[Pricing Intelligence<br/>Optimal Prices]
        D4[What-If Simulator<br/>Test Price Changes]
    end
    
    R -->|receives| P1
    R -->|receives| P2
    R -->|receives| P3
    R -->|receives| P4
    
    R -->|asks| C1
    R -->|asks| C2
    R -->|asks| C3
    R -->|asks| C4
    
    R -->|views| D1
    R -->|views| D2
    R -->|views| D3
    R -->|uses| D4
    
    A -.auto sends.-> P1
    A -.auto sends.-> P2
    A -.auto sends.-> P3
    A -.auto sends.-> P4
    
    style R fill:#4caf50,color:#fff
    style A fill:#ff9800,color:#fff
    style P1 fill:#e3f2fd
    style P2 fill:#e3f2fd
    style P3 fill:#e3f2fd
    style P4 fill:#e3f2fd
    style C1 fill:#fff3e0
    style C2 fill:#fff3e0
    style C3 fill:#fff3e0
    style C4 fill:#fff3e0
    style D1 fill:#f3e5f5
    style D2 fill:#f3e5f5
    style D3 fill:#f3e5f5
    style D4 fill:#f3e5f5
```

## 2. User Scenarios - Real Examples

### Scenario 1: Festival Alert (Proactive)
```mermaid
flowchart LR
    A[📅 Diwali in 3 Days] --> B[🤖 System Checks<br/>Raju's Stock & Sales]
    B --> C[⚡ Alert Generated<br/>'Diwali aa raha hai!<br/>Mithai demand badhega']
    C --> D[📱 Raju Gets Alert<br/>in My Day Chat]
    D --> E[👤 Raju Views<br/>Forecast & Adjusts Price]
    
    style A fill:#ff9800,color:#fff
    style B fill:#2196f3,color:#fff
    style C fill:#4caf50,color:#fff
    style D fill:#9c27b0,color:#fff
    style E fill:#4caf50,color:#fff
```

### Scenario 2: Sales Question (Reactive)
```mermaid
flowchart LR
    A[👤 Ramesh Asks<br/>'Aaj sales kaisa hai?'] --> B[🤖 AI Fetches<br/>Live KPIs]
    B --> C[📊 Gets Today's Data<br/>₹15,240 revenue]
    C --> D[🤖 Bedrock Generates<br/>Hinglish Response]
    D --> E[💬 'Aaj ka sales<br/>₹15,240 hai, kal se<br/>12% zyada!']
    
    style A fill:#4caf50,color:#fff
    style B fill:#2196f3,color:#fff
    style C fill:#ff9800,color:#fff
    style D fill:#2196f3,color:#fff
    style E fill:#9c27b0,color:#fff
```

### Scenario 3: Price Decision (Dashboard)
```mermaid
flowchart LR
    A[👤 Kanta Opens<br/>Dashboard] --> B[📊 Views Current<br/>Atta Price: ₹45/kg]
    B --> C[🎯 AI Suggests<br/>₹48/kg optimal]
    C --> D[🔄 Tests in<br/>What-If Simulator]
    D --> E[✅ Sees +8% Revenue<br/>Updates Price]
    
    style A fill:#4caf50,color:#fff
    style B fill:#9c27b0,color:#fff
    style C fill:#2196f3,color:#fff
    style D fill:#ff9800,color:#fff
    style E fill:#4caf50,color:#fff
```

## 3. Feature Categories - Simple View

| 🔔 Proactive (System → You) | 💬 Chat (You → System) | 📊 Dashboard (Visual) |
|------------------------------|------------------------|----------------------|
| Festival alerts | Ask about sales | View KPIs |
| Demand predictions | Check inventory | See forecasts |
| Price recommendations | Get pricing advice | Pricing intelligence |
| Daily summaries | Ask any question | What-if simulator |
| Stock warnings | Voice queries | Trend analysis |

### Key Difference:
- **Proactive**: System sends alerts automatically (you don't ask)
- **Chat**: You ask questions in Hinglish, AI answers
- **Dashboard**: Visual analytics and tools

## 4. Who Does What - Actor Roles

```mermaid
flowchart TB
    subgraph "👤 Kirana Owner (You)"
        U1[Set alert preferences]
        U2[Ask questions in chat]
        U3[View dashboard]
        U4[Make business decisions]
    end
    
    subgraph "🤖 AI Sahayak System"
        S1[Answer questions<br/>Bedrock AI]
        S2[Generate forecasts<br/>SageMaker]
        S3[Analyze data<br/>Live KPIs]
        S4[Provide insights<br/>Hinglish]
    end
    
    subgraph "⚡ Alert Engine (Automated)"
        A1[Check calendar<br/>EventBridge]
        A2[Monitor events<br/>Lambda]
        A3[Send alerts<br/>WhatsApp/App]
        A4[Track preferences<br/>DynamoDB]
    end
    
    U1 -.tells.-> S1
    U2 -.asks.-> S1
    U3 -.views.-> S3
    
    S1 -.responds to.-> U4
    S2 -.predicts for.-> U4
    S3 -.shows to.-> U4
    
    A1 -.triggers.-> A2
    A2 -.generates.-> A3
    A3 -.notifies.-> U4
    A4 -.stores.-> U1
    
    style U1 fill:#4caf50,color:#fff
    style U2 fill:#4caf50,color:#fff
    style U3 fill:#4caf50,color:#fff
    style U4 fill:#4caf50,color:#fff
    style S1 fill:#2196f3,color:#fff
    style S2 fill:#2196f3,color:#fff
    style S3 fill:#2196f3,color:#fff
    style S4 fill:#2196f3,color:#fff
    style A1 fill:#ff9800,color:#fff
    style A2 fill:#ff9800,color:#fff
    style A3 fill:#ff9800,color:#fff
    style A4 fill:#ff9800,color:#fff
```

## 5. Complete Feature List - What AI Sahayak Does

### 🔔 Proactive Features (Automated Alerts)
| Feature | Example | When |
|---------|---------|------|
| Festival Alerts | "Diwali in 3 days, stock mithai!" | Before festivals |
| Demand Predictions | "Demand spike expected tomorrow" | Daily/Weekly |
| Price Recommendations | "Competitor lowered price, adjust yours" | Price changes |
| Stock Warnings | "Atta stock low, reorder now" | Low inventory |
| Daily Summary | "Today's sales: ₹15K, up 12%" | Set time (e.g., 2 PM) |

### 💬 Chat Features (Ask Anything in Hinglish)
| Question Type | Example Query | AI Response |
|---------------|---------------|-------------|
| Sales | "Aaj sales kaisa hai?" | "₹15,240, kal se 12% zyada" |
| Inventory | "Low stock kya hai?" | "Atta 5kg left, order karo" |
| Pricing | "Price kya rakhun?" | "₹48/kg optimal hai" |
| Forecast | "Demand badhega?" | "Next week 20% increase" |
| General | "Kya karna chahiye?" | Business advice |

### 📊 Dashboard Features (Visual Analytics)
| Feature | What It Shows | Benefit |
|---------|---------------|---------|
| KPIs | Revenue, stock, top items | Quick overview |
| Demand Forecast | 7-day prediction chart | Plan inventory |
| Pricing Intelligence | Optimal prices, margins | Maximize profit |
| What-If Simulator | Impact of price changes | Test before deciding |
| Trend Analysis | Sales patterns over time | Spot opportunities |

## 6. Simple Architecture - How It Works

```mermaid
flowchart TB
    subgraph User["👤 Kirana Owner"]
        Phone[📱 Phone/Computer]
    end
    
    subgraph App["AI Sahayak App"]
        Chat[💬 My Day Chat]
        Dash[📊 Dashboard]
    end
    
    subgraph AI["🤖 AI Brain"]
        Bedrock[Amazon Bedrock<br/>Understands Hinglish]
        SageMaker[SageMaker<br/>Predicts Demand]
    end
    
    subgraph Auto["⚡ Automation"]
        EventBridge[EventBridge<br/>Scheduler]
        Lambda[Lambda<br/>Alert Generator]
    end
    
    subgraph Data["🗄️ Data Storage"]
        DynamoDB[DynamoDB<br/>User Profiles]
        MongoDB[MongoDB<br/>Chat History]
    end
    
    Phone --> Chat
    Phone --> Dash
    
    Chat --> Bedrock
    Dash --> SageMaker
    
    EventBridge --> Lambda
    Lambda --> Bedrock
    Lambda --> Chat
    
    Bedrock --> DynamoDB
    Chat --> MongoDB
    
    style Phone fill:#4caf50,color:#fff
    style Chat fill:#9c27b0,color:#fff
    style Dash fill:#9c27b0,color:#fff
    style Bedrock fill:#2196f3,color:#fff
    style SageMaker fill:#2196f3,color:#fff
    style EventBridge fill:#ff9800,color:#fff
    style Lambda fill:#ff9800,color:#fff
```

## 7. AWS Services - What Powers Each Feature

```mermaid
flowchart LR
    subgraph Features["Features"]
        F1[🔔 Proactive Alerts]
        F2[💬 Hinglish Chat]
        F3[📊 Demand Forecast]
        F4[🎯 Pricing AI]
    end
    
    subgraph AWS["AWS Services"]
        A1[EventBridge<br/>Scheduler]
        A2[Lambda<br/>Alert Engine]
        A3[Bedrock<br/>Nova Lite]
        A4[SageMaker<br/>DeepAR]
        A5[DynamoDB<br/>User Data]
        A6[Cognito<br/>Auth]
    end
    
    F1 --> A1
    F1 --> A2
    F1 --> A3
    
    F2 --> A3
    F2 --> A5
    
    F3 --> A4
    F3 --> A3
    
    F4 --> A3
    F4 --> A4
    
    A6 -.secures.-> F1
    A6 -.secures.-> F2
    A6 -.secures.-> F3
    
    style F1 fill:#e3f2fd
    style F2 fill:#fff3e0
    style F3 fill:#f3e5f5
    style F4 fill:#e8f5e9
    style A1 fill:#ff9800,color:#fff
    style A2 fill:#ff9800,color:#fff
    style A3 fill:#2196f3,color:#fff
    style A4 fill:#2196f3,color:#fff
    style A5 fill:#ff9800,color:#fff
    style A6 fill:#ff9800,color:#fff
```

## 8. Quick Reference - For Your Presentation

### One-Liner Descriptions:

**Proactive Alerts**: System automatically sends business insights before you ask

**Hinglish Chat**: Ask anything in Hindi+English mix, get instant AI answers

**Demand Forecast**: AI predicts next 7 days demand using 2 years of data

**Pricing Intelligence**: AI suggests optimal prices to maximize profit

**What-If Simulator**: Test price changes before applying them

**Dashboard**: Visual KPIs - revenue, stock, trends at a glance

### Target Users:
- 63+ million MSMEs in India
- Kirana stores, small traders, manufacturers
- Limited tech knowledge, speaks Hinglish
- Needs: Better decisions, more profit, less waste

### Key Innovation:
**Proactive > Reactive** - Don't wait for questions, send alerts automatically

### AWS Services Used:
- Bedrock (Nova Lite) - AI chat & reasoning
- SageMaker (DeepAR) - Demand forecasting
- Lambda + EventBridge - Automated alerts
- DynamoDB - User profiles & data
- Cognito - Authentication
- Transcribe + Polly - Voice features

## Usage Tips for Presentation

### Best Diagrams to Use:
1. **Diagram 1** (Simple Use Case) - Shows all features clearly
2. **Diagram 2** (Scenarios) - Real examples people understand
3. **Table in Section 3** - Quick feature comparison
4. **Diagram 6** (Simple Architecture) - How it all connects

### What to Highlight:
- ✅ Three interaction modes: Proactive, Chat, Dashboard
- ✅ Hinglish support for Indian users
- ✅ Real-time data + AI predictions
- ✅ Automated alerts (the "wow" factor)
- ✅ Easy to use (chat-based, no training needed)

### Avoid:
- ❌ Too many technical details
- ❌ Complex UML notation
- ❌ Long lists of features
- ❌ Architecture complexity

Keep it simple: "AI Sahayak tells you what you need to know, when you need it, in your language."
