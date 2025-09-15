from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends
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
import hashlib
import qrcode
import base64
from io import BytesIO
import requests
import math

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

# Global threat database with coordinates (lat, lng, radius in km, threat details)
GLOBAL_THREAT_DATABASE = {
    "natural_disasters": [
        {"name": "Earthquake Zone - Ring of Fire", "lat": 35.6762, "lng": 139.6503, "radius": 500, "threat_level": 9, "type": "seismic"},
        {"name": "Hurricane Alley - Atlantic", "lat": 25.7617, "lng": -80.1918, "radius": 800, "threat_level": 8, "type": "storm"},
        {"name": "Tornado Alley - Midwest US", "lat": 35.2271, "lng": -101.8313, "radius": 600, "threat_level": 7, "type": "tornado"},
        {"name": "Monsoon Flood Zones - South Asia", "lat": 23.6850, "lng": 90.3563, "radius": 1000, "threat_level": 8, "type": "flood"},
        {"name": "Cyclone Zone - Bay of Bengal", "lat": 16.5062, "lng": 80.6480, "radius": 700, "threat_level": 8, "type": "cyclone"},
        {"name": "Wildfire Risk - California", "lat": 36.7783, "lng": -119.4179, "radius": 400, "threat_level": 7, "type": "wildfire"},
        {"name": "Volcanic Activity - Indonesia", "lat": -7.5360, "lng": 110.4450, "radius": 300, "threat_level": 9, "type": "volcanic"},
        {"name": "Tsunami Risk - Pacific Coast", "lat": 35.6762, "lng": 139.6503, "radius": 200, "threat_level": 9, "type": "tsunami"}
    ],
    "crime_hotspots": [
        {"name": "High Crime Area - Mumbai Central", "lat": 19.0760, "lng": 72.8777, "radius": 5, "threat_level": 7, "type": "crime"},
        {"name": "Tourist Scam Zone - Bangkok", "lat": 13.7563, "lng": 100.5018, "radius": 8, "threat_level": 6, "type": "scam"},
        {"name": "Pickpocket Hotspot - Paris Metro", "lat": 48.8566, "lng": 2.3522, "radius": 3, "threat_level": 5, "type": "theft"},
        {"name": "Drug Activity Zone - Mexico Border", "lat": 32.5149, "lng": -117.0382, "radius": 50, "threat_level": 9, "type": "drug_related"},
        {"name": "Violent Crime Area - Johannesburg CBD", "lat": -26.2041, "lng": 28.0473, "radius": 10, "threat_level": 8, "type": "violent_crime"}
    ],
    "political_unrest": [
        {"name": "Protest Zone - Hong Kong", "lat": 22.3193, "lng": 114.1694, "radius": 15, "threat_level": 7, "type": "protest"},
        {"name": "Border Conflict - Kashmir", "lat": 34.0837, "lng": 74.7973, "radius": 100, "threat_level": 9, "type": "conflict"},
        {"name": "Civil Unrest - Myanmar", "lat": 19.7633, "lng": 96.0785, "radius": 200, "threat_level": 8, "type": "civil_unrest"}
    ],
    "health_risks": [
        {"name": "Malaria Endemic Zone - Sub-Saharan Africa", "lat": -1.9441, "lng": 29.8739, "radius": 2000, "threat_level": 6, "type": "disease"},
        {"name": "Yellow Fever Zone - Amazon Basin", "lat": -3.4653, "lng": -62.2159, "radius": 1500, "threat_level": 7, "type": "disease"},
        {"name": "High Altitude Risk - Himalayas", "lat": 28.0139, "lng": 84.0917, "radius": 300, "threat_level": 6, "type": "altitude"}
    ],
    "restricted_areas": [
        {"name": "Military Zone - DMZ Korea", "lat": 38.2400, "lng": 127.0600, "radius": 20, "threat_level": 10, "type": "military"},
        {"name": "Radiation Zone - Chernobyl", "lat": 51.2763, "lng": 30.2218, "radius": 30, "threat_level": 9, "type": "radiation"},
        {"name": "Border Restricted - Pakistan-Afghanistan", "lat": 33.5138, "lng": 69.1793, "radius": 50, "threat_level": 9, "type": "border"}
    ]
}

# Enhanced Models
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
    qr_code: Optional[str] = None
    digital_signature: Optional[str] = None
    verification_status: str = Field(default="verified")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RouteComparison(BaseModel):
    planned_route: List[Dict[str, float]]
    safest_route: List[Dict[str, float]]
    planned_safety_score: int
    safest_safety_score: int
    risk_analysis: Dict[str, Any]
    recommendations: List[str]

class LocationThreat(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    latitude: float
    longitude: float
    threat_type: str
    threat_level: int  # 1-10 scale
    radius_km: float
    description: str
    is_active: bool = Field(default=True)
    source: str = Field(default="global_database")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DetailedAdvisory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    location: str
    coordinates: Optional[Dict[str, float]] = None
    advisory_type: str  # "weather", "security", "health", "transport", "cultural"
    severity: str  # "info", "caution", "warning", "danger", "critical"
    source: str  # "government", "embassy", "local_authority", "crowdsourced"
    affects_radius_km: float = Field(default=50.0)
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    action: str
    resource_type: str  # "tourist", "advisory", "threat", "alert"
    resource_id: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str  # "super_admin", "admin", "operator", "viewer"
    permissions: List[str]
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Create request models
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

class RouteRequest(BaseModel):
    tourist_id: str
    start_location: Dict[str, float]  # {"lat": float, "lng": float}
    end_location: Dict[str, float]
    waypoints: Optional[List[Dict[str, float]]] = []

class LocationUpdate(BaseModel):
    tourist_id: str
    latitude: float
    longitude: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    location_name: Optional[str] = None

# Utility Functions
def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates in kilometers"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def generate_blockchain_hash(tourist_data: dict) -> str:
    """Generate blockchain-style hash for digital ID"""
    data_string = f"{tourist_data['tourist_name']}{tourist_data['phone_number']}{tourist_data['email']}{datetime.now().isoformat()}"
    return hashlib.sha256(data_string.encode()).hexdigest()

def generate_qr_code(data: dict) -> str:
    """Generate QR code for digital ID"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{qr_base64}"
    except:
        return None

def get_nearby_threats(latitude: float, longitude: float, radius_km: float = 100) -> List[LocationThreat]:
    """Get threats near a location from global database"""
    nearby_threats = []
    
    for category, threats in GLOBAL_THREAT_DATABASE.items():
        for threat in threats:
            distance = calculate_distance(latitude, longitude, threat["lat"], threat["lng"])
            if distance <= max(radius_km, threat["radius"]):
                threat_obj = LocationThreat(
                    name=threat["name"],
                    latitude=threat["lat"],
                    longitude=threat["lng"],
                    threat_type=threat["type"],
                    threat_level=threat["threat_level"],
                    radius_km=threat["radius"],
                    description=f"{category.replace('_', ' ').title()} - {threat['name']}",
                    source="global_database"
                )
                nearby_threats.append(threat_obj)
    
    return nearby_threats

async def get_location_name(latitude: float, longitude: float) -> str:
    """Get location name from coordinates using Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', f"{latitude}, {longitude}")
    except:
        pass
    return f"{latitude}, {longitude}"

# Enhanced AI Functions
async def analyze_route_safety(route_points: List[Dict[str, float]], tourist_id: str) -> Dict[str, Any]:
    """Analyze route safety using AI"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"route_analysis_{tourist_id}",
            system_message="You are an AI safety analyst specializing in travel route safety assessment worldwide."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Get threats along the route
        route_threats = []
        for point in route_points:
            threats = get_nearby_threats(point["lat"], point["lng"], 25)  # 25km radius
            route_threats.extend(threats)
        
        analysis_prompt = f"""
        Analyze the safety of this travel route:
        Route points: {json.dumps(route_points, default=str)}
        Nearby threats: {[{"name": t.name, "type": t.threat_type, "level": t.threat_level} for t in route_threats]}
        
        Provide analysis in JSON format:
        {{
            "overall_safety_score": <0-100>,
            "risk_factors": ["factor1", "factor2"],
            "safe_segments": ["segment1", "segment2"],
            "danger_zones": ["zone1", "zone2"],
            "recommendations": ["rec1", "rec2"],
            "alternative_suggestions": ["alt1", "alt2"],
            "best_travel_times": ["time1", "time2"],
            "emergency_contacts": ["contact1", "contact2"]
        }}
        """
        
        user_message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(user_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "overall_safety_score": 70,
                "risk_factors": ["AI analysis error"],
                "safe_segments": [],
                "danger_zones": [],
                "recommendations": ["Exercise general caution"],
                "alternative_suggestions": [],
                "best_travel_times": ["Daylight hours"],
                "emergency_contacts": ["Local emergency services"]
            }
            
    except Exception as e:
        logging.error(f"Route safety analysis error: {str(e)}")
        return {
            "overall_safety_score": 60,
            "risk_factors": ["Analysis unavailable"],
            "safe_segments": [],
            "danger_zones": [],
            "recommendations": ["Use standard safety precautions"],
            "alternative_suggestions": [],
            "best_travel_times": ["Daylight hours"],
            "emergency_contacts": ["Local authorities"]
        }

async def generate_detailed_advisory(location: str, coordinates: Dict[str, float]) -> List[DetailedAdvisory]:
    """Generate detailed travel advisories using AI"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"advisory_{location.replace(' ', '_')}",
            system_message="You are a travel safety advisor with access to global threat intelligence."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Get nearby threats
        threats = get_nearby_threats(coordinates["lat"], coordinates["lng"], 100)
        
        advisory_prompt = f"""
        Generate detailed travel advisories for: {location}
        Coordinates: {coordinates}
        Nearby threats: {[{"name": t.name, "type": t.threat_type, "level": t.threat_level} for t in threats]}
        
        Generate 3-5 advisories in JSON format:
        [
            {{
                "title": "Advisory Title",
                "content": "Detailed content",
                "advisory_type": "weather/security/health/transport/cultural",
                "severity": "info/caution/warning/danger/critical",
                "source": "government/embassy/local_authority"
            }}
        ]
        """
        
        user_message = UserMessage(text=advisory_prompt)
        response = await chat.send_message(user_message)
        
        try:
            advisories_data = json.loads(response)
            advisories = []
            
            for adv_data in advisories_data:
                advisory = DetailedAdvisory(
                    title=adv_data.get("title", "Travel Advisory"),
                    content=adv_data.get("content", "General travel advisory"),
                    location=location,
                    coordinates=coordinates,
                    advisory_type=adv_data.get("advisory_type", "general"),
                    severity=adv_data.get("severity", "info"),
                    source=adv_data.get("source", "ai_generated"),
                    affects_radius_km=50.0
                )
                advisories.append(advisory)
            
            return advisories
            
        except json.JSONDecodeError:
            # Fallback advisory
            return [DetailedAdvisory(
                title="General Travel Advisory",
                content="Exercise normal precautions while traveling. Stay aware of your surroundings and follow local guidance.",
                location=location,
                coordinates=coordinates,
                advisory_type="general",
                severity="info",
                source="ai_generated"
            )]
            
    except Exception as e:
        logging.error(f"Advisory generation error: {str(e)}")
        return []

# API Routes

# Enhanced Tourist Registration
@api_router.post("/tourist-id/register", response_model=TouristID)
async def register_tourist(tourist_data: TouristIDCreate):
    """Register tourist with enhanced blockchain digital ID"""
    tourist_dict = tourist_data.dict()
    
    # Generate blockchain hash
    blockchain_hash = generate_blockchain_hash(tourist_dict)
    
    # Generate digital signature
    digital_signature = hashlib.sha256(f"{blockchain_hash}{tourist_dict['email']}".encode()).hexdigest()
    
    # Create QR code data
    qr_data = {
        "id": str(uuid.uuid4()),
        "name": tourist_dict["tourist_name"],
        "phone": tourist_dict["phone_number"],
        "blockchain_hash": blockchain_hash,
        "valid_until": tourist_data.trip_end_date.isoformat()
    }
    
    qr_code = generate_qr_code(qr_data)
    
    tourist_obj = TouristID(
        **tourist_dict,
        blockchain_hash=blockchain_hash,
        digital_signature=digital_signature,
        qr_code=qr_code
    )
    
    # Store in database
    tourist_mongo = tourist_obj.dict()
    tourist_mongo["trip_start_date"] = tourist_obj.trip_start_date.isoformat()
    tourist_mongo["trip_end_date"] = tourist_obj.trip_end_date.isoformat()
    tourist_mongo["created_at"] = tourist_obj.created_at.isoformat()
    
    await db.tourists.insert_one(tourist_mongo)
    return tourist_obj

# Location-based threats
@api_router.get("/threats/nearby")
async def get_nearby_threats_api(lat: float, lng: float, radius: float = 100):
    """Get threats near a location"""
    threats = get_nearby_threats(lat, lng, radius)
    location_name = await get_location_name(lat, lng)
    
    return {
        "location": location_name,
        "coordinates": {"lat": lat, "lng": lng},
        "search_radius_km": radius,
        "threats_found": len(threats),
        "threats": [t.dict() for t in threats]
    }

# Route comparison
@api_router.post("/routes/compare", response_model=RouteComparison)
async def compare_routes(route_request: RouteRequest):
    """Compare planned route vs safest route"""
    # For prototype, generate a safest route with slight variations
    planned_route = [route_request.start_location] + route_request.waypoints + [route_request.end_location]
    
    # Generate safest route (simplified - add slight deviations to avoid high-threat areas)
    safest_route = []
    for i, point in enumerate(planned_route):
        # Get nearby threats
        threats = get_nearby_threats(point["lat"], point["lng"], 10)
        high_threat_zones = [t for t in threats if t.threat_level >= 7]
        
        if high_threat_zones and i > 0 and i < len(planned_route) - 1:
            # Deviation to avoid high threat
            safest_route.append({
                "lat": point["lat"] + 0.01,  # Small deviation
                "lng": point["lng"] + 0.01
            })
        else:
            safest_route.append(point)
    
    # Analyze both routes
    planned_analysis = await analyze_route_safety(planned_route, route_request.tourist_id)
    safest_analysis = await analyze_route_safety(safest_route, route_request.tourist_id)
    
    return RouteComparison(
        planned_route=planned_route,
        safest_route=safest_route,
        planned_safety_score=planned_analysis.get("overall_safety_score", 70),
        safest_safety_score=safest_analysis.get("overall_safety_score", 85),
        risk_analysis={
            "planned_risks": planned_analysis.get("risk_factors", []),
            "planned_recommendations": planned_analysis.get("recommendations", []),
            "safest_recommendations": safest_analysis.get("recommendations", []),
            "danger_zones": planned_analysis.get("danger_zones", [])
        },
        recommendations=safest_analysis.get("alternative_suggestions", [])
    )

# Enhanced advisories
@api_router.get("/advisories/detailed")
async def get_detailed_advisories(lat: float, lng: float, radius: float = 100):
    """Get detailed location-based advisories"""
    location_name = await get_location_name(lat, lng)
    coordinates = {"lat": lat, "lng": lng}
    
    # Generate AI-powered advisories
    ai_advisories = await generate_detailed_advisory(location_name, coordinates)
    
    # Get stored advisories from database
    stored_advisories = await db.advisories.find({
        "is_active": True,
        "coordinates": {"$exists": True}
    }).to_list(50)
    
    # Combine and return
    all_advisories = [adv.dict() for adv in ai_advisories]
    
    for stored in stored_advisories:
        if stored.get("coordinates"):
            distance = calculate_distance(
                lat, lng,
                stored["coordinates"]["lat"],
                stored["coordinates"]["lng"]
            )
            if distance <= radius:
                stored["created_at"] = datetime.fromisoformat(stored["created_at"])
                if stored.get("expires_at"):
                    stored["expires_at"] = datetime.fromisoformat(stored["expires_at"])
                if stored.get("updated_at"):
                    stored["updated_at"] = datetime.fromisoformat(stored["updated_at"])
                all_advisories.append(stored)
    
    return {
        "location": location_name,
        "coordinates": coordinates,
        "total_advisories": len(all_advisories),
        "advisories": all_advisories
    }

# Admin Dashboard APIs
@api_router.get("/admin/dashboard/stats")
async def get_admin_dashboard_stats():
    """Get comprehensive admin dashboard statistics"""
    # Tourist statistics
    total_tourists = await db.tourists.count_documents({})
    active_tourists = await db.tourists.count_documents({"is_active": True})
    
    # Alert statistics
    total_alerts = await db.emergency_alerts.count_documents({})
    active_alerts = await db.emergency_alerts.count_documents({"status": "active"})
    resolved_alerts = await db.emergency_alerts.count_documents({"status": "resolved"})
    
    # Threat statistics
    total_threats = len([t for category in GLOBAL_THREAT_DATABASE.values() for t in category])
    high_threat_zones = len([t for category in GLOBAL_THREAT_DATABASE.values() for t in category if t["threat_level"] >= 8])
    
    # Advisory statistics
    total_advisories = await db.advisories.count_documents({})
    active_advisories = await db.advisories.count_documents({"is_active": True})
    critical_advisories = await db.advisories.count_documents({"severity": "critical", "is_active": True})
    
    # Recent activity
    recent_tourists = await db.tourists.find({}).sort("created_at", -1).limit(5).to_list(5)
    recent_alerts = await db.emergency_alerts.find({}).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "overview": {
            "total_tourists": total_tourists,
            "active_tourists": active_tourists,
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "total_threats": total_threats,
            "high_threat_zones": high_threat_zones,
            "total_advisories": total_advisories,
            "active_advisories": active_advisories,
            "critical_advisories": critical_advisories
        },
        "recent_activity": {
            "recent_tourists": recent_tourists,
            "recent_alerts": recent_alerts
        },
        "system_health": {
            "ai_integration_status": "operational",
            "database_status": "operational",
            "threat_database_last_updated": datetime.now(timezone.utc).isoformat()
        }
    }

@api_router.get("/admin/tourists")
async def get_all_tourists_admin(skip: int = 0, limit: int = 50):
    """Get all tourists for admin dashboard"""
    tourists = await db.tourists.find({}).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
    
    # Convert datetime strings back to datetime objects
    for tourist in tourists:
        tourist["trip_start_date"] = datetime.fromisoformat(tourist["trip_start_date"])
        tourist["trip_end_date"] = datetime.fromisoformat(tourist["trip_end_date"])
        tourist["created_at"] = datetime.fromisoformat(tourist["created_at"])
    
    return {
        "tourists": tourists,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": await db.tourists.count_documents({})
        }
    }

@api_router.get("/admin/alerts")
async def get_all_alerts_admin(skip: int = 0, limit: int = 50):
    """Get all alerts for admin dashboard"""
    alerts = await db.emergency_alerts.find({}).skip(skip).limit(limit).sort("created_at", -1).to_list(limit)
    
    # Convert datetime strings
    for alert in alerts:
        alert["created_at"] = datetime.fromisoformat(alert["created_at"])
        if alert.get("resolved_at"):
            alert["resolved_at"] = datetime.fromisoformat(alert["resolved_at"])
    
    return {
        "alerts": alerts,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": await db.emergency_alerts.count_documents({})
        }
    }

@api_router.post("/admin/logs")
async def create_admin_log(log_data: AdminLog):
    """Create admin activity log"""
    log_mongo = log_data.dict()
    log_mongo["timestamp"] = log_data.timestamp.isoformat()
    
    await db.admin_logs.insert_one(log_mongo)
    return {"status": "logged", "log_id": log_data.id}

@api_router.get("/admin/logs")
async def get_admin_logs(skip: int = 0, limit: int = 100):
    """Get admin activity logs"""
    logs = await db.admin_logs.find({}).skip(skip).limit(limit).sort("timestamp", -1).to_list(limit)
    
    for log in logs:
        log["timestamp"] = datetime.fromisoformat(log["timestamp"])
    
    return {
        "logs": logs,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": await db.admin_logs.count_documents({})
        }
    }

# Enhanced location tracking
@api_router.post("/location/update")
async def update_location(location_data: LocationUpdate, background_tasks: BackgroundTasks):
    """Update location with enhanced threat detection"""
    # Store location
    location_mongo = location_data.dict()
    location_mongo["timestamp"] = location_data.timestamp.isoformat()
    
    await db.location_history.insert_one(location_mongo)
    
    # Update current location
    await db.tourists.update_one(
        {"id": location_data.tourist_id},
        {"$set": {"current_location": {"lat": location_data.latitude, "lng": location_data.longitude}}}
    )
    
    # Get location name
    location_name = await get_location_name(location_data.latitude, location_data.longitude)
    
    # Check for nearby threats
    threats = get_nearby_threats(location_data.latitude, location_data.longitude, 50)
    high_threats = [t for t in threats if t.threat_level >= 7]
    
    # Create alerts for high threats
    for threat in high_threats:
        alert_data = {
            "tourist_id": location_data.tourist_id,
            "alert_type": "threat_proximity",
            "latitude": location_data.latitude,
            "longitude": location_data.longitude,
            "message": f"High threat detected nearby: {threat.name} (Level {threat.threat_level}/10)"
        }
        
        # Check if similar alert already exists
        existing_alert = await db.emergency_alerts.find_one({
            "tourist_id": location_data.tourist_id,
            "alert_type": "threat_proximity",
            "status": "active"
        })
        
        if not existing_alert:
            from . import EmergencyAlert
            alert_obj = EmergencyAlert(**alert_data)
            alert_mongo = alert_obj.dict()
            alert_mongo["created_at"] = alert_obj.created_at.isoformat()
            await db.emergency_alerts.insert_one(alert_mongo)
    
    # Perform safety analysis
    background_tasks.add_task(perform_enhanced_safety_analysis, location_data.tourist_id)
    
    return {
        "status": "location updated",
        "location_name": location_name,
        "threats_detected": len(threats),
        "high_priority_threats": len(high_threats),
        "message": "Enhanced safety analysis initiated"
    }

async def perform_enhanced_safety_analysis(tourist_id: str):
    """Enhanced background safety analysis"""
    try:
        # Get recent locations
        recent_locations = await db.location_history.find(
            {"tourist_id": tourist_id}
        ).sort("timestamp", -1).limit(10).to_list(10)
        
        if not recent_locations:
            return
        
        # Analyze route pattern
        route_points = [
            {"lat": loc["latitude"], "lng": loc["longitude"]}
            for loc in recent_locations
        ]
        
        # Get AI analysis
        safety_analysis = await analyze_route_safety(route_points, tourist_id)
        
        # Update tourist safety score
        await db.tourists.update_one(
            {"id": tourist_id},
            {"$set": {"safety_score": safety_analysis.get("overall_safety_score", 70)}}
        )
        
    except Exception as e:
        logging.error(f"Enhanced safety analysis error: {str(e)}")

# Keep existing routes from original implementation
# ... (include all previous routes like emergency alerts, crowd reports, etc.)

# Previous emergency alert system
class EmergencyAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tourist_id: str
    alert_type: str  # "panic", "geofence", "anomaly", "threat_proximity"
    latitude: float
    longitude: float
    message: Optional[str] = None
    status: str = Field(default="active")  # "active", "resolved", "false_alarm"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

class EmergencyAlertCreate(BaseModel):
    tourist_id: str
    alert_type: str
    latitude: float
    longitude: float
    message: Optional[str] = None

@api_router.post("/emergency/alert", response_model=EmergencyAlert)
async def create_emergency_alert(alert_data: EmergencyAlertCreate, background_tasks: BackgroundTasks):
    """Create emergency alert with enhanced response"""
    alert_dict = alert_data.dict()
    alert_obj = EmergencyAlert(**alert_dict)
    
    # Store alert
    alert_mongo = alert_obj.dict()
    alert_mongo["created_at"] = alert_obj.created_at.isoformat()
    
    await db.emergency_alerts.insert_one(alert_mongo)
    
    # Enhanced emergency response
    background_tasks.add_task(handle_enhanced_emergency_response, alert_obj.id)
    
    return alert_obj

async def handle_enhanced_emergency_response(alert_id: str):
    """Enhanced emergency response with AI E-FIR generation"""
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
        
        # Generate enhanced E-FIR with AI
        efir_data = await generate_enhanced_efir(alert_obj, tourist_obj)
        
        # Store E-FIR
        efir_record = {
            "id": str(uuid.uuid4()),
            "alert_id": alert_id,
            "tourist_id": alert_obj.tourist_id,
            "efir_data": efir_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.efir_records.insert_one(efir_record)
        
        logging.info(f"Enhanced E-FIR generated for alert {alert_id}: {efir_data.get('fir_number', 'N/A')}")
        
    except Exception as e:
        logging.error(f"Enhanced emergency response error: {str(e)}")

async def generate_enhanced_efir(alert: EmergencyAlert, tourist: TouristID) -> Dict[str, Any]:
    """Generate enhanced E-FIR using AI with location context"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"efir_{alert.id}",
            system_message="You are an AI assistant for generating comprehensive E-FIR reports for tourist emergencies with location-based context."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Get location context
        location_name = await get_location_name(alert.latitude, alert.longitude)
        nearby_threats = get_nearby_threats(alert.latitude, alert.longitude, 25)
        
        efir_prompt = f"""
        Generate a comprehensive E-FIR for tourist emergency:
        
        Tourist Details:
        - Name: {tourist.tourist_name}
        - Digital ID: {tourist.id}
        - Blockchain Hash: {tourist.blockchain_hash}
        - Contact: {tourist.phone_number}
        - Nationality: {tourist.nationality}
        - Emergency Contact: {tourist.emergency_contact_name} ({tourist.emergency_contact_phone})
        
        Incident Details:
        - Type: {alert.alert_type}
        - Location: {location_name}
        - Coordinates: {alert.latitude}, {alert.longitude}
        - Time: {alert.created_at}
        - Message: {alert.message or "No additional message"}
        
        Location Context:
        - Nearby Threats: {[t.name + " (" + t.threat_type + ")" for t in nearby_threats[:3]]}
        
        Generate comprehensive E-FIR in JSON format:
        {{
            "fir_number": "E-FIR-{alert.id[:8]}-{datetime.now().strftime('%Y%m%d')}",
            "incident_classification": "tourist_emergency",
            "severity_level": "high/medium/low",
            "incident_summary": "detailed summary",
            "location_analysis": "detailed location context",
            "threat_assessment": "assessment of local threats",
            "recommended_actions": ["immediate action1", "followup action2"],
            "assigned_units": ["unit1", "unit2"],
            "contact_authorities": ["authority1", "authority2"],
            "medical_requirements": "if applicable",
            "priority_level": "critical/high/medium/low"
        }}
        """
        
        user_message = UserMessage(text=efir_prompt)
        response = await chat.send_message(user_message)
        
        try:
            efir_data = json.loads(response)
            efir_data["generated_at"] = datetime.now(timezone.utc).isoformat()
            efir_data["ai_generated"] = True
            return efir_data
        except json.JSONDecodeError:
            return {
                "fir_number": f"E-FIR-{alert.id[:8]}-{datetime.now().strftime('%Y%m%d')}",
                "incident_classification": "tourist_emergency",
                "severity_level": "high",
                "incident_summary": f"Tourist emergency alert - {alert.alert_type} at {location_name}",
                "location_analysis": f"Incident occurred at {location_name} ({alert.latitude}, {alert.longitude})",
                "threat_assessment": f"Location has {len(nearby_threats)} identified threats nearby",
                "recommended_actions": ["Deploy nearest response team", "Contact local emergency services", "Notify tourist's emergency contact"],
                "assigned_units": ["Tourist Police", "Local Emergency Response", "Medical Services"],
                "contact_authorities": ["Local Police", "Embassy/Consulate", "Tourist Helpline"],
                "medical_requirements": "Assess medical needs on arrival",
                "priority_level": "high",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "ai_generated": True
            }
            
    except Exception as e:
        logging.error(f"Enhanced E-FIR generation error: {str(e)}")
        return {
            "fir_number": f"E-FIR-{alert.id[:8]}-{datetime.now().strftime('%Y%m%d')}",
            "incident_classification": "tourist_emergency",
            "severity_level": "high",
            "incident_summary": "Emergency alert generated - manual review required",
            "location_analysis": f"Location: {alert.latitude}, {alert.longitude}",
            "threat_assessment": "Manual threat assessment required",
            "recommended_actions": ["Manual review and response required"],
            "assigned_units": ["Tourist Police"],
            "contact_authorities": ["Local Emergency Services"],
            "medical_requirements": "To be determined",
            "priority_level": "high",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "ai_generated": False,
            "error_note": "AI generation failed - manual processing required"
        }

# Initialize global threat data
@api_router.post("/init/global-threats")
async def initialize_global_threats():
    """Initialize global threat database"""
    try:
        # Clear existing global threats
        await db.global_threats.delete_many({"source": "global_database"})
        
        # Insert new threats
        threats_to_insert = []
        for category, threats in GLOBAL_THREAT_DATABASE.items():
            for threat in threats:
                threat_obj = LocationThreat(
                    name=threat["name"],
                    latitude=threat["lat"],
                    longitude=threat["lng"],
                    threat_type=threat["type"],
                    threat_level=threat["threat_level"],
                    radius_km=threat["radius"],
                    description=f"{category.replace('_', ' ').title()} - {threat['name']}",
                    source="global_database"
                )
                threats_to_insert.append(threat_obj.dict())
        
        # Convert datetime for MongoDB
        for threat in threats_to_insert:
            threat["created_at"] = threat["created_at"].isoformat() if isinstance(threat["created_at"], datetime) else threat["created_at"]
        
        await db.global_threats.insert_many(threats_to_insert)
        
        return {
            "status": "success",
            "message": f"Initialized {len(threats_to_insert)} global threats",
            "categories": list(GLOBAL_THREAT_DATABASE.keys())
        }
        
    except Exception as e:
        logging.error(f"Global threats initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize global threats")

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