from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, time
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType, ImageContent
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

class PrescriptionCreate(BaseModel):
    image_base64: str
    patient_id: Optional[str] = None

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Prescription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: Optional[str] = None
    image_data: str
    extracted_text: str
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

class ContraindictionCheck(BaseModel):
    medication_name: str
    current_medications: List[str]

class ContraindictionResult(BaseModel):
    has_contraindications: bool
    warnings: List[str]
    recommendations: str

class AdherenceSchedule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    medication_id: str
    medication_name: str
    schedule_times: List[str]
    nudge_messages: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@api_router.get("/")
async def root():
    return {"message": "PillGuide API - Prescription Adherence System"}

@api_router.post("/prescriptions/upload", response_model=Prescription)
async def upload_prescription(data: PrescriptionCreate):
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"prescription-{uuid.uuid4()}",
            system_message="You are a medical prescription analysis expert. Extract medication information from prescription images accurately. Always return valid JSON without markdown formatting."
        ).with_model("gemini", "gemini-3-flash-preview")
        
        image_content = ImageContent(image_base64=data.image_base64)
        
        user_message = UserMessage(
            text="""Analyze this prescription image and extract all medication information. 
            Return ONLY a valid JSON object (no markdown code blocks, no extra text):
            {
                "extracted_text": "full text from prescription",
                "medications": [
                    {
                        "name": "medication name",
                        "dosage": "dosage amount",
                        "frequency": "how often",
                        "timing": ["morning", "afternoon", "night"],
                        "duration": "duration if specified or empty string",
                        "with_food": true/false
                    }
                ]
            }
            
            If the image is unclear or not a prescription, return:
            {
                "extracted_text": "Unable to read prescription clearly",
                "medications": []
            }""",
            file_contents=[image_content]
        )
        
        response = await chat.send_message(user_message)
        
        logging.info(f"Raw Gemini response: {response[:200]}...")
        
        response_text = response.strip()
        
        # Remove markdown code blocks
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Try to find JSON object in the response
        if not response_text.startswith('{'):
            # Look for first { and last }
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
        
        response_text = response_text.strip()
        
        if not response_text:
            raise ValueError("Empty response from Gemini Vision API")
        
        extraction_result = json.loads(response_text)
        
        # Validate the response structure
        if 'extracted_text' not in extraction_result:
            extraction_result['extracted_text'] = 'No text extracted'
        if 'medications' not in extraction_result:
            extraction_result['medications'] = []
        
        medications_with_explanation = []
        for med in extraction_result.get("medications", []):
            # Skip if no medication name
            if not med.get('name'):
                continue
                
            explanation_chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"explanation-{uuid.uuid4()}",
                system_message="You are a healthcare communication expert. Explain medical information in simple, plain language. Always return valid JSON without markdown."
            ).with_model("gemini", "gemini-3-flash-preview")
            
            explanation_msg = UserMessage(
                text=f"""For the medication '{med.get('name', 'Unknown')}' at dosage '{med.get('dosage', 'Unknown')}' taken {med.get('frequency', 'as prescribed')}:
                1. Explain what this medication does in simple, plain language (2-3 sentences)
                2. Explain why the timing matters (using Nudge Theory - explain the 'why' to increase adherence)
                
                Return ONLY valid JSON (no markdown):
                {{
                    "plain_explanation": "simple explanation",
                    "why_timing_matters": "why timing is important"
                }}"""
            )
            
            try:
                explanation_response = await explanation_chat.send_message(explanation_msg)
                explanation_text = explanation_response.strip()
                
                # Remove markdown
                if '```json' in explanation_text:
                    explanation_text = explanation_text.split('```json')[1].split('```')[0].strip()
                elif '```' in explanation_text:
                    explanation_text = explanation_text.split('```')[1].split('```')[0].strip()
                
                # Find JSON object
                if not explanation_text.startswith('{'):
                    start = explanation_text.find('{')
                    end = explanation_text.rfind('}')
                    if start != -1 and end != -1:
                        explanation_text = explanation_text[start:end+1]
                
                explanation_data = json.loads(explanation_text)
                
                # Validate explanation data
                if 'plain_explanation' not in explanation_data:
                    explanation_data['plain_explanation'] = f"This medication is prescribed for your health condition. Please consult your doctor for specific information about {med.get('name', 'this medication')}."
                if 'why_timing_matters' not in explanation_data:
                    explanation_data['why_timing_matters'] = "Taking medication at the right time helps maintain consistent levels in your body for optimal effectiveness."
            except Exception as e:
                logging.error(f"Error getting explanation: {str(e)}")
                explanation_data = {
                    'plain_explanation': f"This medication is prescribed for your health. Please consult your healthcare provider for detailed information.",
                    'why_timing_matters': "Timing helps maintain steady medication levels for best results."
                }
            
            medication_obj = Medication(
                name=med.get('name', 'Unknown Medication'),
                dosage=med.get('dosage', 'As prescribed'),
                frequency=med.get('frequency', 'As prescribed'),
                timing=med.get('timing', []),
                duration=med.get('duration'),
                with_food=med.get('with_food', False),
                plain_language_explanation=explanation_data['plain_explanation'],
                why_timing_matters=explanation_data['why_timing_matters'],
                warnings=[]
            )
            medications_with_explanation.append(medication_obj)
        
        prescription = Prescription(
            patient_id=data.patient_id,
            image_data=data.image_base64[:100],
            extracted_text=extraction_result.get("extracted_text", ""),
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
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response. The prescription image may be unclear or invalid. Please try a clearer image.")
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
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"medication-{uuid.uuid4()}",
            system_message="You are a healthcare communication expert. Explain medical information in simple, plain language."
        ).with_model("gemini", "gemini-3-flash-preview")
        
        explanation_msg = UserMessage(
            text=f"""For the medication '{data.name}' at dosage '{data.dosage}' taken {data.frequency}:
            1. Explain what this medication typically does in simple, plain language (2-3 sentences)
            2. Explain why the timing matters (using Nudge Theory)
            
            Return ONLY valid JSON:
            {{
                "plain_explanation": "simple explanation",
                "why_timing_matters": "why timing is important"
            }}"""
        )
        
        explanation_response = await chat.send_message(explanation_msg)
        explanation_text = explanation_response.strip()
        if explanation_text.startswith('```json'):
            explanation_text = explanation_text[7:]
        if explanation_text.startswith('```'):
            explanation_text = explanation_text[3:]
        if explanation_text.endswith('```'):
            explanation_text = explanation_text[:-3]
        explanation_text = explanation_text.strip()
        
        explanation_data = json.loads(explanation_text)
        
        medication = Medication(
            name=data.name,
            dosage=data.dosage,
            frequency=data.frequency,
            timing=data.timing,
            duration=data.duration,
            with_food=data.with_food,
            plain_language_explanation=explanation_data['plain_explanation'],
            why_timing_matters=explanation_data['why_timing_matters'],
            warnings=[]
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
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"contraindication-{uuid.uuid4()}",
            system_message="You are a medical safety expert. Check for basic contraindications and drug interactions."
        ).with_model("gemini", "gemini-3-flash-preview")
        
        user_message = UserMessage(
            text=f"""Check if '{data.medication_name}' has any basic contraindications or interactions with these current medications: {', '.join(data.current_medications)}.
            
            Return ONLY valid JSON:
            {{
                "has_contraindications": true/false,
                "warnings": ["list of warnings or empty array"],
                "recommendations": "brief recommendation or 'No known contraindications'"
            }}"""
        )
        
        response = await chat.send_message(user_message)
        response_text = response.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        
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