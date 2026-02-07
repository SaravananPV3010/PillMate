"""
PillGuide Backend Server
========================

A FastAPI-based backend for prescription adherence management with multi-language support.
Uses Google Gemini AI for prescription image analysis and plain language medical explanations.

Key Features:
- Multi-language prescription OCR
- AI-powered medication extraction
- Plain language explanations using Nudge Theory
- Contraindication checking
- MongoDB data persistence

Author: Emergent AI
Version: 2.0 (Direct Google Gemini Integration)
"""

from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import base64
import json

# Google Generative AI imports
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# =============================================================================
# INITIALIZATION & CONFIGURATION
# =============================================================================

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# FastAPI app initialization
app = FastAPI(title="PillGuide API", version="2.0")
api_router = APIRouter(prefix="/api")

# Configure Google Generative AI
GEMINI_API_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
genai.configure(api_key=GEMINI_API_KEY)

# Safety settings for medical content
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Supported languages for medical translation
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "hi": "Hindi",
    "ar": "Arabic",
    "zh": "Chinese",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese"
}

# =============================================================================
# PYDANTIC MODELS (Data Validation & Serialization)
# =============================================================================

class PrescriptionCreate(BaseModel):
    """Request model for prescription upload"""
    image_base64: str  # Base64-encoded prescription image
    patient_id: Optional[str] = None
    preferred_language: str = "en"  # User's preferred language for explanations

class Medication(BaseModel):
    """Medication data model with AI-generated explanations"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    dosage: str
    frequency: str
    timing: List[str]
    duration: Optional[str] = None
    plain_language_explanation: str  # Simple explanation of medication purpose
    why_timing_matters: str  # Behavioral nudge explanation
    with_food: bool = False
    warnings: List[str] = []
    original_language: Optional[str] = None  # Language prescription was in
    translated_to: Optional[str] = None  # Language explanations are in
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Prescription(BaseModel):
    """Complete prescription with extracted medications"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: Optional[str] = None
    image_data: str  # Truncated base64 for reference
    extracted_text: str  # Raw OCR text from prescription
    detected_language: str  # Auto-detected prescription language
    preferred_language: str  # User's chosen explanation language
    medications: List[Medication]
    analysis_complete: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MedicationCreate(BaseModel):
    """Request model for manual medication addition"""
    name: str
    dosage: str
    frequency: str
    timing: List[str]
    duration: Optional[str] = None
    with_food: bool = False
    preferred_language: str = "en"

class ContraindictionCheck(BaseModel):
    """Request model for drug interaction checking"""
    medication_name: str
    current_medications: List[str]
    preferred_language: str = "en"

class ContraindictionResult(BaseModel):
    """Response model for contraindication analysis"""
    has_contraindications: bool
    warnings: List[str]
    recommendations: str

class LanguageList(BaseModel):
    """Response model for supported languages"""
    languages: dict

# =============================================================================
# HELPER FUNCTIONS - AI INTERACTION
# =============================================================================

def create_gemini_model(system_instruction: str) -> genai.GenerativeModel:
    """
    Create a configured Gemini model instance
    
    Args:
        system_instruction: System prompt defining model behavior
        
    Returns:
        Configured GenerativeModel instance
        
    Algorithm:
        1. Initialize model with gemini-3-flash-preview
        2. Set system instruction for domain-specific behavior
        3. Configure safety settings for medical content
        4. Set generation config for JSON output
    """
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',  # Using stable flash model
        system_instruction=system_instruction,
        safety_settings=SAFETY_SETTINGS,
        generation_config={
            "temperature": 0.3,  # Lower temperature for medical accuracy
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    )

def extract_json_from_response(text: str) -> dict:
    """
    Extract and parse JSON from AI response
    
    Args:
        text: Raw AI response text
        
    Returns:
        Parsed JSON dictionary
        
    Algorithm:
        1. Strip whitespace from response
        2. Remove markdown code blocks (```json, ```)
        3. Find JSON boundaries ({ and })
        4. Parse and return JSON object
        5. Raise error if invalid
        
    Handles:
        - Markdown-wrapped JSON
        - Extra text before/after JSON
        - Nested code blocks
    """
    text = text.strip()
    
    # Remove markdown code blocks
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].split('```')[0].strip()
    
    # Find JSON boundaries
    if not text.startswith('{'):
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
    
    text = text.strip()
    
    if not text:
        raise ValueError("Empty response after JSON extraction")
    
    return json.loads(text)

async def analyze_prescription_image(image_base64: str, preferred_language: str) -> dict:
    """
    Analyze prescription image and extract medication information
    
    Args:
        image_base64: Base64-encoded prescription image
        preferred_language: User's preferred language for explanations
        
    Returns:
        Dictionary with detected language, extracted text, and medications
        
    Algorithm:
        1. Create Gemini Vision model with medical OCR instructions
        2. Convert base64 to image blob
        3. Send image with multi-language extraction prompt
        4. Parse response for language detection and medication data
        5. Handle errors gracefully with default values
        
    Features:
        - Multi-language OCR (any language input)
        - Automatic language detection
        - Medication name translation to English
        - Dosage format preservation
    """
    model = create_gemini_model(
        "You are a multilingual medical prescription analysis expert. "
        "You can read prescriptions in any language and extract medication information accurately. "
        "Always return valid JSON without markdown."
    )
    
    # Prepare image for Gemini
    image_bytes = base64.b64decode(image_base64)
    image_part = {
        'mime_type': 'image/png',
        'data': image_bytes
    }
    
    prompt = """Analyze this prescription image. It may be in ANY language (English, Spanish, Hindi, Arabic, Chinese, French, etc.).

IMPORTANT: Read the prescription in its original language first, then provide the information.

Return ONLY valid JSON (no markdown):
{
    "detected_language": "language code (en/es/hi/ar/zh/fr/de/pt/ru/ja)",
    "detected_language_name": "language name",
    "extracted_text": "full original text from prescription in original language",
    "medications": [
        {
            "name": "medication name in original language",
            "name_english": "medication name in English",
            "dosage": "dosage in original format",
            "frequency": "frequency in original language",
            "timing": ["timing indicators"],
            "duration": "duration if specified",
            "with_food": true/false
        }
    ]
}

If unclear, return: {"detected_language": "unknown", "detected_language_name": "Unknown", "extracted_text": "Unable to read", "medications": []}"""
    
    try:
        response = model.generate_content([prompt, image_part])
        result = extract_json_from_response(response.text)
        
        # Validate structure
        if 'extracted_text' not in result:
            result['extracted_text'] = 'No text extracted'
        if 'medications' not in result:
            result['medications'] = []
        if 'detected_language' not in result:
            result['detected_language'] = 'unknown'
        if 'detected_language_name' not in result:
            result['detected_language_name'] = 'Unknown'
            
        return result
    except Exception as e:
        logging.error(f"Prescription analysis error: {str(e)}")
        raise

async def generate_medication_explanation(
    med_name: str, 
    dosage: str, 
    frequency: str, 
    target_language: str
) -> dict:
    """
    Generate plain language medication explanation with behavioral nudges
    
    Args:
        med_name: Medication name
        dosage: Dosage amount
        frequency: How often to take
        target_language: Language for explanation
        
    Returns:
        Dictionary with plain explanation, timing rationale, and safety reminder
        
    Algorithm (Nudge Theory Implementation):
        1. Create model with healthcare communication expertise
        2. Generate simple explanation (what medication does)
        3. Apply Nudge Theory: explain WHY timing matters
        4. Add dosage safety reminder
        5. Return structured explanations
        
    Behavioral Science:
        - Uses Nudge Theory to increase medication adherence
        - Explains consequences of poor timing (motivation)
        - Connects actions to health outcomes (meaning)
        - Provides positive reinforcement
    """
    model = create_gemini_model(
        f"You are a multilingual healthcare communication expert. "
        f"Explain medical information in {SUPPORTED_LANGUAGES.get(target_language, 'English')} "
        f"using simple, plain language. Always return valid JSON."
    )
    
    prompt = f"""For the medication '{med_name}' (dosage: '{dosage}', frequency: {frequency}):

Provide explanation in {SUPPORTED_LANGUAGES.get(target_language, 'English')} language:
1. Explain what this medication does in simple, plain language (2-3 sentences)
2. Explain why timing matters (using Nudge Theory - explain the 'why' to increase adherence)
3. Add a safety reminder about dosage accuracy

Return ONLY valid JSON:
{{
    "plain_explanation": "simple explanation",
    "why_timing_matters": "why timing is important",
    "dosage_safety_reminder": "brief dosage safety reminder"
}}"""
    
    try:
        response = model.generate_content(prompt)
        result = extract_json_from_response(response.text)
        
        # Provide defaults if missing
        if 'plain_explanation' not in result:
            result['plain_explanation'] = f"This medication is prescribed for your health. Please consult your doctor for specific information."
        if 'why_timing_matters' not in result:
            result['why_timing_matters'] = "Taking medication at the right time helps maintain consistent levels in your body for optimal effectiveness."
        if 'dosage_safety_reminder' not in result:
            result['dosage_safety_reminder'] = "Always follow the prescribed dosage exactly."
            
        return result
    except Exception as e:
        logging.error(f"Explanation generation error: {str(e)}")
        # Return safe defaults
        return {
            'plain_explanation': f"This medication is prescribed for your health. Please consult your healthcare provider.",
            'why_timing_matters': "Timing helps maintain steady medication levels for best results.",
            'dosage_safety_reminder': "Always follow the prescribed dosage exactly."
        }

async def check_drug_interactions(
    medication_name: str, 
    current_medications: List[str], 
    language: str
) -> dict:
    """
    Check for basic drug interactions and contraindications
    
    Args:
        medication_name: New medication to check
        current_medications: List of current medications
        language: Language for warnings
        
    Returns:
        Dictionary with contraindication status, warnings, and recommendations
        
    Algorithm:
        1. Create medical safety expert model
        2. Query for known interactions
        3. Return structured safety information
        4. Translate warnings to user's language
        
    Note: This is for basic checking only. Always consult healthcare provider.
    """
    model = create_gemini_model(
        f"You are a multilingual medical safety expert. "
        f"Provide contraindication information in {SUPPORTED_LANGUAGES.get(language, 'English')}. "
        f"Always return valid JSON."
    )
    
    prompt = f"""Check if '{medication_name}' has any basic contraindications or interactions with these current medications: {', '.join(current_medications)}.

Provide response in {SUPPORTED_LANGUAGES.get(language, 'English')} language.

Return ONLY valid JSON:
{{
    "has_contraindications": true/false,
    "warnings": ["list of warnings or empty array"],
    "recommendations": "brief recommendation or 'No known contraindications'"
}}"""
    
    try:
        response = model.generate_content(prompt)
        result = extract_json_from_response(response.text)
        return result
    except Exception as e:
        logging.error(f"Contraindication check error: {str(e)}")
        raise

# =============================================================================
# API ENDPOINTS
# =============================================================================

@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PillGuide API v2.0 - Multi-Language Prescription Adherence System"}

@api_router.get("/languages", response_model=LanguageList)
async def get_supported_languages():
    """
    Get list of supported languages
    
    Returns:
        Dictionary of language codes and names
    """
    return {"languages": SUPPORTED_LANGUAGES}

@api_router.post("/prescriptions/upload", response_model=Prescription)
async def upload_prescription(data: PrescriptionCreate):
    """
    Upload and analyze prescription image
    
    Workflow:
        1. Receive base64 prescription image
        2. Analyze with Gemini Vision (multi-language OCR)
        3. Detect prescription language
        4. Extract medication details
        5. Generate explanations in user's preferred language
        6. Apply Nudge Theory for adherence
        7. Store in MongoDB
        8. Return structured prescription data
        
    Error Handling:
        - Invalid image format
        - OCR failure
        - JSON parsing errors
        - Database errors
    """
    try:
        # Step 1: Analyze prescription image
        extraction_result = await analyze_prescription_image(
            data.image_base64, 
            data.preferred_language
        )
        
        detected_lang = extraction_result['detected_language']
        
        # Step 2: Generate explanations for each medication
        medications_with_explanation = []
        for med in extraction_result.get("medications", []):
            if not med.get('name'):
                continue
            
            med_name = med.get('name_english', med.get('name', 'Unknown'))
            
            explanation_data = await generate_medication_explanation(
                med_name,
                med.get('dosage', 'Unknown'),
                med.get('frequency', 'as prescribed'),
                data.preferred_language
            )
            
            # Combine explanation with dosage safety
            full_explanation = f"{explanation_data['plain_explanation']} ⚠️ {explanation_data.get('dosage_safety_reminder', '')}"
            
            medication_obj = Medication(
                name=med_name,
                dosage=med.get('dosage', 'As prescribed'),
                frequency=med.get('frequency', 'As prescribed'),
                timing=med.get('timing', []),
                duration=med.get('duration'),
                with_food=med.get('with_food', False),
                plain_language_explanation=full_explanation,
                why_timing_matters=explanation_data['why_timing_matters'],
                warnings=[explanation_data.get('dosage_safety_reminder', '')],
                original_language=detected_lang,
                translated_to=data.preferred_language
            )
            medications_with_explanation.append(medication_obj)
        
        # Step 3: Create prescription record
        prescription = Prescription(
            patient_id=data.patient_id,
            image_data=data.image_base64[:100],  # Store truncated for reference
            extracted_text=extraction_result.get("extracted_text", ""),
            detected_language=detected_lang,
            preferred_language=data.preferred_language,
            medications=medications_with_explanation,
            analysis_complete=True
        )
        
        # Step 4: Store in MongoDB
        doc = prescription.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        for med in doc['medications']:
            med['created_at'] = med['created_at'].isoformat()
        
        await db.prescriptions.insert_one(doc)
        
        return prescription
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to parse AI response. The prescription image may be unclear or invalid."
        )
    except Exception as e:
        logging.error(f"Error analyzing prescription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze prescription: {str(e)}")

@api_router.get("/prescriptions", response_model=List[Prescription])
async def get_prescriptions(patient_id: Optional[str] = None):
    """
    Retrieve prescriptions for a patient
    
    Args:
        patient_id: Optional patient filter
        
    Returns:
        List of prescription records
    """
    query = {"patient_id": patient_id} if patient_id else {}
    prescriptions = await db.prescriptions.find(query, {"_id": 0}).to_list(1000)
    
    # Convert ISO strings back to datetime
    for prescription in prescriptions:
        if isinstance(prescription['created_at'], str):
            prescription['created_at'] = datetime.fromisoformat(prescription['created_at'])
        for med in prescription.get('medications', []):
            if isinstance(med['created_at'], str):
                med['created_at'] = datetime.fromisoformat(med['created_at'])
    
    return prescriptions

@api_router.post("/medications", response_model=Medication)
async def add_medication_manually(data: MedicationCreate):
    """
    Add medication manually without prescription image
    
    Workflow:
        1. Receive medication details
        2. Generate AI explanation in preferred language
        3. Apply behavioral nudges
        4. Store in database
    """
    try:
        explanation_data = await generate_medication_explanation(
            data.name,
            data.dosage,
            data.frequency,
            data.preferred_language
        )
        
        full_explanation = f"{explanation_data['plain_explanation']} ⚠️ {explanation_data.get('dosage_safety_reminder', '')}"
        
        medication = Medication(
            name=data.name,
            dosage=data.dosage,
            frequency=data.frequency,
            timing=data.timing,
            duration=data.duration,
            with_food=data.with_food,
            plain_language_explanation=full_explanation,
            why_timing_matters=explanation_data['why_timing_matters'],
            warnings=[explanation_data.get('dosage_safety_reminder', '')],
            translated_to=data.preferred_language
        )
        
        doc = medication.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.medications.insert_one(doc)
        
        return medication
    except Exception as e:
        logging.error(f"Error adding medication: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add medication: {str(e)}")

@api_router.get("/medications", response_model=List[Medication])
async def get_medications():
    """Retrieve all manually added medications"""
    medications = await db.medications.find({}, {"_id": 0}).to_list(1000)
    
    for med in medications:
        if isinstance(med['created_at'], str):
            med['created_at'] = datetime.fromisoformat(med['created_at'])
    
    return medications

@api_router.post("/contraindications/check", response_model=ContraindictionResult)
async def check_contraindications(data: ContraindictionCheck):
    """
    Check for drug interactions and contraindications
    
    Safety Note:
        This provides basic checking only. Always consult healthcare provider
        for professional medical advice.
    """
    try:
        result = await check_drug_interactions(
            data.medication_name,
            data.current_medications,
            data.preferred_language
        )
        return ContraindictionResult(**result)
    except Exception as e:
        logging.error(f"Error checking contraindications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check contraindications: {str(e)}")

# =============================================================================
# APP CONFIGURATION
# =============================================================================

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    client.close()
