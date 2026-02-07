# PillGuide - System Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [AI Integration](#ai-integration)
7. [Security & Privacy](#security--privacy)

---

## Overview

PillGuide is a multi-language prescription adherence management system that uses AI to:
- Extract medication information from prescription images in any language
- Translate complex medical information into plain language
- Prevent dosage errors through clear communication
- Increase medication adherence using behavioral science (Nudge Theory)

### Problem Solved
**Complex prescriptions in multiple languages often lead to dosage errors**

### Solution
- Multi-language OCR for prescription reading
- AI-powered translation and explanation
- Behavioral nudges to explain "why timing matters"
- Safety checks for contraindications

---

## System Architecture

### High-Level Architecture

```
┌─────────────┐
│   React     │  ← Frontend (User Interface)
│  Frontend   │
└──────┬──────┘
       │
       │ HTTPS/REST API
       │
┌──────▼──────┐
│   FastAPI   │  ← Backend (Business Logic)
│   Backend   │
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│   MongoDB   │  │   Google    │  │  Gemini AI  │
│  Database   │  │  Gemini API │  │   Vision    │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Component Diagram

```
┌────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                       │
├────────────────────────────────────────────────────────┤
│  - React Router (Navigation)                           │
│  - Axios (API Client)                                  │
│  - Tailwind CSS (Styling)                              │
│  - Shadcn/UI (Components)                              │
│                                                        │
│  Pages:                                                │
│  ├── HomePage (Landing)                                │
│  ├── UploadPage (Prescription Upload)                  │
│  └── MedicationsPage (Medication Management)           │
└────────────────────────────────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│                     API LAYER                          │
├────────────────────────────────────────────────────────┤
│  REST API Endpoints:                                   │
│  - POST /api/prescriptions/upload                      │
│  - GET  /api/prescriptions                             │
│  - POST /api/medications                               │
│  - GET  /api/medications                               │
│  - POST /api/contraindications/check                   │
│  - GET  /api/languages                                 │
└────────────────────────────────────────────────────────┘
                        ▼
┌────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                   │
├────────────────────────────────────────────────────────┤
│  Core Services:                                        │
│  ├── Prescription Analysis Service                     │
│  ├── Language Detection Service                        │
│  ├── Translation Service                               │
│  ├── Medication Explanation Generator                  │
│  ├── Contraindication Checker                          │
│  └── Nudge Theory Engine                               │
└────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────┬──────────────────┬──────────────────┐
│  DATA LAYER     │   AI LAYER       │  CACHE LAYER     │
├─────────────────┼──────────────────┼──────────────────┤
│  MongoDB        │  Google Gemini   │  In-Memory       │
│  Collections:   │  Models:         │  Cache           │
│  - prescriptions│  - Vision API    │  - Language Map  │
│  - medications  │  - Text API      │  - Model Config  │
│  - patients     │  Safety Settings │                  │
└─────────────────┴──────────────────┴──────────────────┘
```

---

## Technology Stack

### Frontend
- **React 18+**: UI library
- **React Router v6**: Client-side routing
- **Tailwind CSS**: Utility-first styling
- **Shadcn/UI**: Accessible component library
- **Axios**: HTTP client for API calls
- **Sonner**: Toast notifications

### Backend
- **FastAPI**: Modern Python web framework
- **Python 3.11+**: Programming language
- **Pydantic**: Data validation
- **Motor**: Async MongoDB driver
- **python-dotenv**: Environment management
- **Uvicorn**: ASGI server

### AI & ML
- **Google Generative AI SDK** (`google-generativeai`): Direct Gemini integration
- **Gemini 1.5 Flash**: Fast, efficient multimodal model
- **Gemini Vision**: Image analysis and OCR

### Database
- **MongoDB**: NoSQL document database
- **Motor**: Async Python driver

### Infrastructure
- **Kubernetes**: Container orchestration
- **Supervisor**: Process management
- **Docker**: Containerization

---

## Core Components

### 1. Prescription Upload & Analysis

**Component**: `analyze_prescription_image()`

**Purpose**: Extract medication information from prescription images in any language

**Input**: 
- Base64-encoded image
- Preferred output language

**Process**:
1. Initialize Gemini Vision model
2. Send image with multi-language OCR prompt
3. Detect prescription language
4. Extract medication details:
   - Name (original + English)
   - Dosage
   - Frequency
   - Timing
   - Special instructions

**Output**:
```json
{
  "detected_language": "es",
  "extracted_text": "Full OCR text",
  "medications": [
    {
      "name": "Metformina",
      "name_english": "Metformin",
      "dosage": "500mg",
      "frequency": "Dos veces al día",
      "timing": ["mañana", "noche"],
      "with_food": true
    }
  ]
}
```

### 2. Plain Language Explanation Generator

**Component**: `generate_medication_explanation()`

**Purpose**: Create simple, understandable medication explanations

**Algorithm**:
```python
function generate_explanation(medication, target_language):
    1. Initialize Gemini model with healthcare communication expertise
    2. Prompt for:
       a. What medication does (2-3 sentences, simple language)
       b. Why timing matters (Nudge Theory application)
       c. Dosage safety reminder
    3. Generate content in target language
    4. Parse JSON response
    5. Return structured explanation
```

**Nudge Theory Implementation**:
- **Motivation**: Explain consequences of poor timing
- **Meaning**: Connect actions to health outcomes  
- **Simplicity**: Remove medical jargon
- **Positive Framing**: Focus on benefits, not penalties

### 3. Multi-Language Translation System

**Supported Languages**: 10+ languages
- English (en)
- Spanish (es)
- Hindi (hi)
- Arabic (ar)
- Chinese (zh)
- French (fr)
- German (de)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)

**Translation Flow**:
```
Prescription (Any Language)
        ↓
    Detection
        ↓
    Extraction
        ↓
 User Language Preference
        ↓
   AI Translation
        ↓
Plain Language Explanation
```

### 4. Contraindication Checker

**Component**: `check_drug_interactions()`

**Purpose**: Identify potential drug interactions

**Algorithm**:
```python
function check_interactions(new_medication, current_medications):
    1. Query Gemini for known interactions
    2. Check against current medication list
    3. Generate warnings in user's language
    4. Provide recommendations
    5. Return structured safety information
```

**Safety Note**: This is for basic checking only. Always consult healthcare provider.

### 5. Data Persistence Layer

**Database**: MongoDB (Document-based)

**Collections**:

**prescriptions**:
```javascript
{
  id: "uuid",
  patient_id: "string",
  image_data: "truncated_base64",
  extracted_text: "string",
  detected_language: "es",
  preferred_language: "en",
  medications: [Medication],
  analysis_complete: true,
  created_at: "ISO8601"
}
```

**medications**:
```javascript
{
  id: "uuid",
  name: "Metformin",
  dosage: "500mg",
  frequency: "Twice daily",
  timing: ["morning", "evening"],
  plain_language_explanation: "string",
  why_timing_matters: "string",
  warnings: ["string"],
  original_language: "es",
  translated_to: "en",
  created_at: "ISO8601"
}
```

---

## Data Flow

### Prescription Upload Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Select prescription image
     ▼
┌─────────────┐
│  Frontend   │
│  (Upload)   │
└─────┬───────┘
      │ 2. Convert to Base64
      │ 3. POST /api/prescriptions/upload
      ▼
┌──────────────┐
│   Backend    │
│   FastAPI    │
└─────┬────────┘
      │ 4. Validate input
      │ 5. Call Gemini Vision API
      ▼
┌──────────────┐
│ Gemini Vision│
│     API      │
└─────┬────────┘
      │ 6. OCR + Language Detection
      │ 7. Return JSON
      ▼
┌──────────────┐
│   Backend    │
│  (Process)   │
└─────┬────────┘
      │ 8. For each medication:
      │    - Generate explanation
      │    - Apply Nudge Theory
      │    - Add safety warnings
      ▼
┌──────────────┐
│   MongoDB    │
│   (Store)    │
└─────┬────────┘
      │ 9. Return prescription object
      ▼
┌──────────────┐
│  Frontend    │
│  (Display)   │
└─────┬────────┘
      │ 10. Show results to user
      ▼
┌─────────┐
│  User   │
└─────────┘
```

---

## AI Integration

### Google Gemini Configuration

**Model**: `gemini-1.5-flash`

**Why Flash?**
- Fast response times (< 2 seconds)
- Cost-effective for production
- Supports vision + text
- High accuracy for medical text

**Configuration**:
```python
genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="Expert instructions",
    safety_settings={
        # Allow medical content
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: BLOCK_NONE
    },
    generation_config={
        "temperature": 0.3,  # Lower = more consistent
        "top_p": 0.95,
        "max_output_tokens": 2048
    }
)
```

### Prompt Engineering

**Prescription Analysis Prompt**:
- Multi-language instruction
- JSON schema specification
- Error handling guidance
- Example outputs

**Explanation Prompt**:
- Target language specification
- Plain language requirement
- Nudge Theory framework
- Safety reminder inclusion

### Response Parsing

**Algorithm**: `extract_json_from_response()`

```python
def extract_json_from_response(text):
    1. Strip whitespace
    2. Remove markdown (```json, ```)
    3. Find JSON boundaries ({ and })
    4. Extract JSON substring
    5. Parse with json.loads()
    6. Handle errors gracefully
```

---

## Security & Privacy

### Data Protection
- **Image Data**: Only first 100 chars stored (reference only)
- **Patient Privacy**: No PII stored beyond patient_id
- **Encryption**: HTTPS for all API calls
- **API Keys**: Environment variables only

### Medical Content Safety
- **Safety Settings**: Configured to allow medical content
- **Disclaimers**: All contraindication checks include medical advice disclaimer
- **Validation**: All inputs validated with Pydantic

### Error Handling
- Graceful degradation
- Default safe values
- Comprehensive logging
- User-friendly error messages

---

## Performance Considerations

### Response Times
- Prescription Analysis: ~5-10 seconds
- Medication Explanation: ~2-3 seconds
- Contraindication Check: ~2-3 seconds

### Optimization Strategies
- Async/await for all I/O operations
- MongoDB indexing on patient_id
- Image compression before upload
- Parallel medication explanation generation (future)

### Scalability
- Horizontal scaling with Kubernetes
- MongoDB sharding for large datasets
- Rate limiting on AI API calls
- Caching for language mappings

---

## Monitoring & Logging

### Logging Levels
- **INFO**: API requests, AI responses
- **ERROR**: Failed analyses, parsing errors
- **WARNING**: Rate limit approaching

### Metrics to Track
- API response times
- AI API success rate
- Language distribution
- Error rates by endpoint

---

## Future Enhancements

1. **Real-time Reminders**: SMS/Push notifications
2. **Voice Support**: Audio explanations
3. **Prescription History**: Trend analysis
4. **Family Sharing**: Multi-user support
5. **Pharmacy Integration**: Direct prescription filling
6. **ML Optimization**: Fine-tuned models for medical text
