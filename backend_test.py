#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Tourist Safety App
Tests all high and medium priority APIs with realistic data
"""

import requests
import json
import uuid
from datetime import datetime, timezone, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://travelsentry-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE_URL}")

class TouristSafetyAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = {}
        self.tourist_id = None
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'response_data': response_data
        }
        
    def test_sample_data_initialization(self):
        """Test POST /api/init/sample-data"""
        print("\n=== Testing Sample Data Initialization ===")
        
        try:
            response = self.session.post(f"{API_BASE_URL}/init/sample-data")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_test("Sample Data Init", True, "Sample data initialized successfully", data)
                else:
                    self.log_test("Sample Data Init", False, f"Unexpected response: {data}")
            else:
                self.log_test("Sample Data Init", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Sample Data Init", False, f"Exception: {str(e)}")
    
    def test_tourist_registration(self):
        """Test POST /api/tourist-id/register - HIGH PRIORITY"""
        print("\n=== Testing Tourist Registration & Digital ID Generation ===")
        
        # Realistic test data as requested
        tourist_data = {
            "tourist_name": "John Doe",
            "passport_number": "A12345678",
            "aadhaar_number": "123456789012",
            "phone_number": "+91-9876543210",
            "email": "john.doe@email.com",
            "nationality": "Indian",
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "+91-9876543211",
            "trip_start_date": datetime.now(timezone.utc).isoformat(),
            "trip_end_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "planned_destinations": ["Guwahati", "Shillong", "Tawang"]
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/tourist-id/register", json=tourist_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'blockchain_hash' in data:
                    self.tourist_id = data['id']  # Store for other tests
                    self.log_test("Tourist Registration", True, f"Tourist registered with ID: {self.tourist_id}", data)
                else:
                    self.log_test("Tourist Registration", False, f"Missing required fields in response: {data}")
            else:
                self.log_test("Tourist Registration", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Tourist Registration", False, f"Exception: {str(e)}")
    
    def test_get_tourist(self):
        """Test GET /api/tourist-id/{tourist_id}"""
        print("\n=== Testing Get Tourist Information ===")
        
        if not self.tourist_id:
            self.log_test("Get Tourist Info", False, "No tourist ID available from registration test")
            return
            
        try:
            response = self.session.get(f"{API_BASE_URL}/tourist-id/{self.tourist_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('id') == self.tourist_id:
                    self.log_test("Get Tourist Info", True, "Tourist information retrieved successfully", data)
                else:
                    self.log_test("Get Tourist Info", False, f"Tourist ID mismatch: {data}")
            else:
                self.log_test("Get Tourist Info", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Tourist Info", False, f"Exception: {str(e)}")
    
    def test_location_update(self):
        """Test POST /api/location/update - HIGH PRIORITY"""
        print("\n=== Testing Location Tracking ===")
        
        if not self.tourist_id:
            self.log_test("Location Update", False, "No tourist ID available")
            return
            
        # Guwahati coordinates as requested
        location_data = {
            "tourist_id": self.tourist_id,
            "latitude": 26.1445,
            "longitude": 91.7362,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location_name": "Guwahati, Assam"
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/location/update", json=location_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'location updated':
                    self.log_test("Location Update", True, "Location updated and safety analysis initiated", data)
                else:
                    self.log_test("Location Update", False, f"Unexpected response: {data}")
            else:
                self.log_test("Location Update", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Location Update", False, f"Exception: {str(e)}")
    
    def test_safety_analysis(self):
        """Test GET /api/safety/analysis/{tourist_id} - HIGH PRIORITY (Gemini AI)"""
        print("\n=== Testing Google Gemini AI Safety Analysis ===")
        
        if not self.tourist_id:
            self.log_test("AI Safety Analysis", False, "No tourist ID available")
            return
            
        # Wait a moment for location data to be processed
        time.sleep(2)
        
        try:
            response = self.session.get(f"{API_BASE_URL}/safety/analysis/{self.tourist_id}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['tourist_id', 'current_safety_score', 'risk_factors', 'recommendations']
                
                if all(field in data for field in required_fields):
                    self.log_test("AI Safety Analysis", True, f"AI analysis completed - Safety Score: {data.get('current_safety_score')}", data)
                else:
                    self.log_test("AI Safety Analysis", False, f"Missing required fields in AI response: {data}")
            else:
                self.log_test("AI Safety Analysis", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("AI Safety Analysis", False, f"Exception: {str(e)}")
    
    def test_emergency_alert(self):
        """Test POST /api/emergency/alert - HIGH PRIORITY (E-FIR Generation)"""
        print("\n=== Testing Emergency Alert System with E-FIR ===")
        
        if not self.tourist_id:
            self.log_test("Emergency Alert", False, "No tourist ID available")
            return
            
        # Emergency at Guwahati coordinates as requested
        alert_data = {
            "tourist_id": self.tourist_id,
            "alert_type": "panic",
            "latitude": 26.1445,
            "longitude": 91.7362,
            "message": "Emergency situation - need immediate help"
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/emergency/alert", json=alert_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and data.get('status') == 'active':
                    self.log_test("Emergency Alert", True, f"Emergency alert created with ID: {data['id']}", data)
                    
                    # Wait for E-FIR generation (background task)
                    time.sleep(3)
                    print("   ⏳ Waiting for E-FIR generation...")
                    
                else:
                    self.log_test("Emergency Alert", False, f"Invalid alert response: {data}")
            else:
                self.log_test("Emergency Alert", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Emergency Alert", False, f"Exception: {str(e)}")
    
    def test_risk_zones(self):
        """Test GET /api/risk-zones - HIGH PRIORITY"""
        print("\n=== Testing Risk Zones ===")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/risk-zones")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    risk_types = set(zone.get('risk_type') for zone in data)
                    self.log_test("Risk Zones", True, f"Retrieved {len(data)} risk zones with types: {risk_types}", data[:2])  # Show first 2
                else:
                    self.log_test("Risk Zones", False, f"No risk zones found or invalid format: {data}")
            else:
                self.log_test("Risk Zones", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Risk Zones", False, f"Exception: {str(e)}")
    
    def test_advisories(self):
        """Test GET /api/advisories - MEDIUM PRIORITY"""
        print("\n=== Testing Travel Advisories ===")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/advisories")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    active_advisories = [adv for adv in data if adv.get('is_active')]
                    self.log_test("Travel Advisories", True, f"Retrieved {len(active_advisories)} active advisories", data[:2])
                else:
                    self.log_test("Travel Advisories", False, f"Invalid advisories format: {data}")
            else:
                self.log_test("Travel Advisories", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Travel Advisories", False, f"Exception: {str(e)}")
    
    def test_crowd_reports(self):
        """Test POST and GET /api/crowd-reports - MEDIUM PRIORITY"""
        print("\n=== Testing Crowd Reporting System ===")
        
        # Test POST - Submit crowd report
        report_data = {
            "reporter_id": self.tourist_id,
            "latitude": 26.1445,
            "longitude": 91.7362,
            "report_type": "safety_issue",
            "description": "Suspicious activity reported near tourist area",
            "verification_status": "pending"
        }
        
        try:
            # Submit report
            response = self.session.post(f"{API_BASE_URL}/crowd-reports", json=report_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    self.log_test("Submit Crowd Report", True, f"Crowd report submitted with ID: {data['id']}", data)
                else:
                    self.log_test("Submit Crowd Report", False, f"Invalid report response: {data}")
            else:
                self.log_test("Submit Crowd Report", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test GET - Retrieve crowd reports
            response = self.session.get(f"{API_BASE_URL}/crowd-reports")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Crowd Reports", True, f"Retrieved {len(data)} crowd reports", data[:1])
                else:
                    self.log_test("Get Crowd Reports", False, f"Invalid reports format: {data}")
            else:
                self.log_test("Get Crowd Reports", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Crowd Reports", False, f"Exception: {str(e)}")
    
    def test_dashboard_stats(self):
        """Test GET /api/dashboard/stats - MEDIUM PRIORITY"""
        print("\n=== Testing Dashboard Stats ===")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/dashboard/stats")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_active_tourists', 'active_emergency_alerts', 'total_crowd_reports']
                
                if all(field in data for field in required_fields):
                    self.log_test("Dashboard Stats", True, f"Dashboard stats retrieved successfully", data)
                else:
                    self.log_test("Dashboard Stats", False, f"Missing required stats fields: {data}")
            else:
                self.log_test("Dashboard Stats", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Exception: {str(e)}")
    
    def test_northeast_locations(self):
        """Test GET /api/northeast/locations - MEDIUM PRIORITY"""
        print("\n=== Testing Northeast Location Data ===")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/northeast/locations")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    states = list(data.keys())
                    self.log_test("Northeast Locations", True, f"Retrieved data for {len(states)} states: {states}", list(data.keys()))
                else:
                    self.log_test("Northeast Locations", False, f"Invalid location data format: {data}")
            else:
                self.log_test("Northeast Locations", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Northeast Locations", False, f"Exception: {str(e)}")
    
    def test_location_history(self):
        """Test GET /api/location/history/{tourist_id}"""
        print("\n=== Testing Location History ===")
        
        if not self.tourist_id:
            self.log_test("Location History", False, "No tourist ID available")
            return
            
        try:
            response = self.session.get(f"{API_BASE_URL}/location/history/{self.tourist_id}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Location History", True, f"Retrieved {len(data)} location records", data[:1])
                else:
                    self.log_test("Location History", False, f"Invalid location history format: {data}")
            else:
                self.log_test("Location History", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Location History", False, f"Exception: {str(e)}")
    
    def test_emergency_alerts_list(self):
        """Test GET /api/emergency/alerts"""
        print("\n=== Testing Emergency Alerts List ===")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/emergency/alerts")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    active_alerts = [alert for alert in data if alert.get('status') == 'active']
                    self.log_test("Emergency Alerts List", True, f"Retrieved {len(data)} alerts, {len(active_alerts)} active", data[:1])
                else:
                    self.log_test("Emergency Alerts List", False, f"Invalid alerts format: {data}")
            else:
                self.log_test("Emergency Alerts List", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Emergency Alerts List", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests in priority order"""
        print("🚀 Starting Comprehensive Tourist Safety App Backend Testing")
        print(f"Backend URL: {API_BASE_URL}")
        print("=" * 80)
        
        # HIGH PRIORITY TESTS FIRST
        print("\n🔥 HIGH PRIORITY API TESTS")
        self.test_sample_data_initialization()  # Initialize data first
        self.test_tourist_registration()        # Digital ID Generation
        self.test_get_tourist()                # Verify registration
        self.test_location_update()            # Location Tracking
        self.test_safety_analysis()            # Gemini AI Analysis
        self.test_emergency_alert()            # Emergency + E-FIR
        self.test_risk_zones()                 # Risk Zones
        
        # MEDIUM PRIORITY TESTS
        print("\n📊 MEDIUM PRIORITY API TESTS")
        self.test_advisories()                 # Travel Advisories
        self.test_crowd_reports()              # Crowd Reporting
        self.test_dashboard_stats()            # Dashboard Stats
        self.test_northeast_locations()        # Northeast Data
        
        # ADDITIONAL TESTS
        print("\n🔍 ADDITIONAL API TESTS")
        self.test_location_history()           # Location History
        self.test_emergency_alerts_list()      # Emergency Alerts List
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results.values() if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📊 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}: {result['message']}")
        
        # Critical Issues
        failed_tests = [name for name, result in self.test_results.items() if not result['success']]
        if failed_tests:
            print(f"\n🚨 FAILED TESTS REQUIRING ATTENTION:")
            for test in failed_tests:
                print(f"   - {test}: {self.test_results[test]['message']}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = TouristSafetyAPITester()
    tester.run_all_tests()