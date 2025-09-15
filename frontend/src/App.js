import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Component for Tourist Registration
const TouristRegistration = ({ onRegistrationSuccess }) => {
  const [formData, setFormData] = useState({
    tourist_name: '',
    passport_number: '',
    aadhaar_number: '',
    phone_number: '',
    email: '',
    nationality: 'Indian',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    trip_start_date: '',
    trip_end_date: '',
    planned_destinations: []
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleDestinationChange = (e) => {
    const destinations = e.target.value.split(',').map(dest => dest.trim());
    setFormData(prev => ({
      ...prev,
      planned_destinations: destinations
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/tourist-id/register`, {
        ...formData,
        trip_start_date: new Date(formData.trip_start_date).toISOString(),
        trip_end_date: new Date(formData.trip_end_date).toISOString()
      });
      
      onRegistrationSuccess(response.data);
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Registration failed. Please try again.');
    }
  };

  return (
    <div className="registration-form bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Tourist Registration</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            name="tourist_name"
            placeholder="Full Name"
            value={formData.tourist_name}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="text"
            name="phone_number"
            placeholder="Phone Number"
            value={formData.phone_number}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="email"
            name="email"
            placeholder="Email Address"
            value={formData.email}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <select
            name="nationality"
            value={formData.nationality}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Indian">Indian</option>
            <option value="Foreign">Foreign</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            name="passport_number"
            placeholder="Passport Number (if applicable)"
            value={formData.passport_number}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="aadhaar_number"
            placeholder="Aadhaar Number (if applicable)"
            value={formData.aadhaar_number}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            name="emergency_contact_name"
            placeholder="Emergency Contact Name"
            value={formData.emergency_contact_name}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="text"
            name="emergency_contact_phone"
            placeholder="Emergency Contact Phone"
            value={formData.emergency_contact_phone}
            onChange={handleInputChange}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Trip Start Date</label>
            <input
              type="date"
              name="trip_start_date"
              value={formData.trip_start_date}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Trip End Date</label>
            <input
              type="date"
              name="trip_end_date"
              value={formData.trip_end_date}
              onChange={handleInputChange}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Planned Destinations (comma-separated)</label>
          <input
            type="text"
            placeholder="e.g., Guwahati, Shillong, Tawang"
            value={formData.planned_destinations.join(', ')}
            onChange={handleDestinationChange}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-200 font-semibold"
        >
          Register & Generate Digital ID
        </button>
      </form>
    </div>
  );
};

// Component for Interactive Risk Map
const InteractiveRiskMap = ({ riskZones }) => {
  const [selectedLayers, setSelectedLayers] = useState({
    flood: true,
    cyclone: true,
    seismic: true,
    crime: true,
    restricted: true
  });

  const toggleLayer = (layer) => {
    setSelectedLayers(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  const layerColors = {
    flood: 'bg-blue-500',
    cyclone: 'bg-green-500',
    seismic: 'bg-orange-500',
    crime: 'bg-red-500',
    restricted: 'bg-purple-500'
  };

  const filteredZones = riskZones.filter(zone => selectedLayers[zone.risk_type]);

  return (
    <div className="risk-map bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Interactive Risk Map</h3>
      
      {/* Layer Controls */}
      <div className="flex flex-wrap gap-2 mb-6">
        {Object.keys(selectedLayers).map(layer => (
          <button
            key={layer}
            onClick={() => toggleLayer(layer)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition duration-200 ${
              selectedLayers[layer]
                ? `${layerColors[layer]} text-white`
                : 'bg-gray-200 text-gray-600'
            }`}
          >
            {layer.charAt(0).toUpperCase() + layer.slice(1)} Risk
          </button>
        ))}
      </div>

      {/* Map Placeholder with Risk Zones */}
      <div className="map-container bg-gray-100 rounded-lg p-4 h-96 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-green-100 to-blue-100 rounded-lg">
          {/* Northeast India Map Representation */}
          <div className="absolute top-1/4 left-1/3 w-32 h-24 bg-green-200 rounded-lg opacity-70">
            <span className="text-xs text-green-800 p-1">Assam</span>
          </div>
          <div className="absolute top-1/6 left-1/2 w-20 h-16 bg-green-300 rounded opacity-70">
            <span className="text-xs text-green-800 p-1">Meghalaya</span>
          </div>
          <div className="absolute top-1/8 left-3/5 w-16 h-20 bg-green-400 rounded opacity-70">
            <span className="text-xs text-green-800 p-1">Arunachal</span>
          </div>
          
          {/* Risk Zone Overlays */}
          {filteredZones.map((zone, index) => (
            <div
              key={zone.id}
              className={`absolute w-12 h-12 rounded-full opacity-60 ${layerColors[zone.risk_type]} animate-pulse`}
              style={{
                top: `${30 + (index * 10)}%`,
                left: `${40 + (index * 15)}%`
              }}
              title={`${zone.name} - Risk Level: ${zone.risk_level}/10`}
            >
              <span className="text-xs text-white p-1">{zone.risk_level}</span>
            </div>
          ))}
        </div>
        
        <div className="absolute bottom-4 left-4 bg-white p-2 rounded shadow">
          <p className="text-xs text-gray-600">Click zones for details</p>
        </div>
      </div>

      {/* Risk Zone List */}
      <div className="mt-4">
        <h4 className="font-semibold text-gray-800 mb-2">Active Risk Zones</h4>
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {filteredZones.map(zone => (
            <div key={zone.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full ${layerColors[zone.risk_type]} mr-2`}></div>
                <span className="text-sm font-medium">{zone.name}</span>
              </div>
              <span className="text-xs text-gray-500">Risk: {zone.risk_level}/10</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Component for Safety Score Calculator
const SafetyScoreCalculator = ({ touristId, safetyAnalysis }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score) => {
    if (score >= 80) return 'bg-green-100 border-green-300';
    if (score >= 60) return 'bg-yellow-100 border-yellow-300';
    return 'bg-red-100 border-red-300';
  };

  return (
    <div className="safety-score bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Safety Score</h3>
      
      {/* Score Display */}
      <div className={`score-display ${getScoreBackground(safetyAnalysis.current_safety_score)} border-2 rounded-lg p-4 mb-4`}>
        <div className="text-center">
          <div className={`text-4xl font-bold ${getScoreColor(safetyAnalysis.current_safety_score)}`}>
            {safetyAnalysis.current_safety_score}
          </div>
          <div className="text-sm text-gray-600">out of 100</div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="score-breakdown space-y-3">
        <h4 className="font-semibold text-gray-800">Risk Factors</h4>
        {safetyAnalysis.risk_factors.length > 0 ? (
          safetyAnalysis.risk_factors.map((factor, index) => (
            <div key={index} className="flex items-center text-sm">
              <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
              {factor}
            </div>
          ))
        ) : (
          <p className="text-sm text-green-600">No significant risk factors detected</p>
        )}

        <h4 className="font-semibold text-gray-800 mt-4">Recommendations</h4>
        {safetyAnalysis.recommendations.map((rec, index) => (
          <div key={index} className="flex items-center text-sm">
            <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
            {rec}
          </div>
        ))}

        {safetyAnalysis.anomalies_detected.length > 0 && (
          <>
            <h4 className="font-semibold text-gray-800 mt-4">Anomalies Detected</h4>
            {safetyAnalysis.anomalies_detected.map((anomaly, index) => (
              <div key={index} className="flex items-center text-sm text-orange-600">
                <div className="w-2 h-2 bg-orange-400 rounded-full mr-2"></div>
                {anomaly}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};

// Component for SOS & Emergency Services
const SOSEmergencyServices = ({ touristId, currentLocation }) => {
  const [sosActive, setSosActive] = useState(false);

  const triggerSOS = async () => {
    if (!currentLocation) {
      alert('Location access required for SOS');
      return;
    }

    setSosActive(true);
    try {
      await axios.post(`${API}/emergency/alert`, {
        tourist_id: touristId,
        alert_type: 'panic',
        latitude: currentLocation.lat,
        longitude: currentLocation.lng,
        message: 'Emergency SOS triggered by user'
      });
      
      alert('SOS Alert Sent! Emergency services notified.');
    } catch (error) {
      console.error('SOS failed:', error);
      alert('SOS failed. Please call emergency numbers directly.');
    } finally {
      setTimeout(() => setSosActive(false), 3000);
    }
  };

  const emergencyContacts = [
    { name: 'Police', number: '100', icon: '🚔' },
    { name: 'Medical Emergency', number: '108', icon: '🚑' },
    { name: 'Fire Service', number: '101', icon: '🚒' },
    { name: 'Tourist Helpline', number: '1363', icon: '🏔️' }
  ];

  return (
    <div className="sos-emergency bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Emergency Services</h3>
      
      {/* SOS Button */}
      <button
        onClick={triggerSOS}
        disabled={sosActive}
        className={`w-full py-4 px-6 rounded-lg font-bold text-white text-lg transition duration-200 ${
          sosActive
            ? 'bg-red-800 animate-pulse cursor-not-allowed'
            : 'bg-red-600 hover:bg-red-700 active:bg-red-800'
        }`}
      >
        {sosActive ? '🚨 SOS ACTIVE - HELP COMING' : '🆘 EMERGENCY SOS'}
      </button>

      {/* Emergency Contacts */}
      <div className="mt-6">
        <h4 className="font-semibold text-gray-800 mb-3">Emergency Contacts</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {emergencyContacts.map((contact, index) => (
            <a
              key={index}
              href={`tel:${contact.number}`}
              className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition duration-200"
            >
              <span className="text-2xl mr-3">{contact.icon}</span>
              <div>
                <div className="font-medium text-gray-800">{contact.name}</div>
                <div className="text-blue-600 font-bold">{contact.number}</div>
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Nearby Help */}
      <div className="mt-6">
        <h4 className="font-semibold text-gray-800 mb-3">Nearby Help</h4>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
            <span className="text-sm">🏥 Civil Hospital Guwahati</span>
            <span className="text-xs text-blue-600">2.3 km</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
            <span className="text-sm">🚔 Panbazar Police Station</span>
            <span className="text-xs text-blue-600">1.1 km</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-blue-50 rounded">
            <span className="text-sm">🏔️ Tourist Information Center</span>
            <span className="text-xs text-blue-600">0.8 km</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Component for Travel Advisories
const TravelAdvisories = ({ advisories }) => {
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'high': return 'border-orange-500 bg-orange-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      default: return 'border-blue-500 bg-blue-50';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      default: return 'ℹ️';
    }
  };

  return (
    <div className="advisories bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Travel Advisories</h3>
      
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {advisories.map(advisory => (
          <div key={advisory.id} className={`border-l-4 p-4 rounded-r-lg ${getSeverityColor(advisory.severity)}`}>
            <div className="flex items-start">
              <span className="text-2xl mr-3">{getSeverityIcon(advisory.severity)}</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-800">{advisory.title}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    advisory.advisory_type === 'official' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {advisory.advisory_type}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{advisory.content}</p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Areas: {advisory.affected_areas.join(', ')}</span>
                  <span>{new Date(advisory.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Component for Crowd Reporting
const CrowdReporting = ({ touristId, currentLocation }) => {
  const [reportForm, setReportForm] = useState({
    report_type: 'safety_issue',
    description: '',
    photo_url: ''
  });

  const handleReportSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentLocation) {
      alert('Location access required for reporting');
      return;
    }

    try {
      await axios.post(`${API}/crowd-reports`, {
        reporter_id: touristId,
        latitude: currentLocation.lat,
        longitude: currentLocation.lng,
        ...reportForm
      });
      
      alert('Report submitted successfully! It will be reviewed by administrators.');
      setReportForm({
        report_type: 'safety_issue',
        description: '',
        photo_url: ''
      });
    } catch (error) {
      console.error('Report submission failed:', error);
      alert('Failed to submit report. Please try again.');
    }
  };

  return (
    <div className="crowd-reporting bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Report Safety Issues</h3>
      
      <form onSubmit={handleReportSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Report Type</label>
          <select
            value={reportForm.report_type}
            onChange={(e) => setReportForm(prev => ({ ...prev, report_type: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="safety_issue">Safety Issue</option>
            <option value="road_block">Road Block</option>
            <option value="weather">Weather Alert</option>
            <option value="crime">Crime Incident</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            rows={4}
            value={reportForm.description}
            onChange={(e) => setReportForm(prev => ({ ...prev, description: e.target.value }))}
            placeholder="Describe the issue in detail..."
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Photo URL (optional)</label>
          <input
            type="url"
            value={reportForm.photo_url}
            onChange={(e) => setReportForm(prev => ({ ...prev, photo_url: e.target.value }))}
            placeholder="https://example.com/photo.jpg"
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 transition duration-200 font-semibold"
        >
          Submit Report
        </button>
      </form>
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('home');
  const [tourist, setTourist] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [riskZones, setRiskZones] = useState([]);
  const [advisories, setAdvisories] = useState([]);
  const [safetyAnalysis, setSafetyAnalysis] = useState({
    current_safety_score: 85,
    risk_factors: [],
    recommendations: ['Stay in well-lit areas', 'Keep emergency contacts handy'],
    anomalies_detected: []
  });

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (error) => {
          console.error('Location access denied:', error);
          // Fallback to Guwahati coordinates
          setCurrentLocation({ lat: 26.1445, lng: 91.7362 });
        }
      );
    }
  }, []);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Initialize sample data
        await axios.post(`${API}/init/sample-data`);
        
        // Load risk zones
        const riskResponse = await axios.get(`${API}/risk-zones`);
        setRiskZones(riskResponse.data);

        // Load advisories
        const advisoriesResponse = await axios.get(`${API}/advisories`);
        setAdvisories(advisoriesResponse.data);
      } catch (error) {
        console.error('Failed to load initial data:', error);
      }
    };

    loadInitialData();
  }, []);

  // Update location and get safety analysis
  useEffect(() => {
    if (tourist && currentLocation) {
      const updateLocationAndAnalysis = async () => {
        try {
          // Update location
          await axios.post(`${API}/location/update`, {
            tourist_id: tourist.id,
            latitude: currentLocation.lat,
            longitude: currentLocation.lng,
            location_name: 'Current Location'
          });

          // Get safety analysis
          const analysisResponse = await axios.get(`${API}/safety/analysis/${tourist.id}`);
          setSafetyAnalysis(analysisResponse.data);
        } catch (error) {
          console.error('Failed to update location or get analysis:', error);
        }
      };

      updateLocationAndAnalysis();
    }
  }, [tourist, currentLocation]);

  const handleRegistrationSuccess = (touristData) => {
    setTourist(touristData);
    setCurrentView('dashboard');
  };

  const renderView = () => {
    switch (currentView) {
      case 'register':
        return <TouristRegistration onRegistrationSuccess={handleRegistrationSuccess} />;
      
      case 'dashboard':
        return (
          <div className="dashboard-grid grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            <div className="col-span-1 lg:col-span-2">
              <InteractiveRiskMap riskZones={riskZones} />
            </div>
            <div>
              <SafetyScoreCalculator touristId={tourist?.id} safetyAnalysis={safetyAnalysis} />
            </div>
            <div>
              <SOSEmergencyServices touristId={tourist?.id} currentLocation={currentLocation} />
            </div>
            <div>
              <TravelAdvisories advisories={advisories} />
            </div>
            <div>
              <CrowdReporting touristId={tourist?.id} currentLocation={currentLocation} />
            </div>
          </div>
        );
      
      default:
        return (
          <div className="home-view text-center">
            <div className="hero-section mb-12">
              <div className="hero-image-container mb-8">
                <img
                  src="https://images.unsplash.com/photo-1697800937428-6aea55069bf9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxub3J0aGVhc3QlMjBpbmRpYSUyMG1vdW50YWluc3xlbnwwfHx8Ymx1ZXwxNzU3OTM1NTI5fDA&ixlib=rb-4.1.0&q=85"
                  alt="Northeast India Mountains"
                  className="w-full h-64 object-cover rounded-lg shadow-lg"
                />
              </div>
              <div className="hero-content bg-white bg-opacity-90 rounded-lg p-8 shadow-lg">
                <h1 className="text-4xl font-bold text-gray-800 mb-4">
                  Northeast India Tourist Safety Platform
                </h1>
                <p className="text-lg text-gray-600 mb-8">
                  Smart, AI-powered safety monitoring and emergency response system for tourists visiting Northeast India
                </p>
                
                <div className="features-grid grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="feature-card bg-blue-50 p-4 rounded-lg">
                    <div className="text-3xl mb-2">🛡️</div>
                    <h3 className="font-semibold text-gray-800">Digital Tourist ID</h3>
                    <p className="text-sm text-gray-600">Secure blockchain-based identity system</p>
                  </div>
                  
                  <div className="feature-card bg-green-50 p-4 rounded-lg">
                    <div className="text-3xl mb-2">🗺️</div>
                    <h3 className="font-semibold text-gray-800">Interactive Risk Maps</h3>
                    <p className="text-sm text-gray-600">Real-time risk zone monitoring and alerts</p>
                  </div>
                  
                  <div className="feature-card bg-red-50 p-4 rounded-lg">
                    <div className="text-3xl mb-2">🆘</div>
                    <h3 className="font-semibold text-gray-800">Emergency SOS</h3>
                    <p className="text-sm text-gray-600">One-tap emergency alert system</p>
                  </div>
                </div>

                {!tourist ? (
                  <div className="cta-buttons space-x-4">
                    <button
                      onClick={() => setCurrentView('register')}
                      className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition duration-200 font-semibold"
                    >
                      Register as Tourist
                    </button>
                    <button
                      onClick={() => setCurrentView('dashboard')}
                      className="bg-gray-600 text-white px-8 py-3 rounded-lg hover:bg-gray-700 transition duration-200 font-semibold"
                    >
                      View Demo Dashboard
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setCurrentView('dashboard')}
                    className="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition duration-200 font-semibold"
                  >
                    Go to Dashboard
                  </button>
                )}
              </div>
            </div>

            {/* Additional Images */}
            <div className="additional-images grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <img
                src="https://images.unsplash.com/photo-1590992674423-eb622d3cd1da?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwyfHxub3J0aGVhc3QlMjBpbmRpYSUyMG1vdW50YWluc3xlbnwwfHx8Ymx1ZXwxNzU3OTM1NTI5fDA&ixlib=rb-4.1.0&q=85"
                alt="Himalayan Peaks"
                className="w-full h-48 object-cover rounded-lg shadow-md"
              />
              <img
                src="https://images.unsplash.com/photo-1632096932162-ab434f5fd026?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwyfHx0b3VyaXNtJTIwc2FmZXR5fGVufDB8fHxibHVlfDE3NTc5MzU1MzZ8MA&ixlib=rb-4.1.0&q=85"
                alt="Mountain Safety Warning"
                className="w-full h-48 object-cover rounded-lg shadow-md"
              />
              <img
                src="https://images.unsplash.com/photo-1577953489345-35dcf2a8bc23?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwzfHxub3J0aGVhc3QlMjBpbmRpYSUyMG1vdW50YWluc3xlbnwwfHx8Ymx1ZXwxNzU3OTM1NTI5fDA&ixlib=rb-4.1.0&q=85"
                alt="Aerial Mountain View"
                className="w-full h-48 object-cover rounded-lg shadow-md"
              />
            </div>
          </div>
        );
    }
  };

  return (
    <div className="App min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Navigation */}
      <nav className="nav-bar bg-white shadow-lg p-4">
        <div className="container mx-auto flex items-center justify-between">
          <div className="logo flex items-center space-x-2">
            <span className="text-2xl">🏔️</span>
            <span className="text-xl font-bold text-gray-800">NE Tourism Safety</span>
          </div>
          
          <div className="nav-links flex space-x-4">
            <button
              onClick={() => setCurrentView('home')}
              className={`px-4 py-2 rounded transition duration-200 ${
                currentView === 'home' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Home
            </button>
            
            {tourist && (
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-4 py-2 rounded transition duration-200 ${
                  currentView === 'dashboard' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
            )}
            
            <button
              onClick={() => setCurrentView('register')}
              className={`px-4 py-2 rounded transition duration-200 ${
                currentView === 'register' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Register
            </button>
          </div>

          {tourist && (
            <div className="user-info flex items-center space-x-2">
              <div className="text-sm text-gray-600">
                Welcome, {tourist.tourist_name}
              </div>
              <div className={`safety-score px-2 py-1 rounded text-xs font-medium ${
                safetyAnalysis.current_safety_score >= 80 
                  ? 'bg-green-100 text-green-800' 
                  : safetyAnalysis.current_safety_score >= 60
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                Safety: {safetyAnalysis.current_safety_score}/100
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content container mx-auto px-4 py-8">
        {renderView()}
      </main>

      {/* Footer */}
      <footer className="footer bg-gray-800 text-white p-6 mt-12">
        <div className="container mx-auto text-center">
          <p className="mb-2">Northeast India Tourist Safety Platform</p>
          <p className="text-sm text-gray-400">
            Powered by AI & Blockchain Technology | Emergency: 100 | Tourist Helpline: 1363
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;