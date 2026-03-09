# AI Sahayak — Full Demo Script (~2 min 45 sec)

**Total runtime:** ~2:45  
**Structure:** 20s Intro (AI video) → ~2:05 UI walkthrough → 20s Closing (AI video)

---

## PART 1 — INTRODUCTORY PHASE (0:00 – 0:20)  
*[Attach your AI-generated story-building video here]*

**Suggested voiceover / on-screen text for your intro video:**
- India’s 12–15 million MSMEs lose upwards of ₹15,000+ every festive season — not because they don’t work hard, but because they’re forced to react too late.
- AI Sahayak flips that: from reactive to **proactive**. We tell the shopkeeper what they need to know — before they have to ask.
- Built for AWS AI for Bharat: WhatsApp onboarding, live alerts, demand forecasting, and pricing that speaks in Hinglish.

*[End intro video; cut to browser/app]*

---

## PART 2 — UI WALKTHROUGH (0:20 – 2:25)

### 0:20 – 0:22 — Logo meaning
*[Show splash screen or logo card]*
- “First, what our logo means for Bharat: Green — growth and trust for India’s 12 million-plus MSMEs. Amber and saffron — the helping hand, the *Sahayak*. Our promise: we’re your quiet co-pilot, surfacing the right insight before the festival, before the rush.”

### 0:22 – 0:33 — Home page
*[Landing / home]*
- “This is the AI Sahayak home. Proactive intelligence for Indian kirana and MSMEs. We’ll see onboarding over WhatsApp, then the dashboard and the proactive loop.”

### 0:33 – 1:03 — Onboarding via chat (WhatsApp Cloud API)
*[WhatsApp / chat onboarding flow]*
- “Onboarding is frictionless — no app download. The bot says *Namaste*, asks for language: English, Hindi, or Hinglish.”
- “Vedika enters her store name — ‘vedika book shop’ — category ‘stationary’, pincode. The system parses natural language into structured data.”
- “For KYC it asks for GST or Aadhar. Once validated, we auto-provision a User ID and password for the web dashboard — so the shopkeeper moves from WhatsApp to the command centre without any forms.”

### 1:03 – 1:08 — Cognito: onboarded user
*[AWS Console → Cognito User Pools]*
- “In AWS Cognito we see Vedika’s profile — created the moment she completed WhatsApp registration. One identity, one place to sign in.”

### 1:08 – 1:13 — DynamoDB: state and history
*[DynamoDB tables]*
- “DynamoDB holds the state: *ai_sahayak_user_info*, *ai_sahayak_stores*, and *ai_sahayak_conversation_history*. Session IDs, user inputs, store details — everything the LLM needs for context.”

### 1:13 – 1:14 — Logout (one of five users)
*[Log out from current user]*
- “We have five demo retailers. Here we log out so we can show the dashboard as a different user.”

### 1:14 – 1:26 — Dashboard overview tab
*[React dashboard — Overview tab]*
- “The React command centre pulls live data: hundreds of thousands of transactions, dozens of SKUs. Top metrics — 30-day revenue, net profit, sell-through — give the owner a single view of the business.”

### 1:26 – 1:39 — Pricing Studio (DeepAR + Bedrock)
*[Select a SKU e.g. Sugar 1kg; show candidate prices and explanation]*
- “In Pricing Studio we pick a SKU — say Sugar 1kg. SageMaker and Bedrock together suggest a ladder: Aggressive, Base, and Recommended.”
- “*Open Full Explanation* shows Bedrock’s plain-language rationale: procurement cost, target margin, competitor context. So the owner gets a clear, data-driven reason for the recommended price.”

### 1:39 – 1:52 — What-If simulation (NLP engine)
*[What-If box; type a scenario]*
- “The What-If engine takes natural language. Example: ‘For Diwali week, market price of Ghee 500ml is 510, my inventory is only 2 days, suggest best price with 12% promo.’”
- “The system parses that into a structured payload — competitor price, promo depth, inventory days — and Bedrock plus SageMaker recompute on the fly: hold stock, react to competitor, or defend share.”

### 1:52 – 2:20 — Proactive edge & WhatsApp loop
*[Back to WhatsApp / My Day chat]*
- “We close the loop on WhatsApp. The owner asks: *Aaj sales kaise chal rahe hain? Sugar price, SKU count.*”
- “The bot pulls live data from DynamoDB: units sold, sales value, active SKU count.”
- “And it doesn’t just answer — it **proactively** warns: for example, 9 SKUs like Mustard Oil and Ghee are below reorder point. So the owner acts before stockout. That’s proactive over reactive.”

### 2:20 – 2:25 — Handoff to closing
*[Brief hold on dashboard or chat]*
- “That’s AI Sahayak: WhatsApp onboarding, Cognito and DynamoDB in the cloud, a React command centre with pricing and What-If, and alerts that reach the shopkeeper where they already are.”

---

## PART 3 — CLOSING PHASE (2:25 – 2:45)  
*[Attach your AI-generated closing video here]*

**Suggested voiceover / on-screen text for your closing video:**
- From reactive to proactive — one message at a time.
- AI Sahayak: built for Bharat, powered by AWS.
- Thank you.

*[End demo]*

---

## Quick reference — timings

| Start | End  | Section                    |
|-------|------|----------------------------|
| 0:00  | 0:20 | Intro (AI video)           |
| 0:20  | 0:22 | Logo meaning               |
| 0:22  | 0:33 | Home page                  |
| 0:33  | 1:03 | Onboarding via chat        |
| 1:03  | 1:08 | Cognito                    |
| 1:08  | 1:13 | DynamoDB                   |
| 1:13  | 1:14 | Logout (5 users)           |
| 1:14  | 1:26 | Dashboard overview         |
| 1:26  | 1:39 | Pricing Studio             |
| 1:39  | 1:52 | What-If engine             |
| 1:52  | 2:20 | Proactive edge & WhatsApp  |
| 2:20  | 2:25 | Handoff                    |
| 2:25  | 2:45 | Closing (AI video)         |

---

*Script aligned to your timestamps and technical walkthrough. Trim or stretch individual lines to match your actual recording pace.*
