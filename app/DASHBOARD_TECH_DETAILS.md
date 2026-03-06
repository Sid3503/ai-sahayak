# AI Sahayak Dashboard - Complete Technical Documentation

## Overview

The AI Sahayak Dashboard is a comprehensive retail intelligence platform designed for Indian kirana stores. It provides proactive alerts, reactive chat capabilities, and a sophisticated control center for pricing, forecasting, and business insights. The system was built for the AWS AI for Bharat Hackathon and integrates multiple AWS services with a modern web stack.

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Interface Layer                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Main Website (React/Vite) - Landing, onboarding, sign-in, chat UI        │
│  • Control Centre (React/Vite) - Dashboard iframe with pricing/forecast     │
│  • "My Day" Chat - Post-sign-in chat scoped to logged-in retailer           │
├─────────────────────────────────────────────────────────────────────────────┤
│                              Backend Services Layer                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Agents Backend (FastAPI/LangGraph) - Chat logic, session, tools          │
│  • Dashboard Backend (Flask) - Pricing, forecasting, KPIs, Bedrock          │
│  • AWS Lambda Functions - Festival orchestrator, alerts processor           │
├─────────────────────────────────────────────────────────────────────────────┤
│                              AWS Services Layer                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Bedrock - LLM for explanations and natural language processing           │
│  • SageMaker DeepAR - Time-series forecasting for demand prediction         │
│  • DynamoDB - Store/user profiles, session state                            │
│  • EventBridge - Scheduled triggers for festival orchestrator               │
│  • SSM Change Calendar - Festival event scheduling                          │
│  • S3 - Calendar data storage                                               │
│  • Cognito - User authentication                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure Deep Dive

### `/app/Dashboard/` - Control Centre Application

#### Core Application Files

**`app.py` (3,040 lines) - Flask Backend API**
- **Purpose**: Main API server providing pricing, forecasting, and business intelligence endpoints
- **Key Features**:
  - Multi-agent pricing pipeline with 6 specialized agents
  - DeepAR forecasting integration (SageMaker or local proxy)
  - Bedrock LLM integration for natural language explanations
  - SOP (Standard Operating Procedure) guardrail enforcement
  - What-if scenario analysis with NL parsing
- **API Endpoints**:
  - `/api/health` - Health check
  - `/api/meta` - Dataset metadata and SKU catalog
  - `/api/model-status` - Bedrock and DeepAR connectivity status
  - `/api/kpis` - Business KPIs and time-series data
  - `/api/price` - Pricing recommendations with explanations
  - `/api/whatif` - Scenario analysis with natural language input
  - `/api/forecast` - Demand forecasting with pricing recommendations
  - `/api/bedrock/test` - Bedrock connectivity test

**Pricing Agents Architecture**:
1. **BasePriceAgent** - Historical median + seasonality + festival adjustments
2. **PromoAgent** - Channel-specific promotion depth with margin protection
3. **CompetitorAgent** - Market price gap analysis and competitive response
4. **InventoryAgent** - Stock level-based price adjustments (low/high inventory)
5. **ProcurementAgent** - Lead time and supplier cost considerations
6. **BillingAgent** - MRP, tax, and cost floor enforcement

**Machine Learning Components**:
- **Neural Network Demand Model** (`DemandMLP`) - 3-layer MLP for unit prediction
- **Reinforcement Learning Policy** (`RandomForestClassifier`) - Optimal price selection
- **Elasticity Estimation** - Log-log OLS regression for price-demand relationship
- **DeepAR Forecasting** - SageMaker endpoint or local probabilistic proxy

#### Frontend Components

**`src/App.jsx` (788 lines) - React Control Centre UI**
- **Tabs**: Overview, Price, Review, Insights
- **Key Features**:
  - Responsive dashboard with KPI tiles and charts
  - Interactive pricing studio with candidate comparison
  - What-if scenario builder with natural language input
  - Forecast visualization with demand bands
  - AI explanation cards with Bedrock integration
  - Modal-based detailed explanations
- **Visual Components**:
  - `LineChart` - Custom SVG-based time-series charts
  - `BandChart` - Demand forecast uncertainty visualization
  - `BotCard` - AI assistant explanation component
  - `KpiCard` - Business metric display cards
  - `MetricChip` - Compact metric displays
  - `BarList` - Revenue distribution visualizations

**`src/styles.css` - Comprehensive UI Styling**
- Modern gradient-based design system
- Responsive grid layouts with CSS Grid
- Custom chart styling with SVG
- Mobile-responsive breakpoints
- Accessibility-focused color contrast

**`vite.config.js` - Build Configuration**
- Vite-based development server
- API proxy configuration for local development
- Base path configuration for iframe embedding

#### AWS Integration

**`aws/lambda/festival_orchestrator.py` - Event-Driven Orchestrator**
- **Purpose**: Daily forecast generation triggered by EventBridge
- **Key Features**:
  - SSM Change Calendar integration for festival detection
  - Multi-retailer batch processing capability
  - SNS notification publishing for alerts
  - SKU discovery via API metadata
  - Action recommendation engine based on forecast results
- **Workflow**:
  1. Check active festivals via SSM Change Calendar
  2. Discover top SKUs for retailer dataset
  3. Generate forecasts for each SKU
  4. Build action recommendations (reorder, price adjustments, promotions)
  5. Publish summary via SNS

**`aws/eventbridge_rules.json` - Scheduled Triggers**
- Daily forecast generation at 06:30 IST
- Special festival windows (e.g., Holi ramp-up)

#### Configuration and Data

**`config/festival_catalog.json` - Festival Definitions**
- 16 Indian festivals with boost multipliers and promo depths
- Pre-window definitions for ramp-up periods
- Calendar integration mappings

**`config/festival_calendar.json` - Calendar Event Specifications**
- SSM Change Calendar ARN mappings
- Event timing and duration configurations

**`deepar_train/` - Training Data**
- JSONL format training data for 5 retailers
- Time-series formatted for SageMaker DeepAR

**`gcpl_pricing_outputs/` - Generated Outputs**
- Pricing simulation results
- Forecast visualizations
- Business reports

#### Scripts and Utilities

**`scripts/` - Data Preparation and Deployment**
- `generate_msme_datasets.py` - Synthetic data generation
- `prepare_deepar_data.py` - DeepAR training data preparation
- `prepare_raju_dataset.py` - Retailer-specific data processing
- `provision_change_calendars.py` - AWS calendar setup
- `apply_calendar_env.py` - Environment configuration

**`generated/` - Auto-generated Content**
- Documentation and reports
- Configuration templates

**`images/` - UI Assets**
- Dashboard screenshots
- Branding assets

## Technical Stack Details

### Backend Technologies

**Python 3.9+ with Key Libraries**:
- `Flask` - API framework with CORS support
- `pandas` - Data manipulation and time-series processing
- `numpy` - Numerical computations
- `boto3` - AWS service integration
- `torch` - Neural network implementation
- `scikit-learn` - ML models and preprocessing
- `rich` - Console output formatting

**Machine Learning Models**:
1. **Demand Forecasting**:
   - Primary: SageMaker DeepAR (when endpoints configured)
   - Fallback: Local probabilistic autoregressive model
   - Features: Seasonality, festival effects, price elasticity

2. **Price Optimization**:
   - Multi-agent system with weighted candidate assembly
   - Elasticity-based demand prediction
   - Margin protection and competitive analysis

3. **Natural Language Processing**:
   - Bedrock LLM (Amazon Nova, Claude 3.5 Sonnet)
   - Rule-based NL parser for what-if scenarios
   - Explanation generation with confidence scoring

### Frontend Technologies

**React 18 with Vite**:
- Modern functional components with hooks
- Custom SVG charting system
- Responsive design with CSS Grid
- Iframe embedding support for main app integration

**Styling**:
- Custom CSS with CSS variables
- Gradient-based design system
- Accessibility-focused color palette
- Mobile-first responsive design

### AWS Services Integration

**Core Services**:
1. **Bedrock** - LLM inference for explanations
2. **SageMaker** - DeepAR forecasting endpoints
3. **DynamoDB** - User profiles and session state
4. **EventBridge** - Scheduled triggers
5. **SSM Change Calendar** - Festival event management
6. **S3** - Calendar and data storage
7. **Cognito** - Authentication
8. **SNS** - Notification delivery

**Lambda Functions**:
- Festival orchestrator with multi-retailer support
- Alert processor for proactive notifications

## Data Flow and Processing

### Pricing Pipeline

```
1. Data Loading → Load retailer dataset with enrichment
2. Row Selection → Pick relevant SKU/channel/region combination
3. Agent Execution → Run 6 pricing agents in sequence
4. Candidate Assembly → Weighted combination of agent outputs
5. Demand Prediction → Elasticity + NN + temporal blending
6. Selection → SOP guardrail enforcement and approval workflow
7. Explanation → Bedrock LLM or deterministic explanation generation
```

### Forecasting Pipeline

```
1. Time-Series Preparation → Build daily SKU series with features
2. Festival Context → Check SSM Change Calendar for active events
3. Model Selection → DeepAR (SageMaker) or local proxy
4. Forecast Generation → Probabilistic demand prediction
5. Price Integration → Run pricing pipeline for forecasted dates
6. Risk Assessment → Stock vs demand analysis
7. Action Recommendation → Reorder, price, promotion decisions
```

### What-If Analysis

```
1. Scenario Input → Natural language or structured overrides
2. NL Parsing → Bedrock LLM or rule-based extraction
3. Override Application → Modify base row parameters
4. Pipeline Re-execution → Run pricing with modified inputs
5. Delta Calculation → Compare original vs updated results
6. Explanation → Business impact analysis
```

## User Workflows

### Retailer Dashboard Usage

1. **Overview Tab**:
   - Business KPIs (revenue, profit, margin, inventory)
   - Time-series trends and charts
   - Category and payment mode analysis
   - Alert notifications

2. **Price Tab**:
   - SKU selection and competitor price input
   - Three candidate price recommendations
   - AI explanation of pricing logic
   - Inventory and margin details

3. **Review Tab**:
   - Natural language what-if scenarios
   - Impact analysis with delta calculations
   - Side-by-side comparison of scenarios

4. **Insights Tab**:
   - Demand forecasting for upcoming days
   - Stock risk assessment
   - Action recommendations
   - Festival impact visualization

### Integration with Main Application

The Control Centre is designed to be embedded as an iframe in the main AI Sahayak application:
- URL parameter `?retailer=raju` locks view to specific retailer
- Same-origin API calls via proxy configuration
- Responsive design for iframe embedding

## Deployment and Configuration

### Environment Variables

**Backend Configuration**:
```
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
AI_SAHAYAK_API_BASE_URL (for agent communication)
MONGODB_URI (for session state)
BEDROCK_MODEL_ID, BEDROCK_FALLBACK_MODELS
DEEPAR_ENDPOINT_RAJU, DEEPAR_ENDPOINT_RAMESH, etc.
```

**Frontend Configuration**:
```
VITE_API_PROXY_TARGET (backend API URL)
VITE_CONTROL_CENTRE_URL (iframe source)
COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID
```

**Lambda Configuration**:
```
AI_SAHAYAK_API_BASE_URL (dashboard API)
AI_SAHAYAK_DATASET_KEY (default retailer)
AI_SAHAYAK_SNS_TOPIC_ARN (for notifications)
AI_SAHAYAK_CALENDAR_EVENTS_JSON (festival definitions)
```

### Running Locally

1. **Export AWS credentials**:
   ```bash
   export AWS_ACCESS_KEY_ID="your_key"
   export AWS_SECRET_ACCESS_KEY="your_secret"
   export AWS_DEFAULT_REGION="ap-south-1"
   ```

2. **Start all services**:
   ```bash
   cd ai-sahayak
   ./start.sh
   ```

3. **Access URLs**:
   - Main site: http://localhost:5173
   - Control Centre: http://localhost:5174/control-centre/
   - Backend API: http://localhost:8000
   - Dashboard API: http://localhost:8001

### AWS Deployment

1. **Infrastructure**:
   - SageMaker endpoints for DeepAR forecasting
   - DynamoDB tables for user/store data
   - SSM Change Calendars for festival events
   - S3 buckets for calendar data
   - EventBridge rules for scheduling
   - Lambda functions for orchestration

2. **Configuration**:
   - Environment variables for service endpoints
   - IAM roles with appropriate permissions
   - CORS configuration for web access
   - SSL certificates for HTTPS

## Key Features and Innovations

### 1. Multi-Agent Pricing System
- Six specialized agents with domain expertise
- Weighted candidate assembly based on business rules
- SOP guardrail enforcement with approval workflows

### 2. Hybrid Forecasting Approach
- SageMaker DeepAR for production forecasting
- Local probabilistic model for development/fallback
- Festival integration via SSM Change Calendar

### 3. Natural Language Interface
- Bedrock LLM for explanation generation
- Rule-based NL parsing for what-if scenarios
- Confidence scoring for extraction quality

### 4. Proactive Intelligence
- EventBridge-triggered daily forecasts
- SSM Change Calendar integration for festivals
- SNS notifications for critical actions

### 5. Retailer-Specific Customization
- Five retailer datasets (Raju, Ramesh, Suresh, Kanta, Lakshmi)
- Channel and region-specific pricing rules
- Inventory and procurement considerations

## Performance Characteristics

### Scalability
- Stateless API design for horizontal scaling
- Lambda-based orchestration for event-driven processing
- DynamoDB for scalable data storage

### Reliability
- Fallback mechanisms for all external dependencies
- Retry logic for API calls
- Graceful degradation when services are unavailable

### Performance
- Caching of runtime data and model status
- Efficient data loading with pandas optimizations
- Async processing for independent operations

## Security Considerations

### Authentication and Authorization
- Cognito integration for user authentication
- Dataset scoping based on retailer identity
- API key validation for service-to-service communication

### Data Protection
- Environment-based credential management
- Secure API communication
- Input validation and sanitization

### AWS Best Practices
- IAM roles with least privilege
- Encrypted data storage
- VPC configuration for private resources

## Monitoring and Observability

### Logging
- Structured logging for API requests
- Error tracking with context
- Performance metrics collection

### Monitoring
- API health checks
- Model connectivity status
- Lambda execution metrics

### Alerting
- SNS notifications for critical events
- Error rate monitoring
- Performance degradation detection

## Future Enhancements

### Planned Features
1. **Advanced ML Models**:
   - Transformer-based demand forecasting
   - Reinforcement learning for dynamic pricing
   - Anomaly detection for unusual patterns

2. **Extended Integration**:
   - WhatsApp Business API for alerts
   - ERP system integration
   - Payment gateway connections

3. **Enhanced Analytics**:
   - Cohort analysis for customer segments
   - Predictive inventory optimization
   - Supply chain risk assessment

4. **Mobile Experience**:
   - Progressive Web App (PWA) support
   - Mobile-optimized interfaces
   - Offline capability for basic functions

## Conclusion

The AI Sahayak Dashboard represents a sophisticated retail intelligence platform that combines modern web technologies with advanced machine learning and AWS cloud services. Its multi-agent architecture, hybrid forecasting approach, and natural language interface provide a comprehensive solution for Indian kirana stores to optimize pricing, manage inventory, and respond to market dynamics.

The system's modular design, comprehensive error handling, and extensive configuration options make it suitable for both development experimentation and production deployment. Its integration with the broader AI Sahayak ecosystem provides a complete solution for proactive retail intelligence.