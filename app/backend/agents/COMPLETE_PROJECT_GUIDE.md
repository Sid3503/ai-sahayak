# 🚀 AI SAHAYAK - Complete Project Guide

## AI-Powered Business Intelligence for India's Kirana Stores

**Target Market: 13+ Million Kirana Stores Across India**

---

## 🎯 Our Two Core Solutions

### 1. Festival Demand Forecaster
| Aspect | Details |
|--------|---------|
| **Inputs** | Sales history + Calendar (Diwali, Eid, Holi, Regional) + Weather data |
| **Outputs** | SKU-level demand forecast, Reorder quantity recommendations, Stockout alerts |
| **Impact** | 20-30% inventory reduction |

### 2. Price Intelligence for D2C
| Aspect | Details |
|--------|---------|
| **Inputs** | Own prices + Competitor prices + Elasticity data |
| **Outputs** | Optimal price band recommendations, Markdown timing suggestions |
| **Impact** | 5-10% margin improvement |

---

## A Comprehensive Walkthrough for the AWS AI for Bharat Hackathon

---

## Why This Wins (The Hook)

**Problem Statement Alignment:** This solution directly addresses "AI Copilots for Small Businesses" and "Demand Forecasting + Pricing Intelligence" - exactly what the hackathon asks for.

**The Market Gap:** 
- Big companies have data teams. Kirana stores operate on "gut feeling" and lose 20-30% profit annually
- No existing solution provides vernacular AI + festival intelligence for Kirana stores

**Our Unfair Advantage:**
- **Digital Panchang**: AI-powered regional event detection (festivals, weddings, weather)
- **Price Intelligence**: Real-time competitor pricing via ONDC network
- **Bhashini Integration**: True vernacular support (not just translation)
- **Proactive, Not Reactive**: System alerts shopkeepers before problems occur

---

# TABLE OF CONTENTS

1. [What is AI Sahayak? (Simple Explanation)](#1-what-is-ai-sahayak-simple-explanation)
2. [How It Works - Two Modes](#2-how-it-works---two-modes)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [The AI Agents - Our Smart Workers](#4-the-ai-agents---our-smart-workers)
5. [MongoDB Database Design](#5-mongodb-database-design)
6. [Complete Data Flow - Step by Step](#6-complete-data-flow---step-by-step)
7. [WhatsApp Integration](#7-whatsapp-integration)
8. [Prompt Files Explained](#8-prompt-files-explained)
9. [Knowledge Base](#9-knowledge-base)
10. [Frontend Dashboard](#10-frontend-dashboard)
11. [Complete Folder Structure](#11-complete-folder-structure)
12. [Implementation Checklist](#12-implementation-checklist)
13. [Demo Scenarios](#13-demo-scenarios)
14. [Quick Start Guide](#14-quick-start-guide)

---

# 1. WHAT IS AI SAHAYAK? (SIMPLE EXPLANATION)

## In Simple Terms

Imagine you own a small shop (kirana store) in India. You want to know:

- "What should I stock for Holi?"
- "How much profit will I make next month?"
- "What price should I set for my products?"
- "Am I charging the right price compared to competitors?"

**AI Sahayak is like having a smart business advisor who:**
- 📱 Talks to you on WhatsApp (in your language!)
- 🎯 Tells you what products to stock before festivals (Demand Forecasting)
- 💰 Helps you set the right prices (Price Intelligence)
- ⚠️ Warns you before you run out of stock (Reorder Alerts)
- 📊 Gives you personalized business advice

## Two Solutions, One Platform

| Feature | What It Does | Why It Matters |
|---------|--------------|----------------|
| **Festival Demand Forecaster** | Predicts what to stock based on local events, weather, past sales | Prevents stockouts and overstocking |
| **Price Intelligence** | Compares your prices to competitors, suggests optimal pricing | Maximizes margins, stays competitive |

## Who is it for?

**Primary Target: Kirana Store Owners (13+ Million across India)**

| Target User | Use Case |
|------------|---------|
| Kirana (grocery) shop owners | "Should I order more sugar before Diwali? What's the right price for milk?" |
| Small pharmacies | "Which medicines will be in demand during flu season?" |
| D2C Sellers | "What price should I set to maximize margins?" |
| Electronics shops | "When should I stock more fans for summer? What's my optimal price point?" |

## User Interface: WhatsApp Agent + Dashboard

### WhatsApp AI Agent (Primary Interface)
- **Voice & Text** in local languages (Hindi, Tamil, Telugu, Bengali, etc.)
- Proactive alerts for festivals, stockouts, pricing opportunities
- Natural conversation - no training needed

### Web Dashboard (Secondary Interface)
- Visual analytics and reports
- Inventory management
- Price optimization controls
- Full conversation history

## Why This Matters in India?

- 🏪 **70% of retail in India is unorganized** (13M+ Kirana stores)
- 📱 **WhatsApp has 400+ million users** in India
- 🌍 **Many shop owners don't speak English** well - Bhashini powers vernacular AI
- 🎪 **Festivals significantly impact sales** (Diwali, Holi, Eid, regional events)
- 💡 **Small shops lose 20-30% profit** due to overstocking or stockouts
- 💰 **Price intelligence can improve margins by 5-10%**

---

# 2. HOW IT WORKS - TWO MODES

## Mode A: Proactive Alerts (AI Comes to You!)

The system automatically detects upcoming events and sends you helpful alerts:

```
 📅 CALENDAR          🤖 AI SYSTEM              📱 WHATSAPP
     │                    │                          │
     │ "Holi in 10 days" │                          │
     │─────────────────▶│                          │
     │                   │ Analyze past sales       │
     │                   │─────────────────▶       │
     │                   │                          │
     │                   │ "Gulal sales +40%       │
     │                   │    last year!"          │
     │                   │◀─────────────────        │
     │                   │                          │
     │                   │ "Order 20kg Gulal?"     │
     │                   │─────────────────────────▶│
     │                   │                          │
     ▼                   ▼                          ▼
```

**Example Alert You Receive:**
```
 🤖 AI Sahayak: "Holi is coming in 10 days! 
Based on your sales, you sold 18kg of Gulal last year.
This year, we predict 40% more demand.
Recommendation: Order 20kg Gulal now!"

[Order 20kg] [View Details] [Ask Question]
```

## Mode B: Reactive Queries (You Ask, AI Answers!)

You send a question on WhatsApp, and AI answers:

```
 📱 WHATSAPP          🤖 AI SYSTEM              🗄️ DATABASE
     │                    │                          │
     │ "Next month        │                          │
     │  profit kaise     │                          │
     │  hoga?"           │                          │
     │─────────────────▶│                          │
     │                   │ Translate to English     │
     │                   │─────────────────▶       │
     │                   │                          │
     │                   │ "What's profit           │
     │                   │  prediction for          │
     │                   │  next month?"            │
     │                   │─────────────────────────▶│
     │                   │                          │
     │                   │ "₹45,000 profit         │
     │                   │  expected (+12%)"        │
     │                   │◀─────────────────        │
     │                   │                          │
     │                   │ Translate to Hindi       │
     │                   │◀─────────────────        │
     │                   │                          │
     │ "₹45,000 profit  │                          │
     │  expected hai!"  │                          │
     │◀─────────────────│                          │
     ▼                   ▼                          ▼
```

**Example Conversation:**
```
You: "Next month kitna profit hoga?"
 🤖 AI: "Aapke store ke hisaab se, agle mahine ka 
        estimated profit ₹45,000 hai. 
        Ye pichle mahine se 12% zyada hai."
```

---

# 3. SYSTEM ARCHITECTURE OVERVIEW

## High-Level Picture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         AI SAHAYAK SYSTEM                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐      ┌─────────────────────────────────────────┐   │
│  │   USER      │      │              AWS CLOUD                  │   │
│  │             │      │                                         │   │
│  │  📱 WhatsApp│      │  ┌─────────┐    ┌─────────┐             │   │
│  │  🌐 Website │──────│─▶│   API   │───▶│ LAMBDA  │             │   │
│  │  📱 Mobile  │      │  │ GATEWAY │    │FUNCTIONS│             │   │
│  │             │      │  └─────────┘    └────┬────┘             │   │
│  └─────────────┘      │                      │                   │   │
│                       │         ┌─────────────┼─────────────┐     │   │
│                       │         ▼             ▼             ▼     │   │
│                       │   ┌─────────┐   ┌─────────┐   ┌─────────┐  │   │
│                       │   │  BEDROCK│   │ MONGODB │   │  S3     │  │   │
│                       │   │  AGENTS │   │ (EC2)   │   │ STORAGE │  │   │
│                       │   └─────────┘   └─────────┘   └─────────┘  │   │
│                       │                                         │   │
│                       └─────────────────────────────────────────┘   │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Components Explained

| Component | What It Does | Why It Matters |
|-----------|--------------|----------------|
| **WhatsApp** | User talks to AI | Everyone already has WhatsApp |
| **API Gateway** | Traffic controller | Routes requests to right place |
| **Lambda** | Server that runs code | No server management needed |
| **Bedrock Agents** | AI that thinks/reasons | Generates smart responses |
| **MongoDB** | Data storage | Stores all business data |
| **S3** | File storage | Stores festival data, models |
| **AWS EventBridge Calendar** | Proactive trigger mechanism | Automatically schedules alerts and forecasts for upcoming events |

---

# 4. THE AI AGENTS - OUR SMART WORKERS

The AI Sahayak system uses **LangGraph** to create a scalable, modular agent architecture with stateful workflows. This framework enables:

- **Stateful conversations**: Maintain context across interactions
- **Modular design**: Independent, reusable components
- **Dynamic routing**: Adaptive workflow paths based on input and confidence
- **Tool integration**: Seamless use of external APIs and services
- **Error handling**: Robust fallback mechanisms
- **Scalability**: Easy addition of new capabilities
- **Maintainability**: Clear separation of concerns

Think of agents as **different team members**, each with a specific job:

## Agent 1: Query Handler (The Receptionist)

**Job:** Understands what the user is asking

```
USER: "Next month profit kaise hoga?"

Agent 1 thinks:
- Language: Hindi
- Intent: Profit forecast request
- Entity: "next month" = date range
- Store: User's store ID

Output: {
  intent: "profit_forecast",
  entities: { period: "next_month" },
  language: "hi"
}
```

## Agent 2: Translation Agent (The Translator)

**Job:** Translates between languages

```
Hindi → English:
"Next month profit kaise hoga?"
↓
"How much profit will I make next month?"

English → Hindi:
"You will make ₹45,000 profit"
↓
"Aap ₹45,000 ka profit kamayenge"
```

**Supports:** Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, English

## Agent 3: Forecast Agent (The Predictor)

**Job:** Generates demand/profit predictions

```
Input: "Predict profit for Store ABC next month"

Agent 3:
 1. Queries MongoDB for historical sales
 2. Checks upcoming events (festivals)
 3. Analyzes trends
 4. Generates prediction

Output: {
  prediction: "₹45,000 profit",
  confidence: 0.85,
  factors: ["Diwali upcoming", "+12% growth"]
}
```

## Agent 4: Event Agent (The Calendar Expert)

**Job:** Detects festivals and generates alerts

```
Input: "What's coming up in next 30 days?"

Agent 4:
 1. Checks Knowledge Base (Panchang)
 2. Maps to user's region
 3. Generates confidence score

Output: {
  events: [
    { name: "Holi", date: "2024-03-25", confidence: 0.9 },
    { name: "Good Friday", date: "2024-03-29", confidence: 0.7 }
  ]
}
```

## Agent 5: Pricing Intelligence Agent (The Price Optimizer)

**Job:** Analyzes pricing strategy and recommends optimal prices

```
Input: "What price should I set for sugar? Competitor is selling at ₹52/kg"

Agent 5:
 1. Gets current pricing data
 2. Analyzes price elasticity
 3. Checks competitor pricing (ONDC network)
 4. Calculates optimal price band

Output: {
  optimalPriceRange: { min: 48, max: 55 },
  recommendedPrice: 50,
  elasticityScore: 0.75,
  competitorAnalysis: "You are 2% below market average",
  marginImpact: "+8% if priced at ₹50",
  markdownTiming: "Consider 5% markdown in 15 days if slow-moving"
}
```

## Agent 6: Response Agent (The Writer)

**Job:** Creates the final answer in user's language

```
Input: {
  answer: "₹45,000 profit expected",
  language: "hi"
}

Agent 5:
 1. Formats for WhatsApp
 2. Adds helpful buttons
 3. Translates to Hindi
 4. Adds explanation

Output:
"Aapke store ka agle mahine ka profit ₹45,000 
hone ka anuman hai. Yeh pichle mahine se 
12% zyada hai.

[Details Dekhein] [Fir Se Puchen]"
```

---

# 5. MONGODB DATABASE DESIGN

This is where all the data is stored. Think of it like organized file cabinets.

## 5.1 Collections Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI SAHAYAK DATABASE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📁 COLLECTIONS (like file cabinets)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   stores     │  │  inventory   │  │   sales     │          │
│  │              │  │              │  │              │          │
│  │ - Store info │  │ - Products   │  │ - Transactions│        │
│  │ - Location   │  │ - Stock      │  │ - Revenue    │          │
│  │ - Owner      │  │ - Prices     │  │ - Items sold │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   events     │  │   users      │  │ conversations│          │
│  │              │  │              │  │              │          │
│  │ - Festivals  │  │ - Login info │  │ - Chat history│         │
│  │ - Confidence │  │ - Preferences│  │ - Context    │          │
│  │ - Impact     │  │ - Language   │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │ forecasts    │  │    udhaar    │                           │
│  │              │  │              │                           │
│  │ - Predictions│  │ - Credit     │                           │
│  │ - Accuracy   │  │ - Customers  │                           │
│  │ - Horizons  │  │ - Due dates  │                           │
│  └──────────────┘  └──────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 5.2 Detailed Schema for Each Collection

### COLLECTION 1: stores

**Purpose:** Store information - the shops using our platform

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // STORE DOCUMENT EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1234"),
  
  // Basic Information
  "storeId": "STORE_001",
  "name": "Sharma Kirana Store",
  "ownerName": "Rajesh Sharma",
  "phone": "+919876543210",
  "email": "rajesh@sharmakirana.com",
  
  // Location (Important for regional events!)
  "location": {
    "address": "123 Main Market",
    "pinCode": "110001",           // ← CRITICAL for regional events
    "city": "New Delhi",
    "district": "Central Delhi",
    "state": "Delhi",
    "culturalZone": "North India", // Festivals vary by zone!
    "coordinates": {
      "latitude": 28.6139,
      "longitude": 77.2090
    }
  },
  
  // Store Type
  "storeType": "kirana",  // "kirana" | "pharmacy" | "electronics" | "clothing" | "general"
  
  // Categories they sell
  "categories": ["groceries", "spices", "sweets", "beverages"],
  
  // Business Info
  "establishedYear": 2015,
  "monthlyRevenue": 150000,  // in rupees
  "employeeCount": 2,
  
  // Settings
  "settings": {
    "language": "hi",          // Preferred language
    "currency": "INR",
    "timezone": "Asia/Kolkata",
    "alertPreferences": {
      "whatsapp": true,
      "sms": false,
      "inApp": true,
      "quietHours": {
        "start": "22:00",
        "end": "07:00"
      }
    },
    "forecastHorizons": [7, 14, 30],  // Days to forecast
    "lowStockThreshold": 10
  },
  
  // Account Info
  "createdAt": ISODate("2024-01-15T10:30:00Z"),
  "updatedAt": ISODate("2024-03-01T14:20:00Z"),
  "subscription": {
    "tier": "free",    // "free" | "paid"
    "plan": "basic",
    "validUntil": ISODate("2024-04-15T00:00:00Z")
  }
}
```

**Indexes for stores collection:**

```javascript
// PRIMARY INDEX (automatically created)
{ "_id": 1 }  // Default _id index

// CUSTOM INDEXES - These make queries fast!
db.stores.createIndex({ "storeId": 1 }, { unique: true })           // Fast lookup by store ID
db.stores.createIndex({ "location.pinCode": 1 })                   // Find stores by pincode
db.stores.createIndex({ "location.state": 1 })                      // Find stores by state
db.stores.createIndex({ "phone": 1 }, { unique: true })             // Login by phone
db.stores.createIndex({ "ownerName": "text", "name": "text" })       // Search by name
db.stores.createIndex({ "subscription.tier": 1 })                   // Filter by subscription
db.stores.createIndex({ "createdAt": -1 })                          // Sort by creation date
```

---

### COLLECTION 2: inventory

**Purpose:** What products each store has, current stock levels, prices

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // INVENTORY DOCUMENT EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1235"),
  
  // Reference to store
  "storeId": "STORE_001",
  
  // Product Identification
  "sku": "SUGAR_1KG_001",
  "barcode": "8901234567890",
  "name": "Sugar (1 kg)",
  "category": "groceries",
  "subCategory": "sweeteners",
  "brand": "Sugar India Co.",
  
  // Quantities
  "currentStock": 50,
  "unit": "kg",
  "reorderPoint": 20,           // Alert when stock drops below this
  "reorderQuantity": 100,
  
  // Pricing
  "costPrice": 42,              // What store paid
  "sellingPrice": 50,           // What store sells for
  "mrp": 55,                    // Maximum Retail Price
  
  // Supplier Info
  "supplier": {
    "name": "ABC Wholesalers",
    "contact": "+919876543210",
    "leadTimeDays": 3
  },
  
  // Product Details
  " gstRate": 5,
  "weight": 1,
  "expiryDate": ISODate("2025-12-31"),
  
  // Historical Metrics
  "metrics": {
    "avgDailySales": 5,
    "maxDailySales": 15,
    "last30DaysSales": 150,
    "turnoverRate": 3.0
  },
  
  // Timestamps
  "lastRestocked": ISODate("2024-02-20T10:00:00Z"),
  "createdAt": ISODate("2024-01-15T10:30:00Z"),
  "updatedAt": ISODate("2024-03-01T14:20:00Z")
}
```

**Indexes for inventory collection:**

```javascript
// CUSTOM INDEXES
db.inventory.createIndex({ "storeId": 1, "sku": 1 }, { unique: true })  // Unique per store+product
db.inventory.createIndex({ "storeId": 1, "category": 1 })              // Products by category
db.inventory.createIndex({ "sku": 1 })                                  // Find by SKU across stores
db.inventory.createIndex({ "currentStock": 1 })                         // Low stock queries
db.inventory.createIndex({ "name": "text", "sku": "text" })             // Search products
db.inventory.createIndex({ "expiryDate": 1 })                           // Expiring items
db.inventory.createIndex({ "storeId": 1, "currentStock": 1 })          // Low stock per store
```

---

### COLLECTION 3: sales

**Purpose:** Every transaction (sale) recorded

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // SALES TRANSACTION EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1236"),
  
  // Reference to store
  "storeId": "STORE_001",
  
  // Transaction Details
  "transactionId": "TXN_20240301_001",
  "timestamp": ISODate("2024-03-01T10:30:00Z"),
  "transactionType": "sale",     // "sale" | "return" | "exchange"
  
  // Items Sold
  "items": [
    {
      "sku": "SUGAR_1KG_001",
      "name": "Sugar (1 kg)",
      "quantity": 2,
      "unitPrice": 50,
      "discount": 0,
      "total": 100
    },
    {
      "sku": "TEA_250G_001",
      "name": "Tea (250g)",
      "quantity": 1,
      "unitPrice": 80,
      "discount": 5,
      "total": 75
    }
  ],
  
  // Totals
  "subTotal": 175,
  "taxAmount": 8.75,
  "discountTotal": 5,
  "totalAmount": 178.75,
  
  // Payment
  "paymentMethod": "cash",       // "cash" | "upi" | "card" | "udhaar"
  "amountReceived": 200,
  "changeGiven": 21.25,
  
  // Customer (if known)
  "customerId": "CUST_001",
  
  // Special Flags
  "isUdhaar": false,             // Credit sale?
  "isFestivalSale": true,         // Was this during a festival?
  "festivalName": "Holi",         // Which festival
  
  // POS Info
  "posDevice": "ANDROID_001",
  "salespersonId": "STAFF_001",
  
  // Metadata
  "createdAt": ISODate("2024-03-01T10:30:00Z")
}
```

**Indexes for sales collection:**

```javascript
// CUSTOM INDEXES
db.sales.createIndex({ "storeId": 1, "timestamp": -1 })                     // Sales by store over time
db.sales.createIndex({ "storeId": 1, "transactionId": 1 }, { unique: true }) // Unique transaction
db.sales.createIndex({ "timestamp": -1 })                                    // All sales by date
db.sales.createIndex({ "customerId": 1, "timestamp": -1 })                   // Customer purchase history
db.sales.createIndex({ "items.sku": 1 })                                     // Sales by product
db.sales.createIndex({ "isUdhaar": 1, "timestamp": -1 })                    // Udhaar (credit) sales
db.sales.createIndex({ "storeId": 1, "festivalName": 1 })                   // Festival sales analysis
db.sales.createIndex({ "timestamp": 1, "storeId": 1 })                      // Date range queries
```

---

### COLLECTION 4: events

**Purpose:** Festivals, events, and their impact on sales

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // EVENT DOCUMENT EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1237"),
  
  // Event Identification
  "eventId": "EVENT_HOLI_2024",
  "name": "Holi",
  "type": "festival",            // "festival" | "harvest" | "weather" | "vacation" | "government"
  
  // Date Information
  "date": ISODate("2024-03-25T00:00:00Z"),
  "endDate": ISODate("2024-03-26T00:00:00Z"),
  "daysUntilEvent": 10,         // Calculated daily
  
  // Regional Information
  "regions": [
    {
      "pinCode": "100001",
      "state": "Delhi",
      "culturalZone": "North India",
      "significance": 0.95,      // How important is this event in this region?
      "confidenceScore": 0.9     // AI's confidence in impact prediction
    },
    {
      "pinCode": "500001",
      "state": "Telangana",
      "culturalZone": "South India",
      "significance": 0.6,
      "confidenceScore": 0.7
    }
  ],
  
  // Expected Impact
  "impactPrediction": {
    "overallSalesLift": 0.40,    // 40% increase expected
    "topCategories": [
      { "category": "sweets", "lift": 0.80 },
      { "category": "colors", "lift": 0.95 },
      { "category": "beverages", "lift": 0.50 }
    ],
    "topProducts": [
      { "sku": "GULAL_1KG_001", "lift": 1.2 },
      { "sku": "SUGAR_1KG_001", "lift": 0.6 }
    ]
  },
  
  // Historical Data (for reference)
  "historicalData": {
    "2023": {
      "actualSalesLift": 0.38,
      "topSelling": ["Gulal", "Colors", "Sweets"]
    },
    "2022": {
      "actualSalesLift": 0.35,
      "topSelling": ["Gulal", "Colors"]
    }
  },
  
  // Alert Status
  "alertStatus": {
    "sent": true,
    "sentAt": ISODate("2024-03-15T10:00:00Z"),
    "storesAlerted": 150,
    "ordersReceived": 45
  },
  
  // Metadata
  "createdAt": ISODate("2024-01-01T00:00:00Z"),
  "updatedAt": ISODate("2024-03-15T10:00:00Z")
}
```

**Indexes for events collection:**

```javascript
// CUSTOM INDEXES
db.events.createIndex({ "eventId": 1 }, { unique: true })                           // Unique event
db.events.createIndex({ "date": 1 })                                               // Events by date
db.events.createIndex({ "date": 1, "type": 1 })                                     // Festivals by date
db.events.createIndex({ "regions.pinCode": 1, "date": 1 })                         // Events for a pincode
db.events.createIndex({ "regions.state": 1, "date": 1 })                           // Events for a state
db.events.createIndex({ "daysUntilEvent": 1 })                                      // Upcoming events
db.events.createIndex({ "alertStatus.sent": 1, "date": 1 })                        // Alert tracking
```

---

### COLLECTION 5: users

**Purpose:** User accounts who access the system

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // USER DOCUMENT EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1238"),
  
  // User Identification
  "userId": "USER_001",
  "cognitoSub": "us-east-1:abc123-def456-ghi789",  // From AWS Cognito
  
  // Associated Store
  "storeId": "STORE_001",
  
  // Personal Info
  "name": "Rajesh Sharma",
  "phone": "+919876543210",
  "email": "rajesh@sharmakirana.com",
  "language": "hi",                // Preferred language for responses
  
  // Role (controls what they can do)
  "role": "owner",                 // "owner" | "manager" | "staff"
  
  // Permissions
  "permissions": {
    "canViewForecasts": true,
    "canViewReports": true,
    "canManageInventory": true,
    "canManageUsers": true,
    "canMakePayments": true,
    "canDeleteData": true
  },
  
  // WhatsApp Linking
  "whatsappLinked": true,
  "whatsappPhone": "+919876543210",
  
  // Settings
  "settings": {
    "notifications": {
      "forecastAlerts": true,
      "eventAlerts": true,
      "lowStockAlerts": true,
      "promotional": false
    },
    "language": "hi",
    "theme": "light"
  },
  
  // Activity
  "lastLogin": ISODate("2024-03-01T09:00:00Z"),
  "loginCount": 156,
  
  // Account Status
  "status": "active",             // "active" | "suspended" | "pending"
  "emailVerified": true,
  "phoneVerified": true,
  
  // Timestamps
  "createdAt": ISODate("2024-01-15T10:30:00Z"),
  "updatedAt": ISODate("2024-03-01T09:00:00Z")
}
```

**Indexes for users collection:**

```javascript
// CUSTOM INDEXES
db.users.createIndex({ "userId": 1 }, { unique: true })                    // Unique user
db.users.createIndex({ "phone": 1 }, { unique: true })                     // Login by phone
db.users.createIndex({ "email": 1 })                                       // Login by email
db.users.createIndex({ "storeId": 1 })                                    // Users in a store
db.users.createIndex({ "cognitoSub": 1 }, { unique: true })               // Cognito linking
db.users.createIndex({ "role": 1 })                                       // Filter by role
db.users.createIndex({ "status": 1 })                                      // Active/inactive users
```

---

### COLLECTION 6: conversations

**Purpose:** Chat history for conversation context

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // CONVERSATION DOCUMENT EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1239"),
  
  // Conversation ID
  "conversationId": "CONV_001",
  "storeId": "STORE_001",
  
  // Channel
  "channel": "whatsapp",         // "whatsapp" | "web" | "mobile"
  "phoneNumber": "+919876543210",
  
  // Messages
  "messages": [
    {
      "messageId": "MSG_001",
      "role": "user",
      "content": "Next month profit kaise hoga?",
      "language": "hi",
      "timestamp": ISODate("2024-03-01T10:30:00Z"),
      "type": "text"            // "text" | "voice" | "image"
    },
    {
      "messageId": "MSG_002",
      "role": "assistant",
      "content": "Aapke store ka agle mahine ka profit ₹45,000 hone ka anuman hai.",
      "language": "hi",
      "timestamp": ISODate("2024-03-01T10:30:05Z"),
      "type": "text",
      "intentDetected": "profit_forecast",
      "confidence": 0.92
    },
    {
      "messageId": "MSG_003",
      "role": "user",
      "content": "Kis products ke liye?",
      "language": "hi",
      "timestamp": ISODate("2024-03-01T10:31:00Z"),
      "type": "text"
    },
    {
      "messageId": "MSG_004",
      "role": "assistant",
      "content": "Sabse zyada profit sweets aur beverages se expected hai...",
      "language": "hi",
      "timestamp": ISODate("2024-03-01T10:31:10Z"),
      "type": "text",
      "contextFrom": "MSG_002"  // References previous message
    }
  ],
  
  // Session Info
  "status": "active",            // "active" | "closed"
  "startedAt": ISODate("2024-03-01T10:30:00Z"),
  "lastMessageAt": ISODate("2024-03-01T10:31:10Z"),
  "expiresAt": ISODate("2024-03-01T11:01:10Z"),  // 30 min TTL
  
  // Context
  "currentIntent": "profit_forecast",
  "entities": {
    "period": "next_month"
  },
  
  // Metadata
  "createdAt": ISODate("2024-03-01T10:30:00Z"),
  "updatedAt": ISODate("2024-03-01T10:31:10Z")
}
```

**Indexes for conversations collection:**

```javascript
// CUSTOM INDEXES
db.conversations.createIndex({ "conversationId": 1 }, { unique: true })         // Unique conversation
db.conversations.createIndex({ "storeId": 1, "startedAt": -1 })                // Store's conversations
db.conversations.createIndex({ "phoneNumber": 1, "startedAt": -1 })            // User's chats
db.conversations.createIndex({ "expiresAt": 1 }, { expireAfterSeconds: 0 })   // Auto-delete old chats (TTL)
db.conversations.createIndex({ "status": 1, "lastMessageAt": -1 })             // Active conversations
```

---

### COLLECTION 7: forecasts

**Purpose:** Store AI predictions

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // FORECAST DOCUMENT EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1240"),
  
  // Forecast ID
  "forecastId": "FC_001",
  "storeId": "STORE_001",
  
  // What we're forecasting
  "target": "demand",            // "demand" | "revenue" | "profit"
  "sku": "SUGAR_1KG_001",       // Optional - can be category-level
  "category": "groceries",
  
  // Forecast Period
  "horizon": 7,                  // 7 days, 14 days, or 30 days
  "startDate": ISODate("2024-03-02T00:00:00Z"),
  "endDate": ISODate("2024-03-08T23:59:59Z"),
  
  // Predictions (daily)
  "predictions": [
    {
      "date": ISODate("2024-03-02T00:00:00Z"),
      "predictedValue": 6,                    // Units expected to sell
      "confidenceLower": 4,
      "confidenceUpper": 8,
      "eventImpact": 0                        // Any event adjustment today
    },
    {
      "date": ISODate("2024-03-03T00:00:00Z"),
      "predictedValue": 7,
      "confidenceLower": 5,
      "confidenceUpper": 10,
      "eventImpact": 0
    }
    // ... more days
  ],
  
  // Summary
  "summary": {
    "totalPredicted": 50,                     // Total for horizon
    "avgDaily": 7.14,
    "trend": "increasing",                    // "increasing" | "stable" | "decreasing"
    "trendPercent": 12
  },
  
  // Model Info
  "model": {
    "name": "DeepAR-Prophet-Ensemble",
    "version": "2.1",
    "trainingDataPoints": 365,
    "accuracy": {
      "mape": 0.12,                           // Mean Absolute Percentage Error
      "rmse": 1.5
    }
  },
  
  // Influencing Factors
  "factors": [
    {
      "name": "Upcoming Festival",
      "event": "Holi",
      "date": ISODate("2024-03-25"),
      "impact": 0.40,
      "description": "Holi typically increases demand by 40%"
    },
    {
      "name": "Seasonality",
      "type": "weekly",
      "impact": 0.15,
      "description": "Weekend sales are typically 15% higher"
    }
  ],
  
  // Metadata
  "generatedAt": ISODate("2024-03-01T02:00:00Z"),   // When forecast was generated
  "validUntil": ISODate("2024-03-02T02:00:00Z"),    // When to regenerate
  "isEventAdjusted": true,
  
  "createdAt": ISODate("2024-03-01T02:00:00Z"),
  "updatedAt": ISODate("2024-03-01T02:00:00Z")
}
```

**Indexes for forecasts collection:**

```javascript
// CUSTOM INDEXES
db.forecasts.createIndex({ "forecastId": 1 }, { unique: true })              // Unique forecast
db.forecasts.createIndex({ "storeId": 1, "sku": 1, "horizon": 1 })            // Store's forecasts
db.forecasts.createIndex({ "storeId": 1, "startDate": -1 })                   // Forecasts by date
db.forecasts.createIndex({ "generatedAt": -1 })                               // Recent forecasts
db.forecasts.createIndex({ "validUntil": 1 })                                 // Expire forecasts
db.forecasts.createIndex({ "sku": 1, "startDate": 1 })                        // Product forecasts
db.forecasts.createIndex({ "category": 1, "startDate": -1 })                 // Category forecasts
```

---

### COLLECTION 8: pricing

**Purpose:** Store pricing data for price intelligence

```javascript
{
  "_id": ObjectId("65f1234567890abcdef1242"),
  
  "storeId": "STORE_001",
  
  "sku": "SUGAR_1KG_001",
  
  "pricing": {
    "costPrice": 42,
    "sellingPrice": 50,
    "mrp": 55,
    "lastUpdated": ISODate("2024-03-01T10:00:00Z")
  },
  
  "competitorData": {
    "source": "ONDC",
    "marketAverage": 52,
    "lowestCompetitor": 48,
    "highestCompetitor": 58,
    "sampleSize": 15,
    "lastUpdated": ISODate("2024-03-01T10:00:00Z")
  },
  
  "elasticity": {
    "priceElasticity": -1.2,
    "confidence": 0.75,
    "optimalPriceMin": 48,
    "optimalPriceMax": 55,
    "recommendedPrice": 51
  },
  
  "markdown": {
    "currentDiscount": 0,
    "recommendedMarkdown": 10,
    "markdownThreshold": 30,
    "daysToMarkdown": 15
  },
  
  "createdAt": ISODate("2024-01-15T10:30:00Z"),
  "updatedAt": ISODate("2024-03-01T10:00:00Z")
}
```

### COLLECTION 9: udhaar

**Purpose:** Track credit given to customers (Udhaar = credit in Hindi)

```javascript
{
  // ═══════════════════════════════════════════════════════════
  // UDHAAR (CREDIT) DOCUMENT EXAMPLE
  // ═══════════════════════════════════════════════════════════
  
  "_id": ObjectId("65f1234567890abcdef1241"),
  
  // Reference
  "udhaarId": "UDHAAR_001",
  "storeId": "STORE_001",
  
  // Customer Info
  "customerId": "CUST_001",
  "customerName": "Mahesh Kumar",
  "customerPhone": "+919876543211",
  
  // Transaction Details
  "transactionDate": ISODate("2024-02-25T10:00:00Z"),
  "dueDate": ISODate("2024-03-05T10:00:00Z"),
  
  // Amount
  "principalAmount": 1500,          // Original amount
  "paidAmount": 0,                  // How much paid so far
  "outstandingAmount": 1500,        // Still owed
  
  // Items (what they bought)
  "items": [
    { "sku": "RICE_5KG_001", "name": "Rice (5 kg)", "quantity": 2, "price": 750 },
    { "sku": "OIL_1L_001", "name": "Oil (1 L)", "quantity": 2, "price": 300 }
  ],
  
  // Status
  "status": "outstanding",           // "outstanding" | "partial" | "paid" | "overdue"
  
  // Payment History
  "payments": [],                    // Array of payments made
  
  // Reminders
  "reminderSent": false,
  "reminderCount": 0,
  
  // Metadata
  "createdAt": ISODate("2024-02-25T10:00:00Z"),
  "updatedAt": ISODate("2024-02-25T10:00:00Z")
}
```

**Indexes for udhaar collection:**

```javascript
// CUSTOM INDEXES
db.udhaar.createIndex({ "udhaarId": 1 }, { unique: true })                         // Unique udhaar
db.udhaar.createIndex({ "storeId": 1, "customerId": 1 })                           // Store's udhaars
db.udhaar.createIndex({ "customerId": 1, "transactionDate": -1 })                  // Customer's credit
db.udhaar.createIndex({ "status": 1, "dueDate": 1 })                               // Outstanding/overdue
db.udhaar.createIndex({ "storeId": 1, "outstandingAmount": -1 })                  // High value udhaars
db.udhaar.createIndex({ "dueDate": 1 })                                            // Due soon
```

---

## 5.3 MongoDB Connection Configuration

```javascript
// File: backend/src/services/mongodb/connection.ts

import { MongoClient, Db } from 'mongodb';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://your-ec2-ip:27017';
const DB_NAME = process.env.DB_NAME || 'ai_sahayak';

let client: MongoClient;
let db: Db;

export async function connectToMongoDB(): Promise<Db> {
  if (db) {
    return db;
  }
  
  try {
    client = new MongoClient(MONGODB_URI, {
      // Connection settings for production
      maxPoolSize: 10,
      minPoolSize: 2,
      connectTimeoutMS: 10000,
      socketTimeoutMS: 45000,
    });
    
    await client.connect();
    console.log('✅ Connected to MongoDB');
    
    db = client.db(DB_NAME);
    
    // Create indexes (do this once on startup)
    await createIndexes(db);
    
    return db;
  } catch (error) {
    console.error('❌ MongoDB connection error:', error);
    throw error;
  }
}

async function createIndexes(db: Db): Promise<void> {
  console.log('📇 Creating indexes...');
  
  // Stores indexes
  await db.collection('stores').createIndex({ 'storeId': 1 }, { unique: true });
  await db.collection('stores').createIndex({ 'location.pinCode': 1 });
  await db.collection('stores').createIndex({ 'phone': 1 }, { unique: true });
  
  // Inventory indexes
  await db.collection('inventory').createIndex({ 'storeId': 1, 'sku': 1 }, { unique: true });
  await db.collection('inventory').createIndex({ 'storeId': 1, 'category': 1 });
  await db.collection('inventory').createIndex({ 'currentStock': 1 });
  
  // Sales indexes
  await db.collection('sales').createIndex({ 'storeId': 1, 'timestamp': -1 });
  await db.collection('sales').createIndex({ 'customerId': 1, 'timestamp': -1 });
  await db.collection('sales').createIndex({ 'timestamp': -1 });
  
  // Events indexes
  await db.collection('events').createIndex({ 'date': 1 });
  await db.collection('events').createIndex({ 'regions.pinCode': 1, 'date': 1 });
  
  // Users indexes
  await db.collection('users').createIndex({ 'userId': 1 }, { unique: true });
  await db.collection('users').createIndex({ 'phone': 1 }, { unique: true });
  await db.collection('users').createIndex({ 'storeId': 1 });
  
  // Conversations indexes (with TTL for auto-expiry)
  await db.collection('conversations').createIndex(
    { 'expiresAt': 1 },
    { expireAfterSeconds: 0 }
  );
  
  console.log('✅ Indexes created successfully');
}

export function getDb(): Db {
  if (!db) {
    throw new Error('Database not connected. Call connectToMongoDB first.');
  }
  return db;
}

export async function closeMongoDB(): Promise<void> {
  if (client) {
    await client.close();
    console.log('🔌 MongoDB connection closed');
  }
}
```

---

# 6. COMPLETE DATA FLOW - STEP BY STEP

## Scenario 1: User Asks "Next month profit kaise hoga?"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP-BY-STEP FLOW: User Query via WhatsApp                                  │
└─────────────────────────────────────────────────────────────────────────────┘

USER                    WHATSAPP              LAMBDA                    LANGGRAPH
SENDS MESSAGE           WEBHOOK               RECEIVES                  FACTORY
                                                                            │
                                                                            ▼
                                                                    ┌─────────────┐
                                                                    │ INTENT      │
                                                                    │ ROUTER      │
                                                                    └──────┬──────┘
                                                                           │
                                                                           ▼
                                                                    ┌─────────────┐
                                                                    │ TASK        │
                                                                    │ PLANNER     │
                                                                    └──────┬──────┘
                                                                           │
                                                                           ▼
                                                                    ┌─────────────┐
                                                                    │ DATA        │
                                                                    │ RETRIEVER   │
                                                                    └──────┬──────┘
                                                                           │
                                                                           ▼
                                                                    ┌─────────────┐
                                                                    │ PROCESSOR   │
                                                                    └──────┬──────┘
                                                                           │
                                                                           ▼
                                                                    ┌─────────────┐
                                                                    │ VALIDATOR   │
                                                                    └──────┬──────┘
                                                                           │
                                                                           ▼
                                                                    ┌─────────────┐
                                                                    │ RESPONDER   │
                                                                    └──────┬──────┘
                                                                           │
                                                                           ▼
                                                                    ┌─────────────┐
                                                                    │ WHATSAPP    │
                                                                    │ API         │
                                                                    └─────────────┘
                                                                               
📱 "Next month                                                         ┌─────────────┐
  profit kaise           ┌──────────────┐                              │             │
  hoga?"                 │ POST /webhook│                             │ Intent:     │
  ──────────────────────▶│              │─────────────────────────────▶│ profit_forecast
                         │ Body: {      │                              │ Language: hi
                         │  from:       │                              │ Entities:   │
                         │  "+91...",   │                              │ next_month  │
                         │  type: text, │                              │ StoreId:    │
                         │  content:    │                              │ STORE_001   │
                         │  "Next..."   │                              └──────┬──────┘
                         │ }            │                             │
                         └──────────────┘                             │
                                                                          │
                                                                          ▼
                                                              ┌─────────────────────┐
                                                              │ MongoDB: STORES    │
                                                              │ Query: storeId     │
                                                              │ from user phone    │
                                                              └──────────┬──────────┘
                                                                         │
                                                                         ▼
                                                              ┌─────────────────────┐
                                                              │ MongoDB: SALES     │
                                                              │ Query: last 90 days│
                                                              │ sales for store    │
                                                              └──────────┬──────────┘
                                                                         │
                                            ┌──────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         AGENT 2: TRANSLATION                               │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Input: "Next month profit kaise hoga?" (Hindi)                     │  │
│  │                                                                     │  │
│  │ Using Bhashini API:                                                │  │
│  │ Hindi → English                                                    │  │
│  │                                                                     │  │
│  │ Output: "What will be the profit next month?" (English)            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         AGENT 3: FORECAST                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Input: "What will be the profit next month?"                       │  │
│  │                                                                     │  │
│  │ Processing:                                                        │  │
│  │ 1. Get historical sales data from MongoDB                          │  │
│  │ 2. Check for upcoming events (Holi in 25 days)                      │  │
│  │ 3. Apply forecasting model                                         │  │
│  │ 4. Generate prediction                                             │  │
│  │                                                                     │  │
│  │ Output: {                                                          │  │
│  │   prediction: "₹45,000 profit",                                    │  │
│  │   confidence: 0.85,                                                │  │
│  │   breakdown: {                                                     │  │
│  │     currentMonthly: "₹40,000",                                     │  │
│  │     expectedGrowth: "12%",                                         │  │
│  │     eventImpact: "+8% from Holi"                                   │  │
│  │   }                                                                │  │
│  │ }                                                                  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         AGENT 2: TRANSLATION (Response)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Input: "₹45,000 profit expected (+12% growth)" (English)            │  │
│  │                                                                     │  │
│  │ Using Bhashini API:                                                │  │
│  │ English → Hindi                                                    │  │
│  │                                                                     │  │
│  │ Output: "₹45,000 profit hone ka anuman hai (+12% growth)"         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         AGENT 4: RESPONSE FORMATTING                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Format for WhatsApp:                                               │  │
│  │                                                                     │  │
│  │ "🎯 Aapke store ka profit forecast:                               │  │
│  │                                                                     │  │
│  │ 📈 Agle mahine ka estimated profit: ₹45,000                      │  │
│  │ 📊 Pichle mahine se: +12% zyada                                    │  │
│  │ 🎪 Holi festival ke karan: +8% impact                               │  │
│  │                                                                     │  │
│  │ [Fir Se Puchen] [Details Dekhein]"                                  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                              WHATSAPP API                                  │
│                    Send formatted message to user                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                                                                     │  │
│  │  🤖 AI Sahayak                                                     │  │
│  │                                                                     │  │
│  │  🎯 Aapke store ka profit forecast:                               │  │
│  │                                                                     │  │
│  │  📈 Agle mahine ka estimated profit: ₹45,000                     │  │
│  │  📊 Pichle mahine se: +12% zyada                                   │  │
│  │  🎪 Holi festival ke karan: +8% impact                             │  │
│  │                                                                     │  │
│  │  ─────────────────────────────────────────                        │  │
│  │                                                                     │  │
│  │  [Fir Se Puchen]  [Details Dekhein]                               │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Scenario 2: Proactive Alert - Holi Coming!

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP-BY-STEP FLOW: Proactive Festival Alert                                │
└─────────────────────────────────────────────────────────────────────────────┘

AWS CALENDAR          EVENTBRIDGE             LANGGRAPH                     MONGODB
"Holi in 10 days"     TRIGGERS                WORKFLOW FACTORY              EVENTS
                         │                        │                              │
                         │                        ▼                              │
                         │                ┌─────────────────┐                    │
                         │                │ PROACTIVE ALERT │                    │
                         │                │   WORKFLOW      │                    │
                         │                └────────┬────────┘                    │
                         │                         │                              │
                         │                         ▼                              │
                         │                ┌─────────────────┐                    │
                         │                │ STORES          │                    │
                         │                │ RELEVANCE       │                    │
                         │                │  ANALYZER       │                    │
                         │                └────────┬────────┘                    │
                         │                         │                              │
                         │                         ▼                              │
                         │                ┌─────────────────┐                    │
                         │                │ IMPACT          │                    │
                         │                │  PREDICTOR      │                    │
                         │                └────────┬────────┘                    │
                         │                         │                              │
                         │                         ▼                              │
                         │                ┌─────────────────┐                    │
                         │                │ ALERT           │                    │
                         │                │  GENERATOR      │                    │
                         │                └────────┬────────┘                    │
                         │                         │                              │
                         │                         ▼                              │
                         │                ┌─────────────────┐                    │
                         │                │ CONFIDENCE      │                    │
                         │                │  CHECK          │                    │
                         │                └────────┬────────┘                    │
                         │                         │                              │
                         │                         ▼                              │
                         │                ┌─────────────────┐                    │
                         │                │ WHATSAPP        │                    │
                         │                │  API            │                    │
                         │                └─────────────────┘                    │
                         │                                                  │
                         └──────────────────────────────────────────────────┘
                         │                        │                         │
┌──────────────┐        │                        │                         │
│ "Holi"       │        │                        │                         │
│ detected     │        │                        │                         │
│ in 10 days   │────────▶                        │                         │
└──────────────┘        │    Event: "Holi_2024"  │                         │
                       │    Days until: 10       │                         │
                       │                        ▼                         │
                       │                 ┌────────────────┐                 │
                       │                 │ Query: Stores  │                 │
                       │                 │ in North India│                 │
                       │                 │ region         │                 │
                       │                 └───────┬────────┘                 │
                       │                         │                         │
                       │                         ▼                         │
                       │                 ┌────────────────┐                 │
                       │                 │ For each store:│                 │
                       │                 │ - Get past    │                 │
                       │                 │   Holi sales   │                 │
                       │                 │ - Calculate    │                 │
                       │                 │   confidence   │                 │
                       │                 │ - If > 0.7:    │                 │
                       │                 │   trigger alert│                 │
                       │                 └───────┬────────┘                 │
                       │                         │                         │
                       │                         ▼                         │
                       │                 ┌────────────────┐                 │
                       │                 │ Generate alert │                 │
                       │                 │ message        │                 │
                       │                 └───────┬────────┘                 │
                       │                         │                         │
                       │                         ▼                         │
                       │                 ┌────────────────┐   ┌──────────┐│
                       │                 │ WhatsApp API   │──▶│ USER'S   ││
                       │                 │ Send Alert     │   │ PHONE    ││
                       │                 └────────────────┘   └──────────┘│
                       │                         │                         │
                       │                         ▼                         │
                       │                 ┌────────────────┐                 │
                       │                 │ Store: Alert   │                 │
                       │                 │ sent in MongoDB│                 │
                       │                 └────────────────┘                 │
```

---

# 7. WHATSAPP INTEGRATION

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHATSAPP INTEGRATION FLOW                     │
└─────────────────────────────────────────────────────────────────┘

                      ┌─────────────────────────────────────────┐
                      │           META DEVELOPER PORTAL         │
                      │        (developers.facebook.com)        │
                      │                                         │
                      │  1. Create WhatsApp Business Account    │
                      │  2. Get Phone Number ID                 │
                      │  3. Get Access Token                    │
                      │  4. Set Webhook URL                     │
                      └─────────────────┬───────────────────────┘ │
                                        │
                                        ▼
                      ┌─────────────────────────────────────────┐
                      │              YOUR SYSTEM                  │
                      │                                         │
                      │  ┌──────────────┐      ┌──────────────┐  │
                      │  │  WhatsApp    │      │   WhatsApp   │  │
                      │  │  Webhook     │      │   Send API   │  │
                      │  │  Lambda      │      │   Lambda     │  │
                      │  └──────┬───────┘      └──────┬───────┘  │
                      │         │                     │          │
                      │         │                     │          │
                      │         ▼                     ▼          │
                      │  ┌──────────────────────────────────┐   │
                      │  │      Processing Pipeline         │   │
                      │  │  (Agents + MongoDB + Bedrock)   │   │
                      │  └──────────────────────────────────┘   │
                      │                                         │
                      └─────────────────────────────────────────┘
```

## Sample WhatsApp Messages

### Proactive Alert (Festival)
```
🤖 AI Sahayak

🎉 Holi aa rahi hai! (10 days)

Aapke store ke hisaab se, aapne pichle saal 18kg Gulal becha.
Is saal 40% zyada demand ho sakti hai.

📦 Recommendation: 20kg Gulal order karein

[Order Now] [Details Dekhein]
```

### Reactive Response (Profit Query)
```
🤖 AI Sahayak

📊 Aapka Profit Forecast:

💰 Agle mahine ka profit: ₹45,000
   ( Pichle mahine se +12% )

🔍 Kyun zyada?
   • Holi festival: +8%
   • General growth: +4%

[See Details] [Kuch aur puchen]
```

### Low Stock Alert
```
⚠️ Stock Kam Hai!

Product: Sugar (1 kg)
Current Stock: 8 kg
Reorder Point: 20 kg

🔄 Recommend: 100 kg order karein
   Cost: ₹4,200
   Supplier: ABC Wholesalers

[Order Now] [Later]
```

### Price Intelligence Recommendation
```
💰 Smart Pricing Suggestion

Product: Sugar (1 kg)
Your Current Price: ₹50
Market Average: ₹52
Competitor Range: ₹48-55

📊 Our Recommendation: ₹51

✅ Benefit: +5% margin while staying competitive
📅 Review again: 7 days

[Apply Price] [View Analysis]
```

### Markdown Timing Alert
```
🏷️ Price Optimization Opportunity

Product: Holi Colors (set)
Current Stock: 45 units
Days in Inventory: 25 days

🔔 Recommendation: Apply 10% markdown now

If you reduce price from ₹120 → ₹108:
- Expected sales increase: +30%
- Margin impact: -8% but faster inventory turnover

[Apply Markdown] [Keep Current Price]
```

---

# 8. PROMPT FILES EXPLAINED

## Why Use Prompt Files?

Prompts are stored as **Markdown files** because:
1. **Easy to edit** - No code changes needed
2. **Version control** - Track changes in Git
3. **Multiple languages** - Different prompts for different languages
4. **Easy to test** - Modify prompts without redeploying

## Example Prompt Files

### File 1: `prompts/translation/hi-en-translation.md`

```markdown
# Hindi to English Translation

## Task
Translate the following Hindi text to English.

## Instructions
1. Preserve the original meaning
2. Keep business/technical terms in English if no Hindi equivalent exists
3. Maintain a natural, conversational tone
4. If the input is already in English, return it as-is

## Examples

Input: "Next month profit kaise hoga?"
Output: "How much profit will I make next month?"

Input: "KitnaGST lagta hai?"
Output: "How much GST is applied?"

## Input Text
{{input_text}}

## Output
```

### File 2: `prompts/query-handling/intent-detection.md`

```markdown
# Intent Detection Agent

## Role
You are an AI assistant that analyzes user queries to understand their intent.

## Task
Analyze the user's message and identify:
1. The primary intent (what they want to know)
2. Entities (specific details mentioned)
3. Language
4. Urgency level

## Supported Intents

| Intent | Description | Example |
|--------|-------------|---------|
| profit_forecast | Ask about future profit | "Next month profit?" |
| demand_forecast | Ask about product demand | "How much will I sell?" |
| pricing | Ask about pricing | "What price should I set?" |
| inventory | Ask about stock | "Do I have enough stock?" |
| event_impact | Ask about festival impact | "How will Diwali affect sales?" |
| general | General question | "Hello" |

## Input
User message: "{{user_message}}"
Language: "{{language}}"

## Output Format (JSON)
{
  "intent": "profit_forecast",
  "confidence": 0.92,
  "entities": {
    "period": "next_month"
  },
  "language": "hi"
}
```

### File 3: `prompts/forecasting/demand-forecast.md`

```markdown
# Demand Forecasting Agent

## Role
You are an AI assistant that predicts product demand based on historical data.

## Input
- Historical sales data: {{sales_data}}
- Upcoming events: {{events}}
- Store information: {{store_info}}

## Task
Generate a demand forecast for the next {{horizon}} days.

## Output Format
{
  "forecast": [
    {
      "date": "2024-03-15",
      "predicted_demand": 50,
      "confidence_lower": 40,
      "confidence_upper": 65
    }
  ],
  "factors": [
    {
      "name": "Holi Festival",
      "impact": 0.40,
      "description": "40% increase expected due to Holi"
    }
  ],
  "summary": {
    "total_predicted": 350,
    "avg_daily": 50,
    "confidence": 0.85
  }
}
```

### File 4: `prompts/response/whatsapp-format.md`

```markdown
# WhatsApp Response Formatter

## Task
Format the AI response for WhatsApp delivery in the user's language.

## Instructions
1. Use emojis appropriately for visual appeal
2. Keep messages concise (WhatsApp has limits)
3. Include relevant buttons for quick actions
4. Use conversational tone
5. Add helpful context

## Example (Hindi)

Input: { "answer": "₹45,000 profit", "type": "forecast" }

Output:
🎯 Aapka Profit Forecast:

💰 Agle mahine ka estimated profit: ₹45,000
📊 Pichle mahine se: +12% zyada

🔍 Iska karan:
• Holi festival ke karan +8%
• Business growth +4%

[Details Dekhein] [Fir Se Puchen]
```

---

# 9. KNOWLEDGE BASE

## What's in the Knowledge Base?

```
┌─────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE BASE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📁 panchang/              🎪 FESTIVAL CALENDAR                 │
│  ├── festivals-2024.json    • All Indian festivals              │
│  ├── festivals-2025.json    • Dates                             │
│  ├── regional-events.json   • Regional significance             │
│  └── cultural-calendar.json • Regional variations              │
│                                                                  │
│  📁 retail/                💡 RETAIL KNOWLEDGE                  │
│  ├── best-practices.md      • Inventory management tips        │
│  ├── pricing-strategies.md  • How to price products            │
│  └── seasonal-tips.md       • Season-based advice              │
│                                                                  │
│  📁 examples/              💬 EXAMPLE CONVERSATIONS             │
│  ├── sample-queries.md     • Example user questions           │
│  └── sample-responses.md   • Example AI responses              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Sample Knowledge Base Entry

### `knowledge-base/panchang/festivals-2024.json`

```json
{
  "festivals": [
    {
      "id": "holi_2024",
      "name": "Holi",
      "date": "2024-03-25",
      "type": "festival",
      "regions": {
        "north_india": {
          "significance": 0.95,
          "key_products": ["gulal", "colors", "sweets", "beverages"],
          "sales_lift": 0.40
        },
        "south_india": {
          "significance": 0.60,
          "key_products": ["sweets", "fruits"],
          "sales_lift": 0.20
        }
      }
    },
    {
      "id": "diwali_2024",
      "name": "Diwali",
      "date": "2024-11-01",
      "type": "festival",
      "regions": {
        "all_india": {
          "significance": 0.99,
          "key_products": ["lights", "sweets", "clothes", "gifts"],
          "sales_lift": 0.60
        }
      }
    }
  ]
}
```

---

# 10. FRONTEND DASHBOARD

## What Users See

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI SAHAYAK DASHBOARD                       │
│                       (Web/Mobile View)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 👋 Welcome, Sharma Ji!                    🔔 3  ⚙️       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📊 Today's Summary                                       │  │
│  │                                                          │  │
│  │   Today's Sales    │  Stock Alerts   │  Upcoming Events│  │
│  │   ₹12,500          │  3 Items        │  Holi (10 days)  │  │
│  │   +15% vs yesterday│  ⚠️            │  🎉              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 📈 Demand Forecast (Next 7 Days)                        │  │
│  │                                                          │  │
│  │    █                                                    │  │
│  │    █ █                                                  │  │
│  │    █ █ █                                                │  │
│  │    █ █ █ █      █ █ █                                   │  │
│  │  ──┴────┴────┴────┴────┴────┴────┴────                │  │
│  │  Mon  Tue  Wed  Thu  Fri  Sat  Sun                    │  │
│  │                                                          │  │
│  │  📦 Top Products: Sugar, Tea, Rice                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 🎯 Quick Actions                                          │  │
│  │                                                          │  │
│  │  [Ask Question]  [View Forecast]  [Check Stock]        │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 💬 Recent Messages                                        │  │
│  │                                                          │  │
│  │  You: Next month profit kaise hoga?                     │  │
│  │  🤖: ₹45,000 (+12%) expected!                           │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# 11. COMPLETE FOLDER STRUCTURE

```
ai-sahayak/
│
├── 📁 infrastructure/                  # AWS & MongoDB Setup
│   ├── 📁 aws/
│   │   ├── 📁 cdk/                   # AWS CDK Infrastructure
│   │   └── 📁 scripts/              # Deployment scripts
│   │
│   ├── 📁 ec2-mongodb/              # MongoDB on EC2
│   │   ├── setup/                   # Installation scripts
│   │   └── config/                  # MongoDB configuration
│   │
│   └── 📁 scripts/                   # Setup scripts
│
├── 📁 backend/                        # Application Backend
│   ├── 📁 src/
│   │   ├── 📁 agents/               # 🤖 AI AGENTS
│   │   │   ├── query-agent/        # Intent detection
│   │   │   ├── translation-agent/  # Language translation (Bhashini)
│   │   │   ├── forecast-agent/     # Festival-driven demand forecasting
│   │   │   ├── pricing-agent/      # Price intelligence & optimization
│   │   │   ├── event-agent/        # Regional event detection (Panchang)
│   │   │   ├── stock-agent/        # Reorder quantity & stockout alerts
│   │   │   └── response-agent/     # Response formatting
│   │   │
│   │   ├── 📁 services/
│   │   │   ├── bedrock/            # Bedrock API client
│   ├── whatsapp/          │   │   # WhatsApp integration
│   │   │   ├── bhashini/          # Translation service
│   │   │   └── mongodb/           # Database connection
│   │   │
│   │   └── 📁 config/              # Configuration
│   │
│   └── package.json
│
├── 📁 prompts/                        # 📝 ALL PROMPTS (Markdown)
│   ├── 📁 system-prompts/
│   ├── 📁 query-handling/
│   ├── 📁 translation/
│   ├── 📁 forecasting/
│   ├── 📁 pricing/
│   ├── 📁 events/
│   └── 📁 response/
│
├── 📁 knowledge-base/                 # 📚 KNOWLEDGE BASE
│   ├── 📁 panchang/                 # Festival data
│   ├── 📁 retail/                   # Retail tips
│   └── 📁 examples/                 # Example conversations
│
├── 📁 frontend/                       # React Dashboard
│   └── 📁 web/
│
├── 📁 data/                          # 📊 Sample Data
│   ├── sample-stores.json
│   ├── sample-sales.json
│   ├── sample-inventory.json
│   └── sample-events.json
│
├── 📁 docs/                          # Documentation
│   ├── deployment-guide.md
│   ├── api-endpoints.md
│   └── demo-script.md
│
├── 📁 agents/                        # 🧠 LangGraph Agents
│   ├── state.py                     # Graph state definitions
│   ├── nodes/                       # Modular agent nodes
│   │   ├── router/                  # Query routing
│   │   │   ├── intent_router.py     # Intent-based routing
│   │   │   └── tools_router.py      # Tool selection
│   │   ├── planners/                # Task planning
│   │   │   ├── forecast_planner.py  # Forecasting tasks
│   │   │   └── pricing_planner.py   # Pricing tasks
│   │   ├── retrievers/              # Data retrieval
│   │   │   ├── sales_retriever.py   # Sales data
│   │   │   ├── inventory_retriever.py # Inventory data
│   │   │   └── events_retriever.py  # Event data
│   │   ├── processors/              # Data processing
│   │   │   ├── forecast_processor.py # Forecast generation
│   │   │   └── pricing_processor.py # Price optimization
│   │   ├── validators/              # Input validation
│   │   │   └── data_validator.py    # Data quality checks
│   │   └── responders/              # Response generation
│   │       ├── text_response.py   # Text responses
│   │       └── interactive_response.py # Interactive messages
│   ├── edges/                       # Workflow connections
│   │   ├── conditional/             # Conditional logic
│   │   │   ├── confidence_check.py  # Confidence-based routing
│   │   │   └── fallback_check.py    # Fallback handling
│   │   └── router/                  # Dynamic routing
│   │       └── next_step_router.py  # Next step determination
│   ├── tools/                       # External integrations
│   │   ├── bhashini_tool.py         # Translation service
│   │   ├── ondc_tool.py             # Competitor pricing
│   │   └── bedrock_tool.py          # LLM interface
│   ├── workflows/                   # Predefined workflows
│   │   ├── forecast_workflow.py     # Demand forecasting
│   │   ├── pricing_workflow.py      # Price optimization
│   │   └── proactive_alert_workflow.py # Proactive alerts
│   └── factory.py                   # Agent creation factory
│
├── README.md
├── package.json
└── .env.example
```

---

# 12. IMPLEMENTATION CHECKLIST

## Phase 1: Foundation (Day 1-2)

- [ ] AWS Account Created
- [ ] Bedrock Model Access Enabled (Qwen/Titan)
- [ ] EC2 Instance Launched
- [ ] MongoDB Installed and Running
- [ ] Security Groups Configured
- [ ] WhatsApp Business API Credentials Obtained
- [ ] API Gateway Created
- [ ] Lambda Functions Set Up
- [ ] Environment Variables Configured

## Phase 2: Core Agents (Day 3-4)

- [ ] Query Agent Created
- [ ] Translation Agent Created with Bhashini
- [ ] Forecast Agent Created
- [ ] Event Agent Created
- [ ] Response Agent Created
- [ ] All Prompt Files Created
- [ ] Agent Pipeline Orchestrated

## Phase 3: Integration (Day 5-6)

- [ ] WhatsApp Webhook Connected
- [ ] MongoDB Collections Created
- [ ] Indexes Created
- [ ] Sample Data Loaded
- [ ] Full Flow Tested
- [ ] Error Handling Implemented
- [ ] Logging Configured

## Phase 4: Polish (Day 7-8)

- [ ] Demo Scenarios Tested
- [ ] Multi-language Support Verified
- [ ] Frontend Dashboard Working
- [ ] Video/Slides Prepared
- [ ] Final Rehearsal Done

---

# 13. DEMO SCENARIOS

## Demo Scenario 1: Festival Alert (Proactive)

**Steps:**
1. Show calendar detecting "Holi in 10 days"
2. Show AI analyzing past sales
3. Show alert sent to WhatsApp
4. Show user receiving and interacting with alert

**Expected Output:**
```
🤖 AI Sahayak: "Holi is coming in 10 days!
Based on your sales, you sold 18kg of Gulal last year.
This year, we predict 40% more demand.

Recommendation: Order 20kg Gulal now!"

[Order Now] [View Details]
```

## Demo Scenario 2: Profit Query (Reactive)

**Steps:**
1. User sends voice note: "Next month profit kaise hoga?"
2. Show translation (Hindi → English)
3. Show AI analyzing data
4. Show response in Hindi

**Expected Output:**
```
User: "Next month profit kaise hoga?"

🤖: "Aapke store ka agle mahine ka profit ₹45,000 
hone ka anuman hai. Ye pichle mahine se 12% zyada hai."
```

## Demo Scenario 3: Pricing Question

**Steps:**
1. User asks: "If I reduce sugar price by ₹5, how much more will I sell?"
2. Show AI analyzing elasticity
3. Show recommendation

**Expected Output:**
```
User: "Sugar ki price ₹5 kam karein to kitna zyada bechege?"

🤖: "Price ₹5 kam karne se 15% zyada demand hogi.
Revenue impact: +₹375/day
But profit margin kam hoga. Recommend: ₹2 kam karein."
```

## Demo Scenario 4: Price Intelligence Auto-Optimization

**Steps:**
1. Show system detecting slow-moving inventory
2. Show competitor price analysis
3. Show markdown recommendation
4. Show user applying the price change

**Expected Output:**
```
🤖 AI Sahayak: "🏷️ Price Optimization

Product: Gulal (1 kg) - Festival stock
Current: ₹80 | Market: ₹85
Stock: 45 units (35 days)

💡 Recommendation: Reduce to ₹72 (-10%)
Expected: +40% sales velocity
Margin impact: -6%

[Apply 10% Off] [Suggest Different Price]"
```

---

# 14. QUICK START GUIDE

## Step 1: Set Up AWS

```bash
# Install AWS CLI
brew install awscli

# Configure
aws configure

# Set up CDK
npm install -g aws-cdk
cdk bootstrap
```

## Step 2: Set Up MongoDB on EC2

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install MongoDB
sudo apt update
sudo apt install mongodb

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Configure (edit /etc/mongodb.conf)
# Bind IP: 0.0.0.0 (for Lambda access)
```

## Step 3: Deploy Backend

```bash
# Install dependencies
cd backend
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Deploy to AWS
cdk deploy --all
```

## Step 4: Set Up WhatsApp

1. Go to developers.facebook.com
2. Create WhatsApp Business app
3. Get Phone Number ID and Access Token
4. Configure webhook URL in AWS
5. Add webhook to your .env

## Step 5: Test

```bash
# Run tests
npm test

# Start local development
npm run dev

# Test WhatsApp webhook
ngrok http 3000
# Configure ngrok URL in Meta developer portal
```

---

# 📞 HELP & SUPPORT

## Common Issues

| Issue | Solution |
|-------|----------|
| MongoDB connection timeout | Check security group allows port 27017 |
| Bedrock model not accessible | Request model access in AWS console |
| WhatsApp webhook not working | Verify ngrok tunnel is active |
| Translation not working | Check Bhashini API credentials |

---

# ✅ WRAP UP

Congratulations! You now have a complete understanding of the AI Sahayak system:

1. **What it does**: Helps small Indian retailers with AI-powered business insights
2. **How it works**: Two modes - proactive alerts and reactive queries
3. **The tech**: AWS Bedrock agents, MongoDB on EC2, WhatsApp integration
4. **The data**: 8 MongoDB collections with proper indexes
5. **The prompts**: Markdown files for easy customization
6. **The flow**: Complete end-to-end data pipelines

# 11. COMPLETE FOLDER STRUCTURE

```
ai-sahayak/
│
├── 📦 .github/
│   ├── workflows/
│   │   ├── backend-ci.yml
│   │   ├── frontend-ci.yml
│   │   ├── agents-ci.yml                          # ★ NEW: Python agents CI pipeline
│   │   ├── infrastructure-ci.yml
│   │   └── release.yml
│   └── CODEOWNERS
│
├── 🏗️ infrastructure/
│   ├── 📁 terraform/
│   │   ├── modules/
│   │   │   ├── networking/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── compute/
│   │   │   │   ├── ecs-cluster.tf
│   │   │   │   ├── lambda-functions.tf
│   │   │   │   └── ec2-mongodb.tf
│   │   │   ├── database/
│   │   │   │   ├── mongodb-ec2.tf
│   │   │   │   ├── dynamodb-tables.tf
│   │   │   │   └── elasticache-redis.tf
│   │   │   ├── messaging/
│   │   │   │   ├── sqs-queues.tf
│   │   │   │   ├── sns-topics.tf
│   │   │   │   └── eventbridge-rules.tf
│   │   │   ├── storage/
│   │   │   │   ├── s3-buckets.tf
│   │   │   │   └── efs-volumes.tf
│   │   │   ├── security/
│   │   │   │   ├── iam-roles.tf
│   │   │   │   ├── kms-keys.tf
│   │   │   │   └── waf-acls.tf
│   │   │   ├── monitoring/
│   │   │   │   ├── cloudwatch-dashboards.tf
│   │   │   │   ├── x-ray-groups.tf
│   │   │   │   └── alerts.tf
│   │   │   └── ci-cd/
│   │   │       ├── codebuild-projects.tf
│   │   │       └── codepipeline.tf
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   │   ├── main.tf
│   │   │   │   ├── terraform.tfvars
│   │   │   │   └── backend.tf
│   │   │   ├── staging/
│   │   │   │   ├── main.tf
│   │   │   │   ├── terraform.tfvars
│   │   │   │   └── backend.tf
│   │   │   └── prod/
│   │   │       ├── main.tf
│   │   │       ├── terraform.tfvars
│   │   │       └── backend.tf
│   │   └── global/
│   │       ├── iam-global.tf
│   │       └── route53.tf
│   │
│   ├── 📁 kubernetes/
│   │   ├── base/
│   │   │   ├── namespaces/
│   │   │   │   ├── backend.yaml
│   │   │   │   ├── frontend.yaml
│   │   │   │   ├── agents.yaml                    # ★ NEW: agents namespace
│   │   │   │   └── monitoring.yaml
│   │   │   ├── configmaps/
│   │   │   │   ├── app-config.yaml
│   │   │   │   └── agent-config.yaml
│   │   │   ├── secrets/
│   │   │   │   └── sealed-secrets.yaml
│   │   │   └── volumes/
│   │   │       └── persistent-volumes.yaml
│   │   └── overlays/
│   │       ├── dev/
│   │       │   ├── kustomization.yaml
│   │       │   └── patches/
│   │       ├── staging/
│   │       └── prod/
│   │
│   └── 📁 docker/
│       ├── base/
│       │   ├── python-base.Dockerfile
│       │   ├── node-base.Dockerfile
│       │   └── nginx-base.Dockerfile
│       ├── services/
│       │   ├── api-gateway.Dockerfile
│       │   ├── agent-orchestrator.Dockerfile
│       │   ├── forecast-service.Dockerfile
│       │   └── whatsapp-service.Dockerfile
│       └── docker-compose/
│           ├── docker-compose.dev.yml
│           ├── docker-compose.staging.yml
│           └── docker-compose.prod.yml
│
│
├── 📁 backend/
│   │
│   ├── 📁 api-gateway/                            # Node.js — Auth, routing, rate limiting
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── auth.routes.js
│   │   │   │   │   ├── forecast.routes.js
│   │   │   │   │   ├── pricing.routes.js
│   │   │   │   │   ├── inventory.routes.js
│   │   │   │   │   ├── orders.routes.js
│   │   │   │   │   ├── chat.routes.js             # ★ NEW: proxies to agents /v1/chat
│   │   │   │   │   └── webhook.routes.js
│   │   │   │   └── index.js
│   │   │   ├── middleware/
│   │   │   │   ├── auth.middleware.js
│   │   │   │   ├── rate-limit.middleware.js
│   │   │   │   ├── validation.middleware.js
│   │   │   │   ├── logging.middleware.js
│   │   │   │   └── error-handler.middleware.js
│   │   │   ├── services/
│   │   │   │   ├── service-registry.js
│   │   │   │   └── circuit-breaker.js
│   │   │   ├── utils/
│   │   │   │   ├── response-formatter.js
│   │   │   │   └── request-validator.js
│   │   │   └── app.js
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── e2e/
│   │   ├── package.json
│   │   ├── Dockerfile
│   │   └── README.md
│   │
│   ├── 📁 services/
│   │   │
│   │   ├── 📁 auth-service/
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── auth.controller.js
│   │   │   │   │   └── rbac.controller.js
│   │   │   │   ├── models/
│   │   │   │   │   ├── user.model.js
│   │   │   │   │   ├── role.model.js
│   │   │   │   │   └── permission.model.js
│   │   │   │   ├── services/
│   │   │   │   │   ├── cognito.service.js
│   │   │   │   │   ├── jwt.service.js
│   │   │   │   │   └── rbac.service.js
│   │   │   │   ├── utils/
│   │   │   │   │   ├── password-hash.js
│   │   │   │   │   └── token-generator.js
│   │   │   │   └── index.js
│   │   │   ├── tests/
│   │   │   ├── package.json
│   │   │   └── Dockerfile
│   │   │
│   │   ├── 📁 forecast-service/
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── forecast.controller.js
│   │   │   │   │   └── health.controller.js
│   │   │   │   ├── models/
│   │   │   │   │   ├── forecast.model.js
│   │   │   │   │   └── sales.model.js
│   │   │   │   ├── services/
│   │   │   │   │   ├── ml/
│   │   │   │   │   │   ├── prophet-engine.py
│   │   │   │   │   │   ├── deepar-engine.py
│   │   │   │   │   │   ├── ensemble-model.py
│   │   │   │   │   │   └── model-loader.py
│   │   │   │   │   ├── sage-maker.service.js
│   │   │   │   │   └── forecast-cache.service.js
│   │   │   │   ├── jobs/
│   │   │   │   │   ├── daily-forecast.job.js
│   │   │   │   │   └── model-retraining.job.js
│   │   │   │   ├── utils/
│   │   │   │   │   ├── data-preprocessor.js
│   │   │   │   │   └── feature-engineering.js
│   │   │   │   └── index.js
│   │   │   ├── tests/
│   │   │   ├── requirements.txt
│   │   │   ├── package.json
│   │   │   └── Dockerfile
│   │   │
│   │   ├── 📁 pricing-service/
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── pricing.controller.js
│   │   │   │   │   └── elasticity.controller.js
│   │   │   │   ├── models/
│   │   │   │   │   ├── price.model.js
│   │   │   │   │   └── competitor.model.js
│   │   │   │   ├── services/
│   │   │   │   │   ├── optimization/
│   │   │   │   │   │   ├── price-optimizer.py
│   │   │   │   │   │   └── elasticity-calculator.py
│   │   │   │   │   ├── ondc.service.js
│   │   │   │   │   └── markdown.service.js
│   │   │   │   ├── jobs/
│   │   │   │   │   └── competitor-sync.job.js
│   │   │   │   └── index.js
│   │   │   ├── tests/
│   │   │   └── Dockerfile
│   │   │
│   │   ├── 📁 inventory-service/
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── stock.controller.js
│   │   │   │   │   └── reorder.controller.js
│   │   │   │   ├── models/
│   │   │   │   │   ├── inventory.model.js
│   │   │   │   │   └── supplier.model.js
│   │   │   │   ├── services/
│   │   │   │   │   ├── stock-calculator.service.js
│   │   │   │   │   ├── reorder.service.js
│   │   │   │   │   └── supplier.service.js
│   │   │   │   └── index.js
│   │   │   ├── tests/
│   │   │   └── Dockerfile
│   │   │
│   │   ├── 📁 order-service/
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   ├── order.controller.js
│   │   │   │   │   └── payment.controller.js
│   │   │   │   ├── models/
│   │   │   │   │   ├── order.model.js
│   │   │   │   │   └── payment.model.js
│   │   │   │   ├── services/
│   │   │   │   │   ├── payment-gateway.service.js
│   │   │   │   │   ├── invoice.service.js
│   │   │   │   │   └── fulfillment.service.js
│   │   │   │   ├── consumers/
│   │   │   │   │   └── order-consumer.js
│   │   │   │   └── index.js
│   │   │   ├── tests/
│   │   │   └── Dockerfile
│   │   │
│   │   ├── 📁 whatsapp-service/                   # Node.js — thin Meta webhook adapter
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   └── webhook.controller.js      # Verify HMAC, ACK Meta, forward to agents
│   │   │   │   ├── services/
│   │   │   │   │   ├── whatsapp-api.service.js    # Outbound Meta Cloud API calls
│   │   │   │   │   ├── message-formatter.service.js
│   │   │   │   │   └── session-manager.service.js
│   │   │   │   ├── handlers/
│   │   │   │   │   ├── message.handler.js         # Text/voice → POST agents /v1/webhooks/whatsapp
│   │   │   │   │   ├── button.handler.js          # Button reply → POST agents
│   │   │   │   │   └── template.handler.js
│   │   │   │   └── index.js
│   │   │   ├── tests/
│   │   │   └── Dockerfile
│   │   │
│   │   ├── 📁 notification-service/
│   │   │   ├── src/
│   │   │   │   ├── controllers/
│   │   │   │   │   └── notification.controller.js
│   │   │   │   ├── services/
│   │   │   │   │   ├── sms.service.js
│   │   │   │   │   ├── email.service.js
│   │   │   │   │   └── push.service.js
│   │   │   │   ├── consumers/
│   │   │   │   │   └── notification-consumer.js
│   │   │   │   └── index.js
│   │   │   ├── tests/
│   │   │   └── Dockerfile
│   │   │
│   │   └── 📁 event-processor/                    # Node.js — EventBridge cron → triggers agents
│   │       ├── src/
│   │       │   ├── controllers/
│   │       │   │   └── event.controller.js
│   │       │   ├── services/
│   │       │   │   ├── calendar.service.js
│   │       │   │   ├── festival-detector.service.js
│   │       │   │   └── impact-analyzer.service.js
│   │       │   ├── jobs/
│   │       │   │   └── event-detection.job.js     # Fires POST agents /v1/chat (channel=SYSTEM)
│   │       │   └── index.js
│   │       ├── tests/
│   │       └── Dockerfile
│   │
│   │
│   ├── 📁 agents/                                 # ★ Python — LangGraph AI Engine
│   │   │
│   │   ├── 📄 langgraph.json                      # LangGraph deployment manifest
│   │   ├── 📄 pyproject.toml                      # Dependencies + package config
│   │   ├── 📄 requirements.txt
│   │   ├── 📄 requirements-dev.txt
│   │   ├── 📄 setup.py
│   │   ├── 📄 Dockerfile.agents
│   │   ├── 📄 .env.example
│   │   ├── 📄 README.md
│   │   │
│   │   ├── 📁 src/
│   │   │   └── 📁 ai_sahayak/
│   │   │       │
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 main.py                     # FastAPI entry point (uvicorn)
│   │   │       │
│   │   │       ├── 📁 api/                        # ── HTTP Layer ──────────────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 server.py               # FastAPI app factory + lifespan + CORS
│   │   │       │   ├── 📄 deps.py                 # Shared DI: graph registry, DB clients
│   │   │       │   │
│   │   │       │   ├── 📁 routes/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 health.py            # GET /health  GET /ready  GET /metrics
│   │   │       │   │   ├── 📄 chat.py              # POST /v1/chat  (web chatbot, sync)
│   │   │       │   │   ├── 📄 stream.py            # POST /v1/stream  (SSE for web UI)
│   │   │       │   │   ├── 📄 websocket.py         # WS /v1/ws/{session_id}  (real-time)
│   │   │       │   │   ├── 📄 webhook_whatsapp.py  # POST /v1/webhooks/whatsapp
│   │   │       │   │   ├── 📄 onboarding.py        # POST /v1/onboarding
│   │   │       │   │   └── 📄 admin.py             # GET /v1/sessions  /v1/graphs  (debug)
│   │   │       │   │
│   │   │       │   └── 📁 middleware/
│   │   │       │       ├── 📄 __init__.py
│   │   │       │       ├── 📄 auth.py              # Verify internal service tokens
│   │   │       │       ├── ��� logging.py           # Structured request/response logging
│   │   │       │       ├── 📄 tracing.py           # OpenTelemetry request tracing
│   │   │       │       └── 📄 rate_limit.py        # Per-store sliding window rate limit
│   │   │       │
│   │   │       ├── 📁 channels/                   # ── Channel Adapters ────────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 base.py                  # BaseChannelAdapter (abstract)
│   │   │       │   ├── 📄 models.py                # AgentRequest / AgentResponse / Channel enum
│   │   │       │   │
│   │   │       │   ├── 📁 whatsapp/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 mapper.py            # Meta payload → AgentRequest
│   │   │       │   │   ├── 📄 formatter.py         # AgentResponse → WA buttons/lists/text
│   │   │       │   │   ├── 📄 outbound.py          # POST reply back to Meta Cloud API
│   │   │       │   │   ├── 📄 verifier.py          # HMAC signature re-verification
│   │   │       │   │   └── 📄 templates.py         # WA message template builders
│   │   │       │   │
│   │   │       │   └── 📁 web/
│   │   │       │       ├── 📄 __init__.py
│   │   │       │       ├── 📄 mapper.py            # Web chat payload → AgentRequest
│   │   │       │       ├── 📄 formatter.py         # AgentResponse → JSON for React UI
│   │   │       │       └── 📄 streaming.py         # SSE / WebSocket stream helpers
│   │   │       │
│   │   │       ├── 📁 graphs/                     # ── LangGraph Core ──────────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   │
│   │   │       │   ├── 📁 state/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 conversation.py      # ConversationState  (main TypedDict)
│   │   │       │   │   ├── 📄 user_context.py      # UserContext: store_id, lang, region, channel
│   │   │       │   │   ├── 📄 agent_state.py       # Per-agent scratchpad
│   │   │       │   │   └── 📄 reducers.py          # Custom merge reducers for lists/dicts
│   │   │       │   │
│   │   │       │   ├── 📁 workflows/               # Top-level compiled StateGraphs
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 retail_assistant.py  # ★ Main copilot graph (all user entry)
│   │   │       │   │   ├── 📄 onboarding.py        # Onboarding Q&A → store metadata
│   │   │       │   │   ├── 📄 forecast.py          # Festival demand forecasting sub-graph
│   │   │       │   │   ├── 📄 pricing.py           # Price intelligence sub-graph
│   │   │       │   │   ├── 📄 inventory.py         # Stock / reorder advisory sub-graph
│   │   │       │   │   └── 📄 alert.py             # Proactive alert generation sub-graph
│   │   │       │   │
│   │   │       │   ├── 📁 nodes/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   │
│   │   │       │   │   ├── 📁 language/            # ★ Multilingual pipeline nodes
│   │   │       │   │   │   ├── 📄 __init__.py
│   │   │       │   │   │   ├── 📄 detector.py      # Detect: hi / mr / gu / ta / te / bn / en
│   │   │       │   │   │   ├── 📄 normalizer.py    # Hinglish / code-mix clean before translate
│   │   │       │   │   │   ├── 📄 translator.py    # User lang → English  (Bhashini NMT)
│   │   │       │   │   │   └── 📄 localizer.py     # English output → user lang + tone
│   │   │       │   │   │
│   │   │       │   │   ├── 📁 router/
│   │   │       │   │   │   ├── 📄 __init__.py
│   │   │       │   │   │   ├── 📄 intent_router.py     # Intent classify → sub-graph pick
│   │   │       │   │   │   ├── 📄 workflow_router.py   # Routes to forecast/pricing/inventory
│   │   │       │   │   │   └── 📄 channel_router.py    # Channel-specific post-processing
│   │   │       │   │   │
│   │   │       │   │   ├── 📁 planners/
│   │   │       │   │   │   ├── 📄 __init__.py
│   │   │       │   │   │   ├── 📄 forecast_planner.py
│   │   │       │   │   │   ├── 📄 pricing_planner.py
│   │   │       │   │   │   ├── 📄 inventory_planner.py
│   │   │       │   │   │   └── 📄 onboarding_planner.py
│   │   │       │   │   │
│   │   │       │   │   ├── 📁 retrievers/
│   │   │       │   │   │   ├── 📄 __init__.py
│   │   │       │   │   │   ├── 📄 sales_retriever.py       # Historical sales ← MongoDB
│   │   │       │   │   │   ├── 📄 inventory_retriever.py   # Current stock ← MongoDB
│   │   │       │   │   │   ├── 📄 events_retriever.py      # Festival data ← Panchang + KB
│   │   │       │   │   │   ├── 📄 competitor_retriever.py  # Competitor prices ← ONDC
│   │   │       │   │   │   └── 📄 profile_retriever.py     # Store profile ← MongoDB
│   │   │       │   │   │
│   │   │       │   │   ├── 📁 processors/
│   │   │       │   │   │   ├── 📄 __init__.py
│   │   │       │   │   │   ├── 📄 forecast_processor.py    # ML demand prediction
│   │   │       │   │   │   ├── 📄 event_processor.py       # Event Confidence Score calc
│   │   │       │   │   │   ├── 📄 pricing_processor.py     # Price band + elasticity
│   │   │       │   │   │   ├── 📄 inventory_processor.py   # Safety stock + reorder
│   │   │       │   │   │   ├── 📄 onboarding_processor.py  # Build StoreMetadata from QnA
│   │   │       │   │   │   └── 📄 explanation_processor.py # Explainable AI "why" builder
│   │   │       │   │   │
│   │   │       │   │   ├── 📁 responders/
│   │   │       │   │   │   ├── 📄 __init__.py
│   │   │       │   │   │   ├── 📄 response_builder.py      # Final answer assembly
│   │   │       │   │   │   ├── 📄 interactive.py           # WA buttons / quick replies / lists
│   │   │       │   │   │   └── 📄 fallback.py              # Graceful degradation responses
│   │   │       │   │   │
│   │   │       │   │   ├── 📁 validators/
│   │   │       │   │   │   ├── 📄 __init__.py
│   │   │       │   │   │   ├── 📄 input_validator.py
│   │   │       │   │   │   └── 📄 output_validator.py
│   │   │       │   │   │
│   │   │       │   │   └── 📁 system/
│   │   │       │   │       ├── 📄 __init__.py
│   │   │       │   │       ├── 📄 error_handler.py
│   │   │       │   │       └── 📄 audit_logger.py          # Decision audit trail (Explainable AI)
│   │   │       │   │
│   │   │       │   ├── 📁 edges/
│   ��   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📁 conditional/
│   │   │       │   │   │   ├── 📄 confidence_router.py     # Route by confidence score threshold
│   │   │       │   │   │   ├── 📄 language_router.py       # Re-route if lang switches mid-conv
│   │   │       │   │   │   ├── 📄 fallback_router.py       # Low confidence → fallback node
│   │   │       │   │   │   └── 📄 safety_router.py         # Guardrails / policy enforcement
│   │   │       │   │   └── 📁 dynamic/
│   │   │       │   │       ├── 📄 next_step_router.py
│   │   │       │   │       └── 📄 planner_tool_router.py
│   │   │       │   │
│   │   │       │   └── 📁 runtime/
│   │   │       │       ├── 📄 __init__.py
│   │   │       │       ├── 📄 executor.py          # run_graph() / arun_graph() / stream_graph()
│   │   │       │       ├── 📄 registry.py          # Graph version registry + factory
│   │   │       │       ├── 📄 checkpointer.py      # LangGraph checkpointer → Redis/MongoDB
│   │   │       │       ├── 📄 streaming.py         # astream_events wrapper for SSE/WS
│   │   │       │       └── 📄 policies.py          # Timeouts, max hops, retry budgets
│   │   │       │
│   │   │       ├── 📁 language/                   # ── Multilingual Engine ─────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 constants.py             # Language codes, locale map, script map
│   │   │       │   │
│   │   │       │   ├── 📁 detection/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 detector.py          # langdetect + custom heuristics
│   │   │       │   │   ├── 📄 script_detector.py   # Unicode range → Devanagari/Gujarati/Tamil
│   │   │       │   │   └── 📄 hinglish.py          # Roman-script Hinglish/Tanglish detection
│   │   │       │   │
│   │   │       │   ├── 📁 translation/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 bhashini_client.py   # Bhashini ULCA API (ASR + NMT + TTS)
│   │   │       │   │   ├── 📄 pipeline.py          # ASR → NMT → TTS pipeline builder
│   │   │       │   │   └── 📄 fallback.py          # Bedrock Claude as translation fallback
│   │   │       │   │
│   │   │       │   ├── 📁 normalization/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 code_mix.py          # Hinglish/Tanglish/Manglish cleaner
│   │   │       │   │   ├── 📄 numerals.py          # ₹ + regional script numbers → int
│   │   │       │   │   └── 📄 dates.py             # "agle mahine" / "Diwali ke baad" → date
│   │   │       │   │
│   │   │       │   └── 📁 localization/
│   │   │       │       ├── 📄 __init__.py
│   │   │       │       ├── 📄 formatter.py         # Numbers, currency, dates per locale
│   │   │       │       ├── 📄 tone_adapter.py      # Formal/informal per lang (Tamil formal etc.)
│   │   │       │       └── 📄 locale_map.py        # State → lang → festivals → calendar
│   │   │       │
│   │   │       ├── 📁 prompts/                    # ── Prompt Library ──────────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 registry.py              # Load prompt by (name, language, version)
│   │   │       │   ├── 📄 loader.py                # Load + version .yaml prompt files
│   │   │       │   │
│   │   │       │   ├── 📁 system/                  # Core system prompts (English base)
│   │   │       │   │   ├── 📄 retail_assistant.yaml
│   │   │       │   │   ├── 📄 onboarding_agent.yaml
│   │   │       │   │   ├── 📄 forecast_agent.yaml
│   │   │       │   │   ├── 📄 pricing_agent.yaml
│   │   │       │   │   └── 📄 inventory_agent.yaml
│   │   │       │   │
│   │   │       │   ├── 📁 intent/                  # ★ Per-language intent classifiers
│   │   │       │   │   ├── 📄 intent_classifier.yaml      # English base + few-shots
│   │   │       │   │   ├── 📄 intent_classifier_hi.yaml   # Hindi few-shots
│   │   │       │   │   ├── 📄 intent_classifier_mr.yaml   # Marathi few-shots
│   │   │       │   │   ├── 📄 intent_classifier_gu.yaml   # Gujarati few-shots
│   │   │       │   │   ├── 📄 intent_classifier_ta.yaml   # Tamil few-shots
│   │   │       │   │   ├── 📄 intent_classifier_te.yaml   # Telugu few-shots
│   │   │       │   │   └── 📄 intent_classifier_bn.yaml   # Bengali few-shots
│   │   │       │   │
│   │   │       │   ├── 📁 agents/                  # Per-agent task prompts
│   │   │       │   │   ├── 📄 forecast_analysis.yaml
│   │   │       │   │   ├── 📄 pricing_recommendation.yaml
│   │   │       │   │   ├── 📄 inventory_advisory.yaml
│   │   │       │   │   ├── 📄 event_detection.yaml
│   │   │       │   │   └── 📄 explanation_builder.yaml
│   │   │       │   │
│   │   │       │   ├── 📁 response_tone/           # ★ Channel × language tone overlays
│   │   │       │   │   ├── 📄 whatsapp_hi.yaml     # Casual Hindi, short, emojis OK
│   │   │       │   │   ├── 📄 whatsapp_mr.yaml
│   │   │       │   │   ├── 📄 whatsapp_gu.yaml
│   │   │       │   │   ├── 📄 whatsapp_ta.yaml
│   │   │       │   │   ├── 📄 whatsapp_te.yaml
│   │   │       │   │   ├── 📄 whatsapp_bn.yaml
│   │   │       │   │   ├── 📄 web_en.yaml          # Professional English for dashboard
│   │   │       │   │   └── 📄 web_hi.yaml
│   │   │       │   │
│   │   │       │   └── 📁 onboarding/              # ★ Per-language onboarding questions
│   │   │       │       ├── 📄 questions_hi.yaml
│   │   │       │       ├── 📄 questions_mr.yaml
│   │   │       │       ├── 📄 questions_gu.yaml
│   │   │       │       ├── 📄 questions_ta.yaml
│   │   │       │       ├── 📄 questions_te.yaml
│   │   │       │       └── 📄 questions_en.yaml
│   │   │       │
│   │   │       ├── 📁 tools/                      # ── External Tool Wrappers ──────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   │
│   │   │       │   ├── 📁 llm/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 bedrock_client.py        # Claude/Llama via Bedrock boto3
│   │   │       │   │   ├── 📄 model_selector.py        # Pick model by task + cost budget
│   │   │       │   │   └── 📄 structured_output.py     # Pydantic output parsers
│   │   │       │   │
│   │   │       │   ├── 📁 data_sources/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 mongodb_tool.py           # Sales, inventory, store profiles
│   │   │       │   │   ├── 📄 dynamodb_tool.py          # Fast KV: SKU prices, sessions
│   │   │       │   │   ├── 📄 s3_tool.py                # CSV uploads, training data, logs
│   │   │       │   │   ├── 📄 ondc_tool.py              # Competitor prices via ONDC API
│   │   │       │   │   ├── 📄 panchang_tool.py          # Festival calendar + muhurat dates
│   │   │       │   │   └── 📄 weather_tool.py           # Weather API for demand signals
│   │   │       │   │
│   │   │       │   ├── 📁 calculators/
│   │   │       │   │   ├── 📄 __init__.py
│   │   │       │   │   ├── 📄 safety_stock.py
│   │   │       │   │   ├── 📄 reorder_point.py
│   │   │       │   │   ├── 📄 elasticity.py             # Price elasticity of demand
│   │   │       │   │   ├── 📄 event_confidence.py       # Event Confidence Score (0–100)
│   │   │       │   │   ├── 📄 margin_calculator.py      # Gross margin + markdown impact
│   │   │       │   │   └── 📄 what_if_simulator.py      # Revenue/volume/margin simulations
│   │   │       │   │
│   │   │       │   └── 📁 ml/
│   │   │       │       ├── 📄 __init__.py
│   │   │       │       ├── 📄 sagemaker_client.py       # Invoke SageMaker endpoints
│   │   │       │       ├── 📄 prophet_engine.py         # Prophet time-series forecasting
│   │   │       │       ├── 📄 deepar_engine.py          # DeepAR multi-SKU forecasting
│   │   │       │       └── 📄 ensemble.py               # Weighted model ensemble
│   │   │       │
│   │   │       ├── 📁 memory/                     # ── Memory & Persistence ────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 conversation.py          # Short-term: in-graph message history
│   │   │       │   ├── 📄 vector_store.py          # Long-term: MongoDB Atlas Vector / FAISS
│   │   │       │   ├── 📄 profile_store.py         # Store profile, preferences, onboarding
│   │   │       │   ├── 📄 session_store.py         # Redis-backed session manager
│   │   │       │   └── 📄 policies.py              # TTL, truncation, privacy/DPDP rules
│   │   │       │
│   │   │       ├── 📁 knowledge_base/             # ── Domain Knowledge (static) ───
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📁 festivals/
│   │   │       │   │   ├── 📄 national.json         # Diwali, Holi, Eid, Christmas, Navratri
│   │   │       │   │   ├── 📄 regional_mh.json      # Ganesh Chaturthi, Gudi Padwa, Rang Panchami
│   │   │       │   │   ├── 📄 regional_gj.json      # Uttarayan, Navratri, Dhuleti
│   │   │       │   │   ├── 📄 regional_tn.json      # Pongal, Karthigai, Chithirai
│   │   │       │   │   ├── 📄 regional_ap_ts.json   # Ugadi, Sankranti, Bonalu
│   │   │       │   │   ├── 📄 regional_wb.json      # Durga Puja, Poila Boishakh
│   │   │       │   │   └── 📄 panchang_2026.json    # Pre-computed muhurat + tithi dates
│   │   │       │   ├── 📁 sku_categories/
│   │   │       │   │   ├── 📄 festival_sku_map.json # Festival → high-demand SKU list
│   │   │       │   │   └── 📄 seasonal_sku_map.json # Season → demand patterns
│   │   │       │   └── 📁 intents/
│   │   │       │       ├── 📄 intent_taxonomy.json      # All intents + aliases per language
│   │   │       │       ├── 📄 intent_examples_hi.json   # Hindi few-shot examples
│   │   │       │       ├── 📄 intent_examples_mr.json
│   │   │       │       ├── 📄 intent_examples_gu.json
│   │   │       │       ├── 📄 intent_examples_ta.json
│   │   │       │       └── 📄 intent_examples_te.json
│   │   │       │
│   │   │       ├── 📁 schemas/                    # ── Pydantic Models ─────────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 chat.py                  # ChatRequest, ChatResponse
│   │   │       │   ├── 📄 webhook.py               # WhatsAppWebhookPayload, WebhookAck
│   │   │       │   ├── 📄 onboarding.py            # OnboardingSession, StoreMetadata
│   │   │       │   ├── 📄 forecast.py              # ForecastRequest, ForecastResult
│   │   │       │   ├── 📄 pricing.py               # PricingRequest, PriceRecommendation
│   │   │       │   ├── 📄 inventory.py             # InventoryQuery, ReorderAlert
│   │   │       │   ├── 📄 language.py              # LanguageContext, SupportedLanguage enum
│   │   │       │   └── 📄 events.py                # FestivalEvent, EventConfidenceScore
│   │   │       │
│   │   │       ├── 📁 config/                     # ── Configuration ───────────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 settings.py              # Pydantic BaseSettings (all env vars)
│   │   │       │   ├── 📄 logging.py               # Structlog config
│   │   │       │   ├── 📄 languages.py             # SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
│   │   │       │   └── 📄 constants.py             # App-wide constants
│   │   │       │
│   │   │       ├── 📁 monitoring/                 # ── Observability ───────────────
│   │   │       │   ├── 📄 __init__.py
│   │   │       │   ├── 📄 tracing.py               # OTel spans: every node + tool + LLM call
│   │   │       │   ├── 📄 metrics.py               # Prometheus: latency, tokens, confidence
│   │   │       │   ├── 📄 langsmith.py             # LangSmith full trace integration
│   │   │       │   └── 📄 audit_log.py             # Explainability: log every agent decision
│   │   │       │
│   │   │       └── 📁 utils/                      # ── Shared Utilities ────────────
│   │   │           ├── 📄 __init__.py
│   │   │           ├── 📄 ids.py                   # session_id / request_id / store_id helpers
│   │   │           ├── 📄 time.py                  # IST timezone, festival window helpers
│   │   │           ├── 📄 retry.py                 # Exponential backoff decorators
│   │   │           ├── 📄 serialization.py         # JSON / Pydantic serializers
│   │   │           └── 📄 exceptions.py            # Custom exception hierarchy
│   │   │
│   │   └── 📁 tests/
│   │       ├── 📄 conftest.py                     # Fixtures: mock graph, Bedrock, Bhashini
│   │       ├── 📁 unit/
│   │       │   ├── 📄 test_language_detector.py
│   │       │   ├── 📄 test_intent_router.py
│   │       │   ├── 📄 test_event_confidence.py
│   │       │   ├── 📄 test_pricing_processor.py
│   │       │   ├── 📄 test_forecast_processor.py
│   ��       │   ├── 📄 test_whatsapp_mapper.py
│   │       │   └── 📄 test_bhashini_client.py
│   │       ├── 📁 integration/
│   │       │   ├── 📄 test_retail_assistant_graph.py
│   │       │   ├── 📄 test_onboarding_graph.py
│   │       │   ├── 📄 test_whatsapp_webhook_flow.py
│   │       │   └── 📄 test_multilingual_roundtrip.py
│   │       └── 📁 e2e/
│   │           ├── 📄 test_holi_demand_forecast.py
│   │           ├── 📄 test_profit_query_hi.py
│   │           ├── 📄 test_pricing_intelligence.py
│   │           └── 📄 test_onboarding_to_dashboard.py
│   │
│   ├── 📁 shared/                                 # Node.js shared libs
│   │   ├── 📁 constants/
│   │   │   ├── error-codes.js
│   │   │   ├── event-types.js
│   │   │   └── languages.js
│   │   ├── 📁 utils/
│   │   │   ├── logger.js
│   │   │   ├── metrics.js
│   │   │   ├── date-utils.js
│   │   │   └── math-utils.js
│   │   ├── 📁 validators/
│   │   │   ├── schemas.js
│   │   │   └── validation.js
│   │   ├── 📁 clients/
│   │   │   ├── mongodb.client.js
│   │   │   ├── redis.client.js
│   │   │   ├── sqs.client.js
│   │   │   └── s3.client.js
│   │   └── 📁 types/
│   │       └── index.d.ts
│   │
│   ├── 📁 database/
│   │   ├── 📁 migrations/
│   │   │   ├── 001-initial-schema.js
│   │   │   ├── 002-add-indexes.js
│   │   │   └── 003-add-event-collection.js
│   │   ├── 📁 seeds/
│   │   │   ├── dev/
│   │   │   │   ├── stores.seed.js
│   │   │   │   └── events.seed.js
│   │   │   └── prod/
│   │   │       └── default-data.seed.js
│   │   └── 📁 scripts/
│   │       ├── backup.js
│   │       ├── restore.js
│   │       └── optimize.js
│   │
│   └── 📁 scripts/
│       ├── health-check.js
│       ├── load-test.js
│       └── benchmark.js
│
│
├── 🎨 frontend/
│   └── 📁 web/
│       ├── public/
│       │   ├── index.html
│       │   ├── manifest.json
│       │   └── robots.txt
│       └── src/
│           ├── 📁 assets/
│           │   ├── images/
│           │   ├── fonts/
│           │   └── icons/
│           ├── 📁 components/
│           │   ├── common/
│           │   │   ├── Button/
│           │   │   │   ├── Button.jsx
│           │   │   │   ├── Button.module.css
│           │   │   │   └── index.js
│           │   │   ├── Input/
│           │   │   ├── Modal/
│           │   │   ├── Spinner/
│           │   │   └── Toast/
│           │   ├── layout/
│           │   │   ├── Header/
│           │   │   ├── Sidebar/
│           │   │   └── Footer/
│           │   ├── dashboard/
│           │   │   ├── KPICards/
│           │   │   ├── ForecastChart/
│           │   │   ├── InventoryTable/
│           │   │   └── AlertsPanel/
│           │   ├── chat/                          # ★ NEW: embedded chat widget
│           │   │   ├── ChatWindow/
│           │   │   │   ├── ChatWindow.jsx         # WebSocket consumer → agents /v1/ws
│           │   │   │   ├── ChatWindow.module.css
│           │   │   │   └── index.js
│           │   │   ├── MessageBubble/
│           │   │   │   ├── MessageBubble.jsx
│           │   │   │   └── index.js
│           │   │   ├── TypingIndicator/
│           │   │   │   └── TypingIndicator.jsx
│           │   │   └── QuickReplies/              # Maps to WA-style buttons in web
│           │   │       └── QuickReplies.jsx
│           │   ├── auth/
│           │   │   ├── LoginForm/
│           │   │   └── RegisterForm/
│           │   └── whatsapp/
│           │       ├── ChatSimulator/
│           │       └── TemplatePreview/
│           ├── 📁 pages/
│           │   ├── Landing/
│           │   │   ├── Landing.jsx
│           │   │   └── Landing.module.css
│           │   ├── Dashboard/
│           │   │   ├── BusinessDashboard.jsx
│           │   │   └── PartnerDashboard.jsx
│           │   ├── Forecast/
│           │   │   ├── ForecastView.jsx
│           │   │   └── ForecastDetails.jsx
│           │   ├── Pricing/
│           │   │   ├── PricingView.jsx
│           │   │   └── WhatIfSimulator.jsx
│           │   ├── Inventory/
│           │   │   ├── InventoryList.jsx
│           │   │   └── ReorderView.jsx
│           │   ├── Orders/
│           │   │   ├── OrderList.jsx
│           │   │   └── OrderDetails.jsx
│           │   └── Settings/
│           │       ├── Profile.jsx
│           │       └── StoreSettings.jsx
│           ├── 📁 hooks/
│           │   ├── useAuth.js
│           │   ├── useForecast.js
│           │   ├── useInventory.js
│           │   ├── useChat.js                     # ★ NEW: chat state + WS hook
│           │   └── useWebSocket.js
│           ├── 📁 services/
│           │   ├── api/
│           │   │   ├── client.js
│           │   │   ├── auth.js
│           │   │   ├── forecast.js
│           │   │   ├── pricing.js
│           │   │   ├── orders.js
│           │   │   └── chat.js                    # ★ NEW: POST /v1/chat + SSE /v1/stream
│           │   ├── websocket/
│           │   │   └── index.js                   # WS /v1/ws/{session_id} connection mgr
│           │   └── analytics/
│           │       └── track.js
│           ├── 📁 store/
│           │   ├── slices/
│           │   │   ├── authSlice.js
│           │   │   ├── forecastSlice.js
│           │   │   ├── chatSlice.js               # ★ NEW: chat messages + session state
│           │   │   └── uiSlice.js
│           │   └── index.js
│           ├── 📁 utils/
│           │   ├── formatters.js
│           │   ├── validators.js
│           │   └── constants.js
│           ├── 📁 config/
│           │   └── index.js
│           ├── App.jsx
│           ├── index.js
│           └── routes.js
│
│
└── 📄 README.md 
```
backend/agents/
│
├── 📄 langgraph.json                    # LangGraph deployment config
├── 📄 pyproject.toml                    # Package + dependency management
├── 📄 requirements.txt
├── 📄 requirements-dev.txt
├── 📄 Dockerfile.agents
├── 📄 .env.example
├── 📄 README.md
│
├── 📁 src/
│   └── 📁 ai_sahayak/
│       │
│       ├── 📄 __init__.py
│       ├── 📄 main.py                   # FastAPI app entry point
│       │
│       ├── 📁 api/                      # ─── HTTP Layer ───────────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 server.py             # FastAPI app factory + middleware + lifespan
│       │   ├── 📄 deps.py               # Shared FastAPI dependencies (DB, graph registry)
│       │   │
│       │   ├── 📁 routes/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 health.py         # GET /health, GET /ready, GET /metrics
│       │   │   ├── 📄 chat.py           # POST /v1/chat (web chatbot, sync)
│       │   │   ├── 📄 stream.py         # POST /v1/stream (SSE for web UI)
│       │   │   ├── 📄 websocket.py      # WS /v1/ws/{session_id} (real-time)
│       │   │   ├── 📄 webhook_whatsapp.py  # POST /v1/webhooks/whatsapp
│       │   │   ├── 📄 onboarding.py     # POST /v1/onboarding (store setup)
│       │   │   └── 📄 admin.py          # GET /v1/sessions, /v1/graphs (debug)
│       │   │
│       │   └── 📁 middleware/
│       │       ├── 📄 __init__.py
│       │       ├── 📄 auth.py           # Verify internal service tokens
│       │       ├── 📄 logging.py        # Request/response structured logging
│       │       ├── 📄 tracing.py        # OpenTelemetry request tracing
│       │       └── 📄 rate_limit.py     # Per-store rate limiting
│       │
│       ├── 📁 channels/                 # ─── Channel Adapters ─────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 base.py               # BaseChannelAdapter (abstract)
│       │   ├── 📄 models.py             # AgentRequest, AgentResponse, Channel enum
│       │   │
│       │   ├── 📁 whatsapp/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 mapper.py         # Meta webhook payload → AgentRequest
│       │   │   ├── 📄 formatter.py      # AgentResponse → WA buttons/text/lists
│       │   │   ├── 📄 outbound.py       # Sends reply back to Meta API
│       │   │   ├── 📄 verifier.py       # HMAC signature verification
│       │   │   └── 📄 templates.py      # WA message template builders
│       │   │
│       │   └── 📁 web/
│       │       ├── 📄 __init__.py
│       │       ├── 📄 mapper.py         # Web chat payload → AgentRequest
│       │       ├── 📄 formatter.py      # AgentResponse → JSON for frontend
│       │       └── 📄 streaming.py      # SSE / WebSocket streaming helpers
│       │
│       ├── 📁 graphs/                   # ─── LangGraph Core ───────────────────
│       │   ├── 📄 __init__.py
│       │   │
│       │   ├── 📁 state/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 conversation.py   # ConversationState (main TypedDict)
│       │   │   ├── 📄 user_context.py   # UserContext: store_id, language, region
│       │   │   ├── 📄 agent_state.py    # Per-agent scratchpad state
│       │   │   └── 📄 reducers.py       # Custom state merge reducers
│       │   │
│       │   ├── 📁 workflows/            # Top-level compiled graphs
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 retail_assistant.py    # Main copilot graph (entry point)
│       │   │   ├── 📄 onboarding.py          # Onboarding Q&A → store metadata
│       │   │   ├── 📄 forecast.py            # Festival demand forecasting graph
│       │   │   ├── 📄 pricing.py             # Price intelligence graph
│       │   │   ├── 📄 inventory.py           # Stock / reorder advisory graph
│       │   │   └── 📄 alert.py               # Proactive alert generation graph
│       │   │
│       │   ├── 📁 nodes/                # Individual node functions
│       │   │   ├── 📄 __init__.py
│       │   │   │
│       │   │   ├── 📁 language/         # ★ Multilingual core
│       │   │   │   ├── 📄 __init__.py
│       │   │   │   ├── 📄 detector.py   # Detects lang from input text
│       │   │   │   ├── 📄 normalizer.py # Hinglish/code-mix normalization
│       │   │   │   ├── 📄 translator.py # Input → English (internal)
│       │   │   │   └── 📄 localizer.py  # English output → user's language
│       │   │   │
│       │   │   ├── 📁 router/
│       │   │   │   ├── 📄 __init__.py
│       │   │   │   ├── 📄 intent_router.py      # Intent detection + classification
│       │   │   │   ├── 📄 workflow_router.py     # Routes to sub-graph
│       │   │   │   └── 📄 channel_router.py      # Channel-specific post-processing
│       │   │   │
│       │   │   ├── 📁 planners/
│       │   │   │   ├── 📄 __init__.py
│       │   │   │   ├── 📄 forecast_planner.py
│       │   │   │   ├── 📄 pricing_planner.py
│       │   │   │   ├── 📄 inventory_planner.py
│       │   │   │   └── 📄 onboarding_planner.py
│       │   │   │
│       │   │   ├── 📁 retrievers/
│       │   │   │   ├── 📄 __init__.py
│       │   │   │   ├── 📄 sales_retriever.py      # Historical sales from MongoDB
│       │   │   │   ├── 📄 inventory_retriever.py
│       │   │   │   ├── 📄 events_retriever.py     # Festival/panchang events
│       │   │   │   ├── 📄 competitor_retriever.py # ONDC pricing data
│       │   │   │   └── 📄 profile_retriever.py    # Store profile + preferences
│       │   │   │
│       │   │   ├── 📁 processors/
│       │   │   │   ├── 📄 __init__.py
│       │   │   │   ├── 📄 forecast_processor.py   # Demand prediction logic
│       │   │   │   ├── 📄 event_processor.py      # Event confidence score calc
│       │   │   │   ├── 📄 pricing_processor.py    # Price band optimization
│       │   │   │   ├── 📄 inventory_processor.py  # Safety stock, reorder calc
│       │   │   │   ├── 📄 onboarding_processor.py # Store metadata builder
│       │   │   │   └── 📄 explanation_processor.py# Explainable AI reasoning
│       │   │   │
│       │   │   ├── 📁 responders/
│       │   │   │   ├── 📄 __init__.py
│       │   │   │   ├── 📄 response_builder.py     # Final answer assembly
│       │   │   │   ├── 📄 interactive.py          # Buttons, quick replies, lists
│       │   │   │   └── 📄 fallback.py             # Graceful fallback responses
│       │   │   │
│       │   │   ├── 📁 validators/
│       │   │   │   ├── 📄 __init__.py
│       │   │   │   ├── 📄 input_validator.py      # Sanitize + schema check inputs
│       │   │   │   └── 📄 output_validator.py     # Validate agent outputs
│       │   │   │
│       │   │   └── 📁 system/
│       │   │       ├── 📄 __init__.py
│       │   │       ├── 📄 error_handler.py
│       │   │       └── 📄 audit_logger.py         # Decision audit trail
│       │   │
│       │   ├── 📁 edges/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📁 conditional/
│       │   │   │   ├── 📄 confidence_router.py    # Route by confidence score
│       │   │   │   ├── 📄 language_router.py      # Re-route if lang changed mid-conv
│       │   │   │   ├── 📄 fallback_router.py      # Low confidence → fallback
│       │   │   │   └── 📄 safety_router.py        # Guardrails / policy check
│       │   │   └── 📁 dynamic/
│       │   │       ├── 📄 next_step_router.py
│       │   │       └── 📄 planner_tool_router.py
│       │   │
│       │   └── 📁 runtime/
│       │       ├── 📄 __init__.py
│       │       ├── 📄 executor.py          # run_graph(), arun_graph(), stream_graph()
│       │       ├── 📄 registry.py          # Graph version registry + factory
│       │       ├── 📄 checkpointer.py      # LangGraph checkpointer (MongoDB/Redis)
│       │       ├── 📄 streaming.py         # astream_events wrapper
│       │       └── 📄 policies.py          # Timeouts, max hops, retry budgets
│       │
│       ├── 📁 language/                 # ─── Multilingual Engine ──────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 constants.py          # Language codes, locale map, script map
│       │   │
│       │   ├── 📁 detection/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 detector.py       # langdetect + custom heuristics
│       │   │   ├── 📄 script_detector.py# Devanagari / Gujarati / Tamil script ID
│       │   │   └── 📄 hinglish.py       # Roman-script Hinglish detection
│       │   │
│       │   ├── 📁 translation/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 bhashini_client.py # Bhashini ULCA API wrapper
│       │   │   ├── 📄 pipeline.py        # ASR → NMT → TTS pipeline builder
│       │   │   └── 📄 fallback.py        # Bedrock as translation fallback
│       │   │
│       │   ├── 📁 normalization/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 code_mix.py        # Hinglish, Tanglish, Manglish cleaner
│       │   │   ├── 📄 numerals.py        # ₹, numbers in regional scripts → int
│       │   │   └── 📄 dates.py           # "agle mahine", "Diwali ke baad" → date
│       │   │
│       │   └── 📁 localization/
│       │       ├── 📄 __init__.py
│       │       ├── 📄 formatter.py       # Format numbers, currency, dates per locale
│       │       ├── 📄 tone_adapter.py    # Formal/informal tone per language
│       │       └── 📄 locale_map.py      # State → lang → festivals → calendar
│       │
│       ├── 📁 prompts/                  # ─── Prompt Library ───────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 registry.py           # PromptRegistry: load by name + lang
│       │   ├── 📄 loader.py             # Load .yaml / .txt files + version them
│       │   │
│       │   ├── 📁 system/               # Core system prompts
│       │   │   ├── 📄 retail_assistant.yaml
│       │   │   ├── 📄 onboarding_agent.yaml
│       │   │   ├── 📄 forecast_agent.yaml
│       │   │   ├── 📄 pricing_agent.yaml
│       │   │   └── 📄 inventory_agent.yaml
│       │   │
│       │   ├── 📁 intent/               # Intent detection prompts
│       │   │   ├── 📄 intent_classifier.yaml      # English base
│       │   │   ├── 📄 intent_classifier_hi.yaml   # Hindi override
│       │   │   ├── 📄 intent_classifier_mr.yaml   # Marathi override
│       │   │   ├── 📄 intent_classifier_gu.yaml   # Gujarati override
│       │   │   ├── 📄 intent_classifier_ta.yaml   # Tamil override
│       │   │   ├── 📄 intent_classifier_te.yaml   # Telugu override
│       │   │   └── 📄 intent_classifier_bn.yaml   # Bengali override
│       │   │
│       │   ├── 📁 agents/               # Per-agent task prompts
│       │   │   ├── 📄 forecast_analysis.yaml
│       │   │   ├── 📄 pricing_recommendation.yaml
│       │   │   ├── 📄 inventory_advisory.yaml
│       │   │   ├── 📄 event_detection.yaml
│       │   │   └── 📄 explanation_builder.yaml
│       │   │
│       │   ├── 📁 response_tone/        # Channel + language tone overlays
│       │   │   ├── 📄 whatsapp_hi.yaml  # Casual Hindi, short sentences, emojis
│       │   │   ├── 📄 whatsapp_mr.yaml
│       │   │   ├── 📄 whatsapp_gu.yaml
│       │   │   ├── 📄 whatsapp_ta.yaml
│       │   │   ├── 📄 whatsapp_te.yaml
│       │   │   ├── 📄 whatsapp_bn.yaml
│       │   │   ├── 📄 web_en.yaml       # Professional English for dashboard
│       │   │   └── 📄 web_hi.yaml
│       │   │
│       │   └── 📁 onboarding/
│       │       ├── 📄 questions_hi.yaml
│       │       ├── 📄 questions_mr.yaml
│       │       ├── 📄 questions_gu.yaml
│       │       ├── 📄 questions_ta.yaml
│       │       ├── 📄 questions_te.yaml
│       │       └── 📄 questions_en.yaml
│       │
│       ├── 📁 tools/                    # ─── External Tool Wrappers ───────────
│       │   ├── 📄 __init__.py
│       │   │
│       │   ├── 📁 llm/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 bedrock_client.py     # Bedrock: Claude/Llama via boto3
│       │   │   ├── 📄 model_selector.py     # Pick model by task + cost budget
│       │   │   └── 📄 structured_output.py  # Pydantic output parsers
│       │   │
│       │   ├── 📁 data_sources/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 mongodb_tool.py        # Sales, inventory, store data
│       │   │   ├── 📄 dynamodb_tool.py       # Fast KV lookups (SKU, prices)
│       │   │   ├── 📄 s3_tool.py             # CSV uploads, training data
│       │   │   ├── 📄 ondc_tool.py           # Competitor prices via ONDC
│       │   │   ├── 📄 panchang_tool.py       # Festival calendar, muhurat dates
│       │   │   └── 📄 weather_tool.py        # Weather API for demand signals
│       │   │
│       │   ├── 📁 calculators/
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 safety_stock.py        # Safety stock formula
│       │   │   ├── 📄 reorder_point.py       # ROP = (avg daily demand × lead time)
│       │   │   ├── 📄 elasticity.py          # Price elasticity of demand
│       │   │   ├── 📄 event_confidence.py    # Event Confidence Score (0-100)
│       │   │   ├── 📄 margin_calculator.py   # Gross margin, markdown impact
│       │   │   └── 📄 what_if_simulator.py   # Revenue/volume/margin simulations
│       │   │
│       │   └── 📁 ml/
│       │       ├── 📄 __init__.py
│       │       ├── 📄 sagemaker_client.py    # Invoke SageMaker endpoints
│       │       ├── 📄 prophet_engine.py      # Prophet time-series forecasting
│       │       ├── 📄 deepar_engine.py       # DeepAR for multi-SKU forecasting
│       │       └── 📄 ensemble.py            # Weighted ensemble of ML models
│       │
│       ├── 📁 memory/                   # ─── Memory & Persistence ─────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 conversation.py       # Short-term: in-graph message history
│       │   ├── 📄 vector_store.py       # Long-term: MongoDB Atlas Vector / FAISS
│       │   ├── 📄 profile_store.py      # Store profile, preferences, onboarding
│       │   ├── 📄 session_store.py      # Redis-backed session manager
│       │   └── 📄 policies.py           # TTL, truncation, privacy rules
│       │
│       ├── 📁 schemas/                  # ─── Pydantic Models ──────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 chat.py               # ChatRequest, ChatResponse
│       │   ├── 📄 webhook.py            # WhatsAppWebhookPayload, WebhookAck
│       │   ├── 📄 onboarding.py         # OnboardingSession, StoreMetadata
│       │   ├── 📄 forecast.py           # ForecastRequest, ForecastResult
│       │   ├── 📄 pricing.py            # PricingRequest, PriceRecommendation
│       │   ├── 📄 inventory.py          # InventoryQuery, ReorderAlert
│       │   ├── 📄 language.py           # LanguageContext, SupportedLanguage enum
│       │   └── 📄 events.py             # FestivalEvent, EventConfidenceScore
│       │
│       ├── 📁 knowledge_base/           # ─── Domain Knowledge ─────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📁 festivals/
│       │   │   ├── 📄 national.json     # Diwali, Holi, Eid, Christmas, Navratri
│       │   │   ├── 📄 regional_mh.json  # Maharashtra: Ganesh Chaturthi, Gudi Padwa
│       │   │   ├── 📄 regional_gj.json  # Gujarat: Uttarayan, Navratri
│       │   │   ├── 📄 regional_tn.json  # Tamil Nadu: Pongal, Karthigai
│       │   │   ├── 📄 regional_ap_ts.json # AP/Telangana: Ugadi, Sankranti
│       │   │   ├── 📄 regional_wb.json  # West Bengal: Durga Puja, Poila Boishakh
│       │   │   └── 📄 panchang_2026.json# Pre-computed muhurat + dates
│       │   ├── 📁 sku_categories/
│       │   │   ├── 📄 festival_sku_map.json  # Festival → high-demand SKUs
│       │   │   └── 📄 seasonal_sku_map.json  # Season → demand patterns
│       │   └── 📁 intents/
│       │       ├── 📄 intent_taxonomy.json   # All supported intents + aliases
│       │       └── 📄 intent_examples_hi.json# Hindi few-shot examples per intent
│       │
│       ├── 📁 config/                   # ─── Configuration ────────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 settings.py           # Pydantic BaseSettings (all env vars)
│       │   ├── 📄 logging.py            # Structlog config
│       │   ├── 📄 languages.py          # SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
│       │   └── 📄 constants.py          # App-wide constants
│       │
│       ├── 📁 monitoring/               # ─── Observability ────────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 tracing.py            # OpenTelemetry spans: node, tool, LLM
│       │   ├── 📄 metrics.py            # Prometheus: latency, token usage, etc.
│       │   ├── 📄 langsmith.py          # LangSmith tracing integration
│       │   └── 📄 audit_log.py          # Explainability: log every decision
│       │
│       └── 📁 utils/                    # ─── Shared Utilities ─────────────────
│           ├── 📄 __init__.py
│           ├── 📄 ids.py                # session_id, request_id, store_id helpers
│           ├── 📄 time.py               # IST timezone, festival window helpers
│           ├── 📄 retry.py              # Exponential backoff decorators
│           ├── 📄 serialization.py      # JSON / Pydantic serializers
│           └── 📄 exceptions.py         # Custom exception hierarchy
│
└── 📁 tests/
    ├── 📄 conftest.py                   # Fixtures: mock graph, mock Bedrock, etc.
    ├── 📁 unit/
    │   ├── 📄 test_language_detector.py
    │   ├── 📄 test_intent_router.py
    │   ├── 📄 test_event_confidence.py
    │   ├── 📄 test_pricing_processor.py
    │   ├── 📄 test_forecast_processor.py
    │   ├── 📄 test_whatsapp_mapper.py
    │   └── 📄 test_bhashini_client.py
    ├── 📁 integration/
    │   ├── 📄 test_retail_assistant_graph.py
    │   ├── 📄 test_onboarding_graph.py
    │   ├── 📄 test_whatsapp_webhook_flow.py
    │   └── 📄 test_multilingual_roundtrip.py  # Hindi/Marathi/Gujarati full round trips
    └── 📁 e2e/
        ├── 📄 test_holi_demand_forecast.py    # Proactive alert scenario
        ├── 📄 test_profit_query_hi.py         # "Next month kitna profit hoga?"
        ├── 📄 test_pricing_intelligence.py    # ONDC competitor flow
        └── 📄 test_onboarding_to_dashboard.py # Full new user journey 
```

Now you're ready to build this for the hackathon! 🚀

**Good luck!** 🎉

---

*Document Version: 1.0*
*Last Updated: February 2024*
*For: AWS AI for Bharat Hackathon*