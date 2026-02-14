# Requirements Document: AI Sahayak

## Introduction

AI Sahayak is an AI-Powered Retail Intelligence platform designed specifically for Bharat MSMEs (Micro, Small, and Medium Enterprises). The system provides proactive, hyper-local demand forecasting, pricing intelligence, and inventory optimization by leveraging cultural events, festivals, and regional life-events. Built on AWS serverless architecture, it delivers multilingual conversational AI assistance, predictive analytics, and actionable insights to help small retailers maximize revenue and minimize waste.

The platform operates through two primary interaction modes:

**Scenario A: Proactive Alerts (AI-Initiated)**
The system automatically detects upcoming events and initiates intelligent alerts. For example:
- AWS Change Calendar detects "Holi is 10 days away"
- EventBridge wakes up the system
- SageMaker analyzes historical data and predicts a 40% spike in Gulal demand
- Bedrock crafts a multilingual alert: "Holi is coming! Order 20kg Gulal?"
- Alert is sent via WhatsApp, SMS, and in-app notification
- User can confirm order via WhatsApp or open Amplify mobile app for detailed analysis

**Scenario B: Reactive Queries (User-Initiated)**
Retailers can ask business questions and receive intelligent answers. For example:
- User sends WhatsApp voice note: "Next month Xtra profit hoga?" (Hindi)
- Bhashini translates to English and detects intent: profit forecast
- Lambda queries DynamoDB for current data and SageMaker for predictions
- Bedrock generates response: "Estimated profit is ₹45,000"
- Response is translated back to Hindi and sent via WhatsApp
- User can open Amplify web app for detailed charts and breakdown

This conversational, event-driven approach makes advanced retail intelligence accessible to small business owners who may not be tech-savvy, enabling them to compete effectively in the modern retail landscape.

## Glossary

- **AI_Sahayak**: The complete AI-Powered Retail Intelligence platform
- **Generative_AI_Layer**: Amazon Bedrock-based conversational AI system with multilingual support
- **Forecasting_Engine**: Amazon SageMaker-based time-series forecasting and demand prediction system
- **Event_Engine**: AWS-based proactive event detection and alerting system using Change Calendar and EventBridge
- **Knowledge_Base**: Amazon Bedrock Knowledge Base containing Panchang data, cultural events, and festival information
- **Bhashini_Integration**: Indian language translation service integrated via AWS Lambda, with ngrok tunneling for external API access
- **Translate_Box**: The ngrok-based tunneling service that enables secure communication between AWS Lambda and Bhashini external APIs
- **SKU**: Stock Keeping Unit - individual product identifier
- **Event_Confidence_Score**: Numerical score (0-1) indicating likelihood and impact of a regional event
- **Elasticity_Simulation**: Price sensitivity analysis for demand prediction
- **Promo_ROI_Guard**: System that validates promotional campaign profitability
- **ONDC**: Open Network for Digital Commerce
- **Udhaar**: Credit or informal lending system common in Indian retail
- **Digital_Panchang**: AWS Systems Manager Change Calendar containing Indian calendar events
- **MSME**: Micro, Small, and Medium Enterprise
- **Sachet_AI**: Micro-subscription pricing model for pay-per-event access
- **AR_Assistant**: Augmented Reality shelf optimization tool
- **Lite_Mode**: Low-bandwidth optimized interface for 2G/3G networks
- **Proactive_Alert**: AI-initiated notification triggered by event detection (Scenario A)
- **Reactive_Query**: User-initiated question answered by the AI system (Scenario B)

## Requirements

### Requirement 1: Multilingual Conversational AI Assistant

**User Story:** As an MSME retailer, I want to interact with the system in my native language using voice or text through multiple channels including WhatsApp, so that I can easily access insights without language barriers.

#### Acceptance Criteria

1. WHEN a user initiates a voice query via WhatsApp voice note or web/mobile app, THE Generative_AI_Layer SHALL process the input within 3 seconds
2. WHEN a user speaks in Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, or English, THE Bhashini_Integration SHALL translate the input to English for processing
3. WHEN the Generative_AI_Layer generates a response, THE Bhashini_Integration SHALL translate the output back to the user's preferred language
4. WHEN a user asks about festival demand, THE Generative_AI_Layer SHALL query the Knowledge_Base for relevant Panchang data
5. THE Generative_AI_Layer SHALL use Claude 3 or Llama 3 models via Amazon Bedrock
6. WHEN network bandwidth is below 3G speeds, THE AI_Sahayak SHALL switch to Lite_Mode with text-only responses
7. WHEN a user sends a text or voice query via WhatsApp, THE AI_Sahayak SHALL process it and respond through the same WhatsApp channel

### Requirement 1A: Bhashini Translation Integration Architecture

**User Story:** As a system architect, I want secure and reliable integration with Bhashini translation services, so that multilingual processing works seamlessly across all channels.

#### Acceptance Criteria

1. THE Bhashini_Integration SHALL use AWS Lambda functions to communicate with Bhashini external APIs
2. WHEN Bhashini APIs require external access, THE Translate_Box SHALL use ngrok or similar tunneling service to enable secure communication
3. THE Bhashini_Integration SHALL handle both text translation and voice transcription through the same integration layer
4. WHEN Bhashini service is unavailable, THE AI_Sahayak SHALL fallback to cached translations or English-only mode
5. THE Bhashini_Integration SHALL log all translation requests and responses for quality monitoring
6. THE Translate_Box SHALL maintain secure credentials and API keys in AWS Secrets Manager
7. WHEN translation latency exceeds 2 seconds, THE Bhashini_Integration SHALL log a performance warning

### Requirement 2: Proactive Life-Event Detection and AI-Initiated Alerts

**User Story:** As an MSME retailer, I want the system to automatically detect upcoming cultural events and festivals relevant to my region and proactively alert me with specific recommendations, so that I can prepare inventory without constantly monitoring the system.

#### Acceptance Criteria

1. THE Event_Engine SHALL use AWS Change Calendar (Digital_Panchang) as the primary trigger for event detection
2. WHEN AWS Change Calendar detects an upcoming event (e.g., "Holi is 10 days away"), THE Event_Engine SHALL automatically wake up via Amazon EventBridge
3. WHEN a regional event is detected, THE Event_Engine SHALL calculate an Event_Confidence_Score based on historical sales data, regional demographics, and event significance
4. THE Event_Confidence_Score SHALL be a value between 0 and 1, where 1 indicates highest confidence
5. WHEN an Event_Confidence_Score exceeds 0.7, THE Event_Engine SHALL trigger the Forecasting_Engine to analyze S3 historical data and predict demand spikes
6. WHEN demand analysis is complete, THE Generative_AI_Layer SHALL craft a multilingual alert with specific recommendations (e.g., "Holi is coming! Order 20kg Gulal?")
7. THE Event_Engine SHALL consider hyper-local factors including pin code, district, state, and cultural region
8. WHEN multiple events overlap, THE Event_Engine SHALL prioritize events by Event_Confidence_Score
9. THE Event_Engine SHALL monitor the Digital_Panchang for upcoming events within a 30-day window

### Requirement 3: Hyper-Local SKU-Level Demand Forecasting

**User Story:** As an MSME retailer, I want accurate demand forecasts for each product at my store location, so that I can optimize inventory and avoid stockouts or overstocking.

#### Acceptance Criteria

1. THE Forecasting_Engine SHALL generate SKU-level demand predictions for a 7-day, 14-day, and 30-day horizon
2. WHEN generating forecasts, THE Forecasting_Engine SHALL incorporate Event_Confidence_Score data from the Event_Engine
3. THE Forecasting_Engine SHALL use Amazon SageMaker time-series models trained on historical sales data
4. WHEN historical data is insufficient for a SKU, THE Forecasting_Engine SHALL use category-level or regional aggregate data
5. THE Forecasting_Engine SHALL update forecasts daily at 2 AM IST
6. WHEN a high-confidence event is detected, THE Forecasting_Engine SHALL trigger an immediate forecast refresh
7. THE Forecasting_Engine SHALL provide forecast accuracy metrics with each prediction

### Requirement 4: Elasticity-Aware Pricing Intelligence

**User Story:** As an MSME retailer, I want to understand how price changes will impact demand for my products, so that I can set optimal prices that maximize revenue.

#### Acceptance Criteria

1. THE Forecasting_Engine SHALL calculate price elasticity coefficients for each SKU category
2. WHEN a user requests pricing recommendations, THE Forecasting_Engine SHALL simulate demand impact across a price range of ±30% from current price
3. THE Forecasting_Engine SHALL provide elasticity simulation results showing expected demand at different price points
4. WHEN elasticity data is unavailable, THE Forecasting_Engine SHALL use category-level or regional elasticity estimates
5. THE Forecasting_Engine SHALL update elasticity coefficients monthly based on observed price-demand relationships

### Requirement 5: Deterministic What-If Simulation Lab

**User Story:** As an MSME retailer, I want to simulate different pricing and inventory scenarios, so that I can make data-driven decisions before implementing changes.

#### Acceptance Criteria

1. WHEN a user specifies a price change scenario, THE Forecasting_Engine SHALL calculate the deterministic impact on demand, revenue, and profit
2. WHEN a user specifies an inventory level scenario, THE Forecasting_Engine SHALL calculate stockout probability and holding costs
3. THE Forecasting_Engine SHALL allow simulation of up to 5 concurrent scenarios
4. THE Forecasting_Engine SHALL provide side-by-side comparison of scenario outcomes
5. WHEN a simulation is complete, THE Forecasting_Engine SHALL generate an explainable summary of key drivers and assumptions

### Requirement 6: Promo ROI Guard

**User Story:** As an MSME retailer, I want to validate that promotional campaigns will be profitable before launching them, so that I don't lose money on poorly planned promotions.

#### Acceptance Criteria

1. WHEN a user proposes a promotional campaign, THE Forecasting_Engine SHALL calculate expected ROI based on discount depth, duration, and forecasted demand lift
2. WHEN expected ROI is negative, THE Forecasting_Engine SHALL alert the user and suggest alternative parameters
3. THE Forecasting_Engine SHALL consider cannibalization effects on non-promoted SKUs
4. THE Forecasting_Engine SHALL factor in supplier costs, margins, and operational costs
5. WHEN a promotion is approved, THE Event_Engine SHALL schedule alerts for campaign start and end dates

### Requirement 7: ONDC Market Intelligence Layer

**User Story:** As an MSME retailer, I want to understand competitive pricing and demand trends from ONDC marketplace data, so that I can stay competitive.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL integrate with ONDC APIs to fetch regional pricing data for comparable SKUs
2. WHEN generating pricing recommendations, THE Forecasting_Engine SHALL incorporate ONDC competitive pricing data
3. THE AI_Sahayak SHALL refresh ONDC data daily
4. WHEN ONDC data is unavailable, THE Forecasting_Engine SHALL proceed with internal data only
5. THE AI_Sahayak SHALL anonymize and aggregate ONDC data to protect individual seller privacy

### Requirement 8: Udhaar (Credit) Intelligence

**User Story:** As an MSME retailer, I want to track informal credit extended to customers and predict repayment patterns, so that I can manage cash flow effectively.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL maintain a record of Udhaar transactions per customer
2. WHEN a customer requests credit, THE AI_Sahayak SHALL provide a repayment probability score based on historical behavior
3. THE AI_Sahayak SHALL alert the retailer when outstanding Udhaar exceeds a configurable threshold
4. THE AI_Sahayak SHALL predict cash flow impact of outstanding Udhaar on inventory purchasing capacity
5. THE AI_Sahayak SHALL maintain customer privacy and store Udhaar data with encryption

### Requirement 9: Hyper-Local Stock Sharing Mode

**User Story:** As an MSME retailer, I want to share excess inventory with nearby retailers and borrow stock when needed, so that we can collectively reduce waste and stockouts.

#### Acceptance Criteria

1. WHEN a retailer has excess inventory of a SKU, THE AI_Sahayak SHALL identify nearby retailers with predicted demand for that SKU
2. WHEN a retailer faces a stockout, THE AI_Sahayak SHALL identify nearby retailers with available inventory
3. THE AI_Sahayak SHALL facilitate stock sharing requests between retailers within a 5 km radius
4. THE AI_Sahayak SHALL maintain store-level data isolation and only share inventory availability with explicit consent
5. WHEN a stock sharing transaction occurs, THE AI_Sahayak SHALL update inventory records for both parties

### Requirement 10: AR Shelf Optimization Assistant

**User Story:** As an MSME retailer, I want to visualize optimal shelf layouts using augmented reality, so that I can maximize sales through better product placement.

#### Acceptance Criteria

1. WHEN a user activates AR mode, THE AR_Assistant SHALL use the device camera to scan the current shelf layout
2. THE AR_Assistant SHALL overlay recommendations for product placement based on demand forecasts and category affinity
3. THE AR_Assistant SHALL highlight high-demand SKUs that should be placed at eye level
4. THE AR_Assistant SHALL suggest complementary product groupings
5. WHEN network bandwidth is insufficient, THE AR_Assistant SHALL operate in offline mode using cached recommendations

### Requirement 11: Sachet AI Micro-Subscription System

**User Story:** As an MSME retailer, I want to pay only for the AI features I use on a per-event basis, so that I can access advanced intelligence without high fixed costs.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL offer a pay-per-event pricing model where users pay only when accessing forecasts or simulations
2. THE AI_Sahayak SHALL provide a free tier with basic event alerts and limited forecasts
3. WHEN a user exceeds free tier limits, THE AI_Sahayak SHALL prompt for micro-payment authorization
4. THE AI_Sahayak SHALL integrate with UPI and other Indian payment systems for micro-transactions
5. THE AI_Sahayak SHALL provide transparent pricing with cost estimates before each paid action

### Requirement 12: Data Pipeline and Storage

**User Story:** As a system administrator, I want a robust data pipeline that cleans, transforms, and stores retail data, so that forecasting models have high-quality inputs.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL use AWS Glue and DataBrew for data cleaning and transformation
2. THE AI_Sahayak SHALL store raw data in Amazon S3 organized by date and store ID
3. THE AI_Sahayak SHALL store real-time inventory data in Amazon DynamoDB with sub-second read latency
4. WHEN data quality issues are detected, THE AI_Sahayak SHALL log errors and alert administrators
5. THE AI_Sahayak SHALL retain historical data for a minimum of 24 months for model training
6. THE AI_Sahayak SHALL implement data lifecycle policies to archive cold data to S3 Glacier

### Requirement 13: Authentication and Multi-Tenant Security

**User Story:** As a system administrator, I want secure, store-level data isolation with role-based access control, so that each retailer's data remains private and secure.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL use Amazon Cognito for user authentication and authorization
2. THE AI_Sahayak SHALL implement store-level data isolation where each retailer can only access their own data
3. WHEN a user authenticates, THE AI_Sahayak SHALL assign role-based permissions (Owner, Manager, Staff)
4. THE AI_Sahayak SHALL encrypt all data at rest using AWS KMS
5. THE AI_Sahayak SHALL encrypt all data in transit using TLS 1.3
6. THE AI_Sahayak SHALL log all data access events to AWS CloudTrail for audit purposes

### Requirement 14: Multi-Channel Client Interface and Dashboard

**User Story:** As an MSME retailer, I want an intuitive interface accessible through web, mobile, and WhatsApp that displays forecasts, alerts, and recommendations, so that I can quickly act on insights through my preferred channel.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL provide a web dashboard built with AWS Amplify
2. THE AI_Sahayak SHALL provide a mobile-responsive interface that works on smartphones and tablets
3. THE AI_Sahayak SHALL provide WhatsApp as a primary interface channel for queries, alerts, and confirmations
4. WHEN a user logs in to the web or mobile app, THE AI_Sahayak SHALL display a summary of upcoming events, current forecasts, and pending alerts
5. THE AI_Sahayak SHALL provide interactive charts for demand trends, pricing simulations, and inventory levels
6. WHEN operating in Lite_Mode, THE AI_Sahayak SHALL display simplified text-based views with minimal graphics
7. THE AI_Sahayak SHALL support offline viewing of cached forecasts and alerts
8. WHEN a user receives a WhatsApp alert, THE AI_Sahayak SHALL allow the user to confirm actions via WhatsApp or open the Amplify app for detailed views

### Requirement 15: Proactive Multi-Channel Event Alerting

**User Story:** As an MSME retailer, I want to receive proactive alerts about upcoming events with specific recommendations through WhatsApp, SMS, and in-app notifications, so that I can prepare inventory without constantly checking the system.

#### Acceptance Criteria

1. WHEN a high-confidence event is detected (score > 0.7), THE Event_Engine SHALL send alerts via WhatsApp, SMS, and in-app notifications
2. THE Event_Engine SHALL send alerts at least 7 days before a major event
3. THE Event_Engine SHALL include specific, actionable recommendations in each alert (e.g., "Holi is coming! Order 20kg Gulal?" or "Diwali in 10 days - stock 50 boxes of sweets")
4. WHEN the user receives a WhatsApp alert, THE AI_Sahayak SHALL allow the user to respond via WhatsApp to confirm orders or ask follow-up questions
5. WHEN network connectivity is unavailable, THE Event_Engine SHALL queue alerts for delivery when connectivity resumes
6. THE Event_Engine SHALL allow users to configure alert preferences and quiet hours
7. WHEN an alert is sent via WhatsApp, THE AI_Sahayak SHALL provide an option to open the Amplify mobile app for detailed analysis

### Requirement 15A: User-Initiated Reactive Queries

**User Story:** As an MSME retailer, I want to ask business questions via WhatsApp voice notes or text and receive intelligent answers with detailed analysis options, so that I can get insights on-demand.

#### Acceptance Criteria

1. WHEN a user sends a WhatsApp voice note (e.g., "Next month Xtra profit hoga?"), THE Bhashini_Integration SHALL translate and detect the intent
2. WHEN a query is received, THE AI_Sahayak SHALL route it to the appropriate Lambda function to query DynamoDB and SageMaker
3. WHEN analysis is complete, THE Generative_AI_Layer SHALL craft a conversational response in the user's language (e.g., "Estimated profit is ₹45,000")
4. WHEN a response is sent via WhatsApp, THE AI_Sahayak SHALL provide an option to open the Amplify web app for detailed charts and breakdowns
5. THE AI_Sahayak SHALL support queries about profit forecasts, inventory levels, pricing recommendations, and event impacts
6. WHEN a query cannot be answered with confidence, THE AI_Sahayak SHALL explain the limitation and suggest alternative questions
7. THE AI_Sahayak SHALL maintain conversation context for follow-up questions within a 30-minute session

### Requirement 16: Scalability and Performance

**User Story:** As a system administrator, I want the platform to scale seamlessly to support 10,000+ MSMEs with consistent performance, so that growth doesn't degrade user experience.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL support concurrent usage by 10,000+ retailers without performance degradation
2. THE AI_Sahayak SHALL respond to API requests within 2 seconds at the 95th percentile
3. THE AI_Sahayak SHALL respond to voice queries within 3 seconds at the 95th percentile
4. THE AI_Sahayak SHALL auto-scale compute resources based on demand using AWS Lambda and SageMaker auto-scaling
5. THE AI_Sahayak SHALL maintain 99.9% uptime availability
6. WHEN system load exceeds capacity, THE AI_Sahayak SHALL gracefully degrade by prioritizing critical functions

### Requirement 17: Explainable AI and Transparency

**User Story:** As an MSME retailer, I want to understand why the system makes specific recommendations, so that I can trust the insights and make informed decisions.

#### Acceptance Criteria

1. WHEN the Forecasting_Engine generates a forecast, THE AI_Sahayak SHALL provide an explanation of key factors (e.g., "Demand increased due to Diwali in 10 days")
2. WHEN the Forecasting_Engine recommends a price change, THE AI_Sahayak SHALL explain the expected impact on demand and revenue
3. THE AI_Sahayak SHALL display confidence intervals and uncertainty ranges for all predictions
4. THE AI_Sahayak SHALL provide access to historical forecast accuracy metrics
5. THE AI_Sahayak SHALL use plain language explanations suitable for non-technical users

### Requirement 18: Low-Bandwidth and Offline Support

**User Story:** As an MSME retailer in a rural area with poor connectivity, I want the system to work on 2G/3G networks and provide offline access to critical information, so that I can use it reliably.

#### Acceptance Criteria

1. WHEN network bandwidth is below 100 kbps, THE AI_Sahayak SHALL automatically switch to Lite_Mode
2. THE AI_Sahayak SHALL cache the most recent forecasts, alerts, and recommendations for offline access
3. THE AI_Sahayak SHALL synchronize data when connectivity is restored
4. THE AI_Sahayak SHALL compress all data transfers to minimize bandwidth usage
5. THE AI_Sahayak SHALL provide a progressive web app (PWA) that works offline

### Requirement 19: AWS Well-Architected Framework Compliance

**User Story:** As a system architect, I want the platform to follow AWS Well-Architected Framework best practices, so that it is reliable, secure, efficient, and cost-optimized.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL implement AWS Well-Architected Framework pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, and Sustainability
2. THE AI_Sahayak SHALL use AWS CloudWatch for monitoring and observability
3. THE AI_Sahayak SHALL implement automated backup and disaster recovery procedures
4. THE AI_Sahayak SHALL use AWS Cost Explorer and Budgets to monitor and optimize costs
5. THE AI_Sahayak SHALL implement infrastructure as code using AWS CloudFormation or CDK
6. THE AI_Sahayak SHALL conduct regular AWS Well-Architected Reviews

### Requirement 20: Data Privacy and Compliance

**User Story:** As an MSME retailer, I want my business data to be handled securely and in compliance with Indian data protection regulations, so that my privacy is protected.

#### Acceptance Criteria

1. THE AI_Sahayak SHALL comply with Indian data protection regulations including Digital Personal Data Protection Act (DPDPA)
2. THE AI_Sahayak SHALL store all data within Indian AWS regions (Mumbai, Hyderabad)
3. THE AI_Sahayak SHALL provide users with the ability to export their data in standard formats
4. THE AI_Sahayak SHALL provide users with the ability to delete their data upon request
5. THE AI_Sahayak SHALL obtain explicit consent before collecting or processing personal data
6. THE AI_Sahayak SHALL anonymize data used for aggregate analytics and model training
