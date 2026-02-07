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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="PillGuide API", version="2.0")
api_router = APIRouter(prefix="/api")

# Configure Google Generative AI with your API key
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if not GEMINI_API_KEY:
    logging.warning("GEMINI_API_KEY not found. Set it in .env file")
genai.configure(api_key=GEMINI_API_KEY)

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

class PrescriptionCreate(BaseModel):
    image_base64: str
    patient_id: Optional[str] = None
    preferred_language: str = "en"

class Medication(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    dosage: str
    frequency: str
    timing: List[str]
    duration: Optional[str] = None
    plain_language_explanation: str
    why_timing_matters: str
    with_food: bool = False
    warnings: List[str] = []
    original_language: Optional[str] = None
    translated_to: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Prescription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: Optional[str] = None
    image_data: str
    extracted_text: str
    detected_language: str
    preferred_language: str
    medications: List[Medication]
    analysis_complete: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MedicationCreate(BaseModel):
    name: str
    dosage: str
    frequency: str
    timing: List[str]
    duration: Optional[str] = None
    with_food: bool = False
    preferred_language: str = "en"

class ContraindictionCheck(BaseModel):
    medication_name: str
    current_medications: List[str]
    preferred_language: str = "en"

class ContraindictionResult(BaseModel):
    has_contraindications: bool
    warnings: List[str]
    recommendations: str

class LanguageList(BaseModel):
    languages: dict

def extract_json_from_response(text: str) -> dict:
    """Extract and parse JSON from AI response"""
    text = text.strip()
    
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].split('```')[0].strip()
    
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
    """Analyze prescription image using Gemini Vision"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Create image part for Gemini
        image_part = {
            'mime_type': 'image/png',
            'data': image_bytes
        }
        
        prompt = """Analyze this prescription image. It may be in ANY language.

Return ONLY valid JSON (no markdown):
{
    "detected_language": "language code (en/es/hi/ar/zh/fr/de/pt/ru/ja)",
    "detected_language_name": "language name",
    "extracted_text": "full original text from prescription",
    "medications": [
        {
            "name": "medication name in original language",
            "name_english": "medication name in English",
            "dosage": "dosage amount",
            "frequency": "frequency",
            "timing": ["morning", "evening"],
            "duration": "duration if specified",
            "with_food": true/false
        }
    ]
}

If unclear, return: {"detected_language": "unknown", "detected_language_name": "Unknown", "extracted_text": "Unable to read", "medications": []}"""
        
        response = model.generate_content([prompt, image_part])
        result = extract_json_from_response(response.text)
        
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
    """Generate plain language explanation with Nudge Theory"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""For medication '{med_name}' (dosage: '{dosage}', frequency: {frequency}):

Provide explanation in {SUPPORTED_LANGUAGES.get(target_language, 'English')}:
1. Simple explanation (what it does, 2-3 sentences)
2. Why timing matters (Nudge Theory)
3. Dosage safety reminder

Return ONLY valid JSON:
{{
    "plain_explanation": "simple explanation",
    "why_timing_matters": "why timing is important",
    "dosage_safety_reminder": "safety reminder"
}}"""
        
        response = model.generate_content(prompt)
        result = extract_json_from_response(response.text)
        
        if 'plain_explanation' not in result:
            result['plain_explanation'] = f"This medication is prescribed for your health condition."
        if 'why_timing_matters' not in result:
            result['why_timing_matters'] = "Taking medication at the right time helps maintain consistent levels."
        if 'dosage_safety_reminder' not in result:
            result['dosage_safety_reminder'] = "Always follow the prescribed dosage exactly."
            
        return result
    except Exception as e:
        logging.error(f"Explanation generation error: {str(e)}")
        return {
            'plain_explanation': f"This medication is prescribed for your health.",
            'why_timing_matters': "Timing helps maintain steady medication levels.",
            'dosage_safety_reminder': "Always follow the prescribed dosage exactly."
        }

async def check_drug_interactions(
    medication_name: str, 
    current_medications: List[str], 
    language: str
) -> dict:
    """Check for drug interactions"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Check if '{medication_name}' has contraindications with: {', '.join(current_medications)}.

Provide in {SUPPORTED_LANGUAGES.get(language, 'English')}.

Return ONLY valid JSON:
{{
    "has_contraindications": true/false,
    "warnings": ["list of warnings"],
    "recommendations": "recommendations"
}}"""
        
        response = model.generate_content(prompt)
        result = extract_json_from_response(response.text)
        return result
    except Exception as e:
        logging.error(f"Contraindication check error: {str(e)}")
        raise

@api_router.get("/")
async def root():
    return {"message": "PillGuide API - Multi-Language Prescription System"}

@api_router.get("/languages", response_model=LanguageList)
async def get_supported_languages():
    return {"languages": SUPPORTED_LANGUAGES}

@api_router.post("/prescriptions/upload", response_model=Prescription)
async def upload_prescription(data: PrescriptionCreate):
    try:
        extraction_result = await analyze_prescription_image(
            data.image_base64, 
            data.preferred_language
        )
        
        detected_lang = extraction_result['detected_language']
        
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
        
        prescription = Prescription(
            patient_id=data.patient_id,
            image_data=data.image_base64[:100],
            extracted_text=extraction_result.get("extracted_text", ""),
            detected_language=detected_lang,
            preferred_language=data.preferred_language,
            medications=medications_with_explanation,
            analysis_complete=True
        )
        
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
            detail="Failed to parse AI response. The prescription image may be unclear."
        )
    except Exception as e:
        logging.error(f"Error analyzing prescription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze prescription: {str(e)}")

@api_router.get("/prescriptions", response_model=List[Prescription])
async def get_prescriptions(patient_id: Optional[str] = None):
    query = {"patient_id": patient_id} if patient_id else {}
    prescriptions = await db.prescriptions.find(query, {"_id": 0}).to_list(1000)
    
    for prescription in prescriptions:
        if isinstance(prescription['created_at'], str):
            prescription['created_at'] = datetime.fromisoformat(prescription['created_at'])
        for med in prescription.get('medications', []):
            if isinstance(med['created_at'], str):
                med['created_at'] = datetime.fromisoformat(med['created_at'])
    
    return prescriptions

@api_router.post("/medications", response_model=Medication)
async def add_medication_manually(data: MedicationCreate):
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
    medications = await db.medications.find({}, {"_id": 0}).to_list(1000)
    
    for med in medications:
        if isinstance(med['created_at'], str):
            med['created_at'] = datetime.fromisoformat(med['created_at'])
    
    return medications

@api_router.post("/contraindications/check", response_model=ContraindictionResult)
async def check_contraindications(data: ContraindictionCheck):
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
    client.close()