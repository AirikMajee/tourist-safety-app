from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# AI Integration Setup
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Northeast India locations and risk data
NORTHEAST_LOCATIONS = {
    "assam": {
        "name": "Assam",
        "major_cities": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur"],
        "risk_zones": ["Brahmaputra River Areas", "Kaziranga National Park Periphery"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "1363"}
    },
    "meghalaya": {
        "name": "Meghalaya",
        "major_cities": ["Shillong", "Tura", "Jowai", "Nongpoh"],
        "risk_zones": ["Living Root Bridge Areas", "Dawki Border Areas"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "0364-2224066"}
    },
    "manipur": {
        "name": "Manipur",
        "major_cities": ["Imphal", "Thoubal", "Bishnupur"],
        "risk_zones": ["Border Areas", "Remote Hill Districts"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "0385-2414006"}
    },
    "mizoram": {
        "name": "Mizoram",
        "major_cities": ["Aizawl", "Lunglei", "Serchhip"],
        "risk_zones": ["Myanmar Border Areas", "Remote Villages"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "0389-2322649"}
    },
    "nagaland": {
        "name": "Nagaland",
        "major_cities": ["Kohima", "Dimapur", "Mokokchung"],
        "risk_zones": ["Myanmar Border Areas", "Remote Tribal Areas"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "0370-2290144"}
    },
    "tripura": {
        "name": "Tripura",
        "major_cities": ["Agartala", "Dharmanagar", "Udaipur"],
        "risk_zones": ["Bangladesh Border Areas", "Forest Areas"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "0381-2315347"}
    },
    "arunachal_pradesh": {
        "name": "Arunachal Pradesh",
        "major_cities": ["Itanagar", "Tawang", "Bomdila", "Pasighat"],
        "risk_zones": ["China Border Areas", "Remote Mountain Passes", "Tawang Sector"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "0360-2214255"}
    },
    "sikkim": {
        "name": "Sikkim",
        "major_cities": ["Gangtok", "Namchi", "Gyalshing", "Mangan"],
        "risk_zones": ["High Altitude Areas", "Nathu La Pass", "Glacier Areas"],
        "emergency_contacts": {"police": "100", "tourist_helpline": "03592-202033"}
    }
}

# Define Models
class TouristID(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tourist_name: str
    passport_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    phone_number: str
    email: str
    nationality: str
    emergency_contact_name: str
    emergency_contact_phone: str
    trip_start_date: datetime
    trip_end_date: datetime
    planned_destinations: List[str]
    current_location: Optional[Dict[str, float]] = None
    safety_score: int = Field(default=85)
    is_active: bool = Field(default=True)
    blockchain_hash: str = Field(default_factory=lambda: str(uuid.uuid4())[:16])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LocationUpdate(BaseModel):
    tourist_id: str
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    location_name: Optional[str] = None

class EmergencyAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tourist_id: str
    alert_type: str  # "panic", "geofence", "anomaly"
    latitude: float
    longitude: float
    message: Optional[str] = None
    status: str = Field(default="active")  # "active", "resolved", "false_alarm"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

class RiskZone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    state: str
    risk_type: str  # "flood", "cyclone", "seismic", "crime", "restricted"
    risk_level: int  # 1-10 scale
    coordinates: List[Dict[str, float]]  # Array of lat/lng points for polygon
    description: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CrowdReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reporter_id: Optional[str] = None
    latitude: float
    longitude: float
    report_type: str  # "safety_issue", "road_block", "weather", "crime"
    description: str
    photo_url: Optional[str] = None
    verification_status: str = Field(default="pending")  # "pending", "verified", "rejected"
    admin_comment: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verified_at: Optional[datetime] = None

class Advisory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    advisory_type: str  # "official", "crowdsourced"
    affected_areas: List[str]
    severity: str  # "low", "medium", "high", "critical"
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SafetyAnalysis(BaseModel):
    tourist_id: str
    current_safety_score: int
    risk_factors: List[str]
    recommendations: List[str]
    anomalies_detected: List[str]

# Create models for requests
class TouristIDCreate(BaseModel):
    tourist_name: str
    passport_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    phone_number: str
    email: str
    nationality: str
    emergency_contact_name: str
    emergency_contact_phone: str
    trip_start_date: datetime
    trip_end_date: datetime
    planned_destinations: List[str]

class EmergencyAlertCreate(BaseModel):
    tourist_id: str
    alert_type: str
    latitude: float
    longitude: float
    message: Optional[str] = None

# AI Helper Functions
async def analyze_tourist_behavior(tourist_id: str, recent_locations: List[Dict]) -> SafetyAnalysis:
    """Analyze tourist behavior using AI"""
    try:
        # Initialize AI chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"safety_analysis_{tourist_id}",
            system_message="You are a tourist safety AI analyst specializing in Northeast India. Analyze tourist behavior patterns and provide safety recommendations."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Prepare analysis data
        analysis_prompt = f"""
        Analyze the following tourist movement data for safety assessment:
        Tourist ID: {tourist_id}
        Recent locations: {json.dumps(recent_locations, default=str)}
        
        Provide analysis in this JSON format:
        {{
            "safety_score": <integer 0-100>,
            "risk_factors": ["factor1", "factor2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "anomalies_detected": ["anomaly1", "anomaly2"]
        }}
        
        Consider factors like:
        - Movement patterns in Northeast India
        - Time spent in risk zones
        - Deviation from planned routes
        - Movement during unsafe hours
        - Proximity to border areas
        """
        
        user_message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        try:
            ai_analysis = json.loads(response)
            return SafetyAnalysis(
                tourist_id=tourist_id,
                current_safety_score=ai_analysis.get("safety_score", 75),
                risk_factors=ai_analysis.get("risk_factors", []),
                recommendations=ai_analysis.get("recommendations", []),
                anomalies_detected=ai_analysis.get("anomalies_detected", [])
            )
        except json.JSONDecodeError:
            # Fallback if AI response is not valid JSON
            return SafetyAnalysis(
                tourist_id=tourist_id,
                current_safety_score=75,
                risk_factors=["Unable to analyze - AI response error"],
                recommendations=["Stay in well-lit areas", "Keep emergency contacts handy"],
                anomalies_detected=[]
            )
            
    except Exception as e:
        logging.error(f"AI analysis error: {str(e)}")
        return SafetyAnalysis(
            tourist_id=tourist_id,
            current_safety_score=70,
            risk_factors=["Analysis unavailable"],
            recommendations=["Follow standard safety protocols"],
            anomalies_detected=[]
        )

async def generate_efir(alert: EmergencyAlert, tourist: TouristID) -> Dict[str, Any]:
    """Generate automated E-FIR using AI"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"efir_{alert.id}",
            system_message="You are an AI assistant for generating E-FIR (Electronic First Information Report) for tourist safety incidents in Northeast India."
        ).with_model("gemini", "gemini-2.0-flash")
        
        efir_prompt = f"""
        Generate an E-FIR for the following tourist emergency:
        
        Tourist Details:
        - Name: {tourist.tourist_name}
        - ID: {tourist.id}
        - Contact: {tourist.phone_number}
        - Emergency Contact: {tourist.emergency_contact_name} ({tourist.emergency_contact_phone})
        
        Incident Details:
        - Type: {alert.alert_type}
        - Location: {alert.latitude}, {alert.longitude}
        - Time: {alert.created_at}
        - Message: {alert.message or "No message provided"}
        
        Generate a formal E-FIR report in JSON format with these fields:
        {{
            "fir_number": "<auto-generated>",
            "incident_summary": "<brief summary>",
            "location_details": "<detailed location>",
            "recommended_actions": ["action1", "action2"],
            "priority_level": "<high/medium/low>",
            "assigned_units": ["unit1", "unit2"]
        }}
        """
        
        user_message = UserMessage(text=efir_prompt)
        response = await chat.send_message(user_message)
        
        try:
            efir_data = json.loads(response)
            efir_data["generated_at"] = datetime.now(timezone.utc).isoformat()
            return efir_data
        except json.JSONDecodeError:
            return {
                "fir_number": f"E-FIR-{alert.id[:8]}",
                "incident_summary": f"Tourist emergency alert - {alert.alert_type}",
                "location_details": f"Coordinates: {alert.latitude}, {alert.longitude}",
                "recommended_actions": ["Deploy nearest response team", "Contact emergency services"],
                "priority_level": "high",
                "assigned_units": ["Tourist Police", "Local Police Station"],
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logging.error(f"E-FIR generation error: {str(e)}")
        return {
            "fir_number": f"E-FIR-{alert.id[:8]}",
            "incident_summary": "Emergency alert generated",
            "location_details": f"Coordinates: {alert.latitude}, {alert.longitude}",
            "recommended_actions": ["Manual review required"],
            "priority_level": "high",
            "assigned_units": ["Tourist Police"],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

# API Routes

# Tourist ID Management
@api_router.post("/tourist-id/register", response_model=TouristID)
async def register_tourist(tourist_data: TouristIDCreate):
    """Register new tourist and generate digital ID"""
    tourist_dict = tourist_data.dict()
    tourist_obj = TouristID(**tourist_dict)
    
    # Convert datetime objects to ISO format for MongoDB
    tourist_mongo = tourist_obj.dict()
    tourist_mongo["trip_start_date"] = tourist_obj.trip_start_date.isoformat()
    tourist_mongo["trip_end_date"] = tourist_obj.trip_end_date.isoformat()
    tourist_mongo["created_at"] = tourist_obj.created_at.isoformat()
    
    await db.tourists.insert_one(tourist_mongo)
    return tourist_obj

@api_router.get("/tourist-id/{tourist_id}", response_model=TouristID)
async def get_tourist(tourist_id: str):
    """Get tourist information by ID"""
    tourist = await db.tourists.find_one({"id": tourist_id})
    if not tourist:
        raise HTTPException(status_code=404, detail="Tourist not found")
    
    # Convert ISO strings back to datetime objects
    tourist["trip_start_date"] = datetime.fromisoformat(tourist["trip_start_date"])
    tourist["trip_end_date"] = datetime.fromisoformat(tourist["trip_end_date"])
    tourist["created_at"] = datetime.fromisoformat(tourist["created_at"])
    
    return TouristID(**tourist)

# Location Tracking
@api_router.post("/location/update")
async def update_location(location_data: LocationUpdate, background_tasks: BackgroundTasks):
    """Update tourist location and perform safety analysis"""
    # Store location update
    location_mongo = location_data.dict()
    location_mongo["timestamp"] = location_data.timestamp.isoformat()
    
    await db.location_history.insert_one(location_mongo)
    
    # Update current location in tourist record
    await db.tourists.update_one(
        {"id": location_data.tourist_id},
        {"$set": {"current_location": {"lat": location_data.latitude, "lng": location_data.longitude}}}
    )
    
    # Perform background safety analysis
    background_tasks.add_task(perform_safety_check, location_data.tourist_id)
    
    return {"status": "location updated", "message": "Safety analysis initiated"}

@api_router.get("/location/history/{tourist_id}")
async def get_location_history(tourist_id: str, limit: int = 50):
    """Get location history for a tourist"""
    locations = await db.location_history.find(
        {"tourist_id": tourist_id}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Convert ISO strings back to datetime objects
    for location in locations:
        location["timestamp"] = datetime.fromisoformat(location["timestamp"])
    
    return locations

# Emergency Alerts
@api_router.post("/emergency/alert", response_model=EmergencyAlert)
async def create_emergency_alert(alert_data: EmergencyAlertCreate, background_tasks: BackgroundTasks):
    """Create emergency alert and trigger response"""
    alert_dict = alert_data.dict()
    alert_obj = EmergencyAlert(**alert_dict)
    
    # Store alert
    alert_mongo = alert_obj.dict()
    alert_mongo["created_at"] = alert_obj.created_at.isoformat()
    
    await db.emergency_alerts.insert_one(alert_mongo)
    
    # Trigger emergency response
    background_tasks.add_task(handle_emergency_response, alert_obj.id)
    
    return alert_obj

@api_router.get("/emergency/alerts", response_model=List[EmergencyAlert])
async def get_emergency_alerts(status: Optional[str] = None, limit: int = 100):
    """Get emergency alerts"""
    query = {}
    if status:
        query["status"] = status
    
    alerts = await db.emergency_alerts.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Convert ISO strings back to datetime objects
    for alert in alerts:
        alert["created_at"] = datetime.fromisoformat(alert["created_at"])
        if alert.get("resolved_at"):
            alert["resolved_at"] = datetime.fromisoformat(alert["resolved_at"])
    
    return [EmergencyAlert(**alert) for alert in alerts]

# Risk Zones
@api_router.get("/risk-zones", response_model=List[RiskZone])
async def get_risk_zones(state: Optional[str] = None, risk_type: Optional[str] = None):
    """Get risk zones"""
    query = {"is_active": True}
    if state:
        query["state"] = state
    if risk_type:
        query["risk_type"] = risk_type
    
    zones = await db.risk_zones.find(query).to_list(100)
    
    # Convert ISO strings back to datetime objects
    for zone in zones:
        zone["created_at"] = datetime.fromisoformat(zone["created_at"])
    
    return [RiskZone(**zone) for zone in zones]

@api_router.post("/risk-zones", response_model=RiskZone)
async def create_risk_zone(zone_data: RiskZone):
    """Create new risk zone"""
    zone_mongo = zone_data.dict()
    zone_mongo["created_at"] = zone_data.created_at.isoformat()
    
    await db.risk_zones.insert_one(zone_mongo)
    return zone_data

# Crowd Reports
@api_router.post("/crowd-reports", response_model=CrowdReport)
async def submit_crowd_report(report_data: CrowdReport):
    """Submit crowd-sourced safety report"""
    report_mongo = report_data.dict()
    report_mongo["created_at"] = report_data.created_at.isoformat()
    
    await db.crowd_reports.insert_one(report_mongo)
    return report_data

@api_router.get("/crowd-reports", response_model=List[CrowdReport])
async def get_crowd_reports(status: Optional[str] = None, limit: int = 50):
    """Get crowd reports"""
    query = {}
    if status:
        query["verification_status"] = status
    
    reports = await db.crowd_reports.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Convert ISO strings back to datetime objects
    for report in reports:
        report["created_at"] = datetime.fromisoformat(report["created_at"])
        if report.get("verified_at"):
            report["verified_at"] = datetime.fromisoformat(report["verified_at"])
    
    return [CrowdReport(**report) for report in reports]

@api_router.put("/crowd-reports/{report_id}/verify")
async def verify_crowd_report(report_id: str, action: str, admin_comment: Optional[str] = None):
    """Verify or reject crowd report"""
    if action not in ["verified", "rejected"]:
        raise HTTPException(status_code=400, detail="Action must be 'verified' or 'rejected'")
    
    update_data = {
        "verification_status": action,
        "verified_at": datetime.now(timezone.utc).isoformat()
    }
    
    if admin_comment:
        update_data["admin_comment"] = admin_comment
    
    result = await db.crowd_reports.update_one(
        {"id": report_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"status": "updated", "action": action}

# Advisories
@api_router.get("/advisories", response_model=List[Advisory])
async def get_advisories(advisory_type: Optional[str] = None, is_active: bool = True):
    """Get travel advisories"""
    query = {"is_active": is_active}
    if advisory_type:
        query["advisory_type"] = advisory_type
    
    advisories = await db.advisories.find(query).sort("created_at", -1).to_list(50)
    
    # Convert ISO strings back to datetime objects
    for advisory in advisories:
        advisory["created_at"] = datetime.fromisoformat(advisory["created_at"])
        if advisory.get("expires_at"):
            advisory["expires_at"] = datetime.fromisoformat(advisory["expires_at"])
    
    return [Advisory(**advisory) for advisory in advisories]

@api_router.post("/advisories", response_model=Advisory)
async def create_advisory(advisory_data: Advisory):
    """Create new advisory"""
    advisory_mongo = advisory_data.dict()
    advisory_mongo["created_at"] = advisory_data.created_at.isoformat()
    if advisory_data.expires_at:
        advisory_mongo["expires_at"] = advisory_data.expires_at.isoformat()
    
    await db.advisories.insert_one(advisory_mongo)
    return advisory_data

# Safety Analysis
@api_router.get("/safety/analysis/{tourist_id}", response_model=SafetyAnalysis)
async def get_safety_analysis(tourist_id: str):
    """Get AI-powered safety analysis for tourist"""
    # Get recent location history
    recent_locations = await db.location_history.find(
        {"tourist_id": tourist_id}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    # Perform AI analysis
    analysis = await analyze_tourist_behavior(tourist_id, recent_locations)
    
    # Update tourist safety score
    await db.tourists.update_one(
        {"id": tourist_id},
        {"$set": {"safety_score": analysis.current_safety_score}}
    )
    
    return analysis

# Dashboard APIs
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_tourists = await db.tourists.count_documents({"is_active": True})
    active_alerts = await db.emergency_alerts.count_documents({"status": "active"})
    total_reports = await db.crowd_reports.count_documents({})
    verified_reports = await db.crowd_reports.count_documents({"verification_status": "verified"})
    
    return {
        "total_active_tourists": total_tourists,
        "active_emergency_alerts": active_alerts,
        "total_crowd_reports": total_reports,
        "verified_crowd_reports": verified_reports,
        "verification_rate": round((verified_reports / max(total_reports, 1)) * 100, 2)
    }

@api_router.get("/dashboard/tourist-heatmap")
async def get_tourist_heatmap():
    """Get tourist location heatmap data"""
    # Get all active tourists with current locations
    tourists = await db.tourists.find(
        {"is_active": True, "current_location": {"$exists": True}}
    ).to_list(1000)
    
    heatmap_data = []
    for tourist in tourists:
        if tourist.get("current_location"):
            heatmap_data.append({
                "lat": tourist["current_location"]["lat"],
                "lng": tourist["current_location"]["lng"],
                "intensity": 1
            })
    
    return heatmap_data

# Northeast India specific data
@api_router.get("/northeast/locations")
async def get_northeast_locations():
    """Get Northeast India location data"""
    return NORTHEAST_LOCATIONS

@api_router.get("/northeast/emergency-contacts/{state}")
async def get_emergency_contacts(state: str):
    """Get emergency contacts for specific state"""
    state_data = NORTHEAST_LOCATIONS.get(state.lower())
    if not state_data:
        raise HTTPException(status_code=404, detail="State not found")
    
    return state_data["emergency_contacts"]

# Background Tasks
async def perform_safety_check(tourist_id: str):
    """Background task to check tourist safety"""
    try:
        # Get recent locations
        recent_locations = await db.location_history.find(
            {"tourist_id": tourist_id}
        ).sort("timestamp", -1).limit(5).to_list(5)
        
        if not recent_locations:
            return
        
        # Check for anomalies (e.g., no movement for too long, in risk zones)
        latest_location = recent_locations[0]
        
        # Check if in risk zone
        risk_zones = await db.risk_zones.find({"is_active": True}).to_list(100)
        
        for zone in risk_zones:
            # Simple point-in-polygon check (simplified for prototype)
            if len(zone["coordinates"]) > 0:
                # Create geofence alert if needed
                alert_data = {
                    "tourist_id": tourist_id,
                    "alert_type": "geofence",
                    "latitude": latest_location["latitude"],
                    "longitude": latest_location["longitude"],
                    "message": f"Tourist entered {zone['risk_type']} risk zone: {zone['name']}"
                }
                
                # Check if similar alert already exists
                existing_alert = await db.emergency_alerts.find_one({
                    "tourist_id": tourist_id,
                    "alert_type": "geofence",
                    "status": "active"
                })
                
                if not existing_alert:
                    alert_obj = EmergencyAlert(**alert_data)
                    alert_mongo = alert_obj.dict()
                    alert_mongo["created_at"] = alert_obj.created_at.isoformat()
                    await db.emergency_alerts.insert_one(alert_mongo)
        
    except Exception as e:
        logging.error(f"Safety check error: {str(e)}")

async def handle_emergency_response(alert_id: str):
    """Background task to handle emergency response"""
    try:
        # Get alert details
        alert = await db.emergency_alerts.find_one({"id": alert_id})
        if not alert:
            return
        
        alert["created_at"] = datetime.fromisoformat(alert["created_at"])
        alert_obj = EmergencyAlert(**alert)
        
        # Get tourist details
        tourist = await db.tourists.find_one({"id": alert_obj.tourist_id})
        if not tourist:
            return
        
        tourist["trip_start_date"] = datetime.fromisoformat(tourist["trip_start_date"])
        tourist["trip_end_date"] = datetime.fromisoformat(tourist["trip_end_date"])
        tourist["created_at"] = datetime.fromisoformat(tourist["created_at"])
        tourist_obj = TouristID(**tourist)
        
        # Generate E-FIR
        efir_data = await generate_efir(alert_obj, tourist_obj)
        
        # Store E-FIR
        efir_record = {
            "id": str(uuid.uuid4()),
            "alert_id": alert_id,
            "tourist_id": alert_obj.tourist_id,
            "efir_data": efir_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.efir_records.insert_one(efir_record)
        
        logging.info(f"E-FIR generated for alert {alert_id}: {efir_data['fir_number']}")
        
    except Exception as e:
        logging.error(f"Emergency response error: {str(e)}")

# Initialize sample data
@api_router.post("/init/sample-data")
async def initialize_sample_data():
    """Initialize sample data for Northeast India"""
    try:
        # Sample risk zones
        sample_risk_zones = [
            {
                "name": "Brahmaputra Flood Zone",
                "state": "assam",
                "risk_type": "flood",
                "risk_level": 8,
                "coordinates": [
                    {"lat": 26.1445, "lng": 91.7362},
                    {"lat": 26.1500, "lng": 91.7400},
                    {"lat": 26.1400, "lng": 91.7450},
                    {"lat": 26.1350, "lng": 91.7300}
                ],
                "description": "High flood risk area along Brahmaputra River",
                "is_active": True
            },
            {
                "name": "Tawang Border Area",
                "state": "arunachal_pradesh",
                "risk_type": "restricted",
                "risk_level": 9,
                "coordinates": [
                    {"lat": 27.5856, "lng": 91.8575},
                    {"lat": 27.6000, "lng": 91.8700},
                    {"lat": 27.5800, "lng": 91.8800},
                    {"lat": 27.5700, "lng": 91.8500}
                ],
                "description": "Restricted border area - special permits required",
                "is_active": True
            },
            {
                "name": "Guwahati Crime Hotspot",
                "state": "assam",
                "risk_type": "crime",
                "risk_level": 6,
                "coordinates": [
                    {"lat": 26.1433, "lng": 91.7898},
                    {"lat": 26.1500, "lng": 91.7950},
                    {"lat": 26.1400, "lng": 91.8000},
                    {"lat": 26.1350, "lng": 91.7850}
                ],
                "description": "Higher crime incidence area - exercise caution",
                "is_active": True
            }
        ]
        
        for zone_data in sample_risk_zones:
            zone_obj = RiskZone(**zone_data)
            zone_mongo = zone_obj.dict()
            zone_mongo["created_at"] = zone_obj.created_at.isoformat()
            await db.risk_zones.insert_one(zone_mongo)
        
        # Sample advisories
        sample_advisories = [
            {
                "title": "Monsoon Travel Advisory",
                "content": "Heavy rainfall expected in Assam and Meghalaya. Avoid low-lying areas and riverbanks.",
                "advisory_type": "official",
                "affected_areas": ["assam", "meghalaya"],
                "severity": "high",
                "is_active": True,
                "expires_at": datetime(2025, 8, 31, 23, 59, 59, tzinfo=timezone.utc)
            },
            {
                "title": "Inner Line Permit Required",
                "content": "All tourists visiting Arunachal Pradesh must obtain Inner Line Permit before travel.",
                "advisory_type": "official",
                "affected_areas": ["arunachal_pradesh"],
                "severity": "critical",
                "is_active": True
            }
        ]
        
        for advisory_data in sample_advisories:
            advisory_obj = Advisory(**advisory_data)
            advisory_mongo = advisory_obj.dict()
            advisory_mongo["created_at"] = advisory_obj.created_at.isoformat()
            if advisory_obj.expires_at:
                advisory_mongo["expires_at"] = advisory_obj.expires_at.isoformat()
            await db.advisories.insert_one(advisory_mongo)
        
        return {"status": "success", "message": "Sample data initialized"}
        
    except Exception as e:
        logging.error(f"Sample data initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize sample data")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()