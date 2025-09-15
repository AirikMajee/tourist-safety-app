import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Enhanced Tourist Registration Component
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
  const [isLoading, setIsLoading] = useState(false);

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
    setIsLoading(true);
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
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="registration-form bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-2xl p-8 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-2xl">🛡️</span>
        </div>
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Digital Tourist ID Registration</h2>
        <p className="text-gray-600">Secure blockchain-based identity for safe travel</p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name *</label>
            <input
              type="text"
              name="tourist_name"
              placeholder="Enter your full name"
              value={formData.tourist_name}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              required
            />
          </div>
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Phone Number *</label>
            <input
              type="text"
              name="phone_number"
              placeholder="+91-XXXXXXXXXX"
              value={formData.phone_number}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              required
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Email Address *</label>
            <input
              type="email"
              name="email"
              placeholder="your.email@example.com"
              value={formData.email}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              required
            />
          </div>
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Nationality</label>
            <select
              name="nationality"
              value={formData.nationality}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
            >
              <option value="Indian">Indian</option>
              <option value="Foreign">Foreign</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Passport Number</label>
            <input
              type="text"
              name="passport_number"
              placeholder="A1234567"
              value={formData.passport_number}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
            />
          </div>
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Aadhaar Number</label>
            <input
              type="text"
              name="aadhaar_number"
              placeholder="XXXX XXXX XXXX"
              value={formData.aadhaar_number}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
            />
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Emergency Contact</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="form-group">
              <label className="block text-sm font-semibold text-gray-700 mb-2">Contact Name *</label>
              <input
                type="text"
                name="emergency_contact_name"
                placeholder="Emergency contact person"
                value={formData.emergency_contact_name}
                onChange={handleInputChange}
                className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                required
              />
            </div>
            <div className="form-group">
              <label className="block text-sm font-semibold text-gray-700 mb-2">Contact Phone *</label>
              <input
                type="text"
                name="emergency_contact_phone"
                placeholder="+91-XXXXXXXXXX"
                value={formData.emergency_contact_phone}
                onChange={handleInputChange}
                className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                required
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Trip Start Date *</label>
            <input
              type="date"
              name="trip_start_date"
              value={formData.trip_start_date}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              required
            />
          </div>
          <div className="form-group">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Trip End Date *</label>
            <input
              type="date"
              name="trip_end_date"
              value={formData.trip_end_date}
              onChange={handleInputChange}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label className="block text-sm font-semibold text-gray-700 mb-2">Planned Destinations *</label>
          <input
            type="text"
            placeholder="e.g., New York, Paris, Tokyo (comma-separated)"
            value={formData.planned_destinations.join(', ')}
            onChange={handleDestinationChange}
            className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
            required
          />
          <p className="text-sm text-gray-500 mt-1">Enter destinations separated by commas</p>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-4 px-6 rounded-xl font-bold text-white text-lg transition duration-200 ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transform hover:scale-105'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-2"></div>
              Generating Digital ID...
            </span>
          ) : (
            '🔐 Register & Generate Blockchain ID'
          )}
        </button>
      </form>
    </div>
  );
};

// Digital ID Display Component
const DigitalIDDisplay = ({ tourist }) => {
  return (
    <div className="digital-id bg-gradient-to-br from-blue-600 to-purple-700 rounded-2xl shadow-2xl p-8 text-white max-w-md mx-auto">
      <div className="text-center mb-6">
        <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-3xl">🆔</span>
        </div>
        <h3 className="text-2xl font-bold mb-2">Digital Tourist ID</h3>
        <p className="text-blue-100 text-sm">Blockchain-secured identity</p>
      </div>
      
      <div className="space-y-4">
        <div className="bg-white bg-opacity-10 rounded-lg p-4">
          <p className="text-blue-100 text-sm">Name</p>
          <p className="font-bold text-lg">{tourist.tourist_name}</p>
        </div>
        
        <div className="bg-white bg-opacity-10 rounded-lg p-4">
          <p className="text-blue-100 text-sm">ID Number</p>
          <p className="font-mono text-sm">{tourist.id}</p>
        </div>
        
        <div className="bg-white bg-opacity-10 rounded-lg p-4">
          <p className="text-blue-100 text-sm">Blockchain Hash</p>
          <p className="font-mono text-xs break-all">{tourist.blockchain_hash}</p>
        </div>
        
        <div className="bg-white bg-opacity-10 rounded-lg p-4">
          <p className="text-blue-100 text-sm">Verification Status</p>
          <div className="flex items-center">
            <span className="w-3 h-3 bg-green-400 rounded-full mr-2"></span>
            <span className="font-semibold">{tourist.verification_status}</span>
          </div>
        </div>
        
        {tourist.qr_code && (
          <div className="bg-white rounded-lg p-4 text-center">
            <p className="text-gray-800 text-sm mb-2">QR Code</p>
            <img src={tourist.qr_code} alt="QR Code" className="mx-auto w-32 h-32" />
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Interactive Map Component
const InteractiveMap = ({ userLocation, threats, routes, onLocationChange }) => {
  const [mapCenter, setMapCenter] = useState([20.0, 77.0]); // Default to India
  const [zoom, setZoom] = useState(6);
  const mapRef = useRef(null);

  useEffect(() => {
    if (userLocation) {
      setMapCenter([userLocation.lat, userLocation.lng]);
      setZoom(12);
    }
  }, [userLocation]);

  const getThreatColor = (threatLevel) => {
    if (threatLevel >= 8) return '#ef4444'; // red
    if (threatLevel >= 6) return '#f97316'; // orange  
    if (threatLevel >= 4) return '#eab308'; // yellow
    return '#22c55e'; // green
  };

  const getThreatIcon = (threatType) => {
    const icons = {
      'seismic': '🌍',
      'storm': '🌀',
      'flood': '🌊',
      'crime': '🚨',
      'health': '🏥',
      'restricted': '⛔',
      'volcanic': '🌋',
      'wildfire': '🔥'
    };
    return icons[threatType] || '⚠️';
  };

  return (
    <div className="interactive-map bg-white rounded-2xl shadow-2xl overflow-hidden">
      <div className="map-header bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
        <h3 className="text-xl font-bold flex items-center">
          <span className="mr-2">🗺️</span>
          Live Threat Map
        </h3>
        <p className="text-blue-100 text-sm">Real-time global safety monitoring</p>
      </div>
      
      <div className="map-container h-96">
        <MapContainer
          center={mapCenter}
          zoom={zoom}
          style={{ height: '100%', width: '100%' }}
          ref={mapRef}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {/* User Location Marker */}
          {userLocation && (
            <Marker position={[userLocation.lat, userLocation.lng]}>
              <Popup>
                <div className="text-center">
                  <strong>📍 Your Location</strong>
                  <br />
                  <small>{userLocation.lat.toFixed(4)}, {userLocation.lng.toFixed(4)}</small>
                </div>
              </Popup>
            </Marker>
          )}
          
          {/* Threat Zones */}
          {threats.map((threat, index) => (
            <React.Fragment key={index}>
              <Circle
                center={[threat.latitude, threat.longitude]}
                radius={threat.radius_km * 1000} // Convert to meters
                pathOptions={{
                  color: getThreatColor(threat.threat_level),
                  fillColor: getThreatColor(threat.threat_level),
                  fillOpacity: 0.2
                }}
              />
              <Marker position={[threat.latitude, threat.longitude]}>
                <Popup>
                  <div className="threat-popup">
                    <div className="flex items-center mb-2">
                      <span className="text-2xl mr-2">{getThreatIcon(threat.threat_type)}</span>
                      <strong>{threat.name}</strong>
                    </div>
                    <p className="text-sm mb-2">{threat.description}</p>
                    <div className="flex justify-between text-xs">
                      <span>Level: {threat.threat_level}/10</span>
                      <span>Radius: {threat.radius_km}km</span>
                    </div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          ))}
          
          {/* Route Lines */}
          {routes && (
            <>
              {routes.planned_route && (
                <Polyline
                  positions={routes.planned_route.map(p => [p.lat, p.lng])}
                  pathOptions={{ color: '#ef4444', weight: 4, opacity: 0.7 }}
                />
              )}
              {routes.safest_route && (
                <Polyline
                  positions={routes.safest_route.map(p => [p.lat, p.lng])}
                  pathOptions={{ color: '#22c55e', weight: 4, opacity: 0.7 }}
                />
              )}
            </>
          )}
        </MapContainer>
      </div>
      
      {/* Map Legend */}
      <div className="map-legend p-4 bg-gray-50 border-t">
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
            <span>High Risk (8-10)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-orange-500 rounded-full mr-2"></div>
            <span>Medium Risk (6-7)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 rounded-full mr-2"></div>
            <span>Low Risk (4-5)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
            <span>Safe (1-3)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Route Planner Component
const RoutePlanner = ({ tourist, onRouteCompare }) => {
  const [routeData, setRouteData] = useState({
    start_location: '',
    end_location: '',
    waypoints: []
  });
  const [routeComparison, setRouteComparison] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleLocationInput = (field, value) => {
    setRouteData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const geocodeLocation = async (locationName) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(locationName)}`
      );
      const data = await response.json();
      if (data.length > 0) {
        return {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon)
        };
      }
    } catch (error) {
      console.error('Geocoding error:', error);
    }
    return null;
  };

  const analyzeRoute = async () => {
    if (!routeData.start_location || !routeData.end_location) {
      alert('Please enter both start and end locations');
      return;
    }

    setIsAnalyzing(true);
    try {
      // Geocode locations
      const startCoords = await geocodeLocation(routeData.start_location);
      const endCoords = await geocodeLocation(routeData.end_location);
      
      if (!startCoords || !endCoords) {
        alert('Could not find coordinates for one or more locations');
        return;
      }

      // Get waypoint coordinates
      const waypointCoords = [];
      for (const waypoint of routeData.waypoints) {
        if (waypoint.trim()) {
          const coords = await geocodeLocation(waypoint);
          if (coords) waypointCoords.push(coords);
        }
      }

      // Call route comparison API
      const response = await axios.post(`${API}/routes/compare`, {
        tourist_id: tourist.id,
        start_location: startCoords,
        end_location: endCoords,
        waypoints: waypointCoords
      });

      setRouteComparison(response.data);
      onRouteCompare(response.data);
    } catch (error) {
      console.error('Route analysis failed:', error);
      alert('Route analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="route-planner bg-white rounded-2xl shadow-2xl p-6">
      <div className="header mb-6">
        <h3 className="text-2xl font-bold text-gray-800 flex items-center">
          <span className="mr-2">🛣️</span>
          Smart Route Planner
        </h3>
        <p className="text-gray-600">Compare your planned route with the safest alternative</p>
      </div>

      <div className="route-inputs space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Start Location</label>
          <input
            type="text"
            placeholder="Enter starting point (e.g., New York, NY)"
            value={routeData.start_location}
            onChange={(e) => handleLocationInput('start_location', e.target.value)}
            className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">End Location</label>
          <input
            type="text"
            placeholder="Enter destination (e.g., Los Angeles, CA)"
            value={routeData.end_location}
            onChange={(e) => handleLocationInput('end_location', e.target.value)}
            className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Waypoints (Optional)</label>
          <input
            type="text"
            placeholder="Enter stops along the way (comma-separated)"
            value={routeData.waypoints.join(', ')}
            onChange={(e) => handleLocationInput('waypoints', e.target.value.split(',').map(w => w.trim()))}
            className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
          />
        </div>

        <button
          onClick={analyzeRoute}
          disabled={isAnalyzing}
          className={`w-full py-3 px-6 rounded-xl font-bold text-white transition duration-200 ${
            isAnalyzing
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transform hover:scale-105'
          }`}
        >
          {isAnalyzing ? (
            <span className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Analyzing Routes...
            </span>
          ) : (
            '🎯 Analyze & Compare Routes'
          )}
        </button>
      </div>

      {routeComparison && (
        <div className="route-results mt-6 space-y-4">
          <h4 className="text-lg font-bold text-gray-800">Route Comparison Results</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="planned-route bg-red-50 border-2 border-red-200 rounded-xl p-4">
              <div className="flex items-center mb-2">
                <span className="w-4 h-4 bg-red-500 rounded-full mr-2"></span>
                <h5 className="font-bold text-red-800">Your Planned Route</h5>
              </div>
              <div className="safety-score text-2xl font-bold text-red-600 mb-2">
                Safety Score: {routeComparison.planned_safety_score}/100
              </div>
              <div className="risks">
                <p className="text-sm font-semibold text-red-700 mb-1">Risk Factors:</p>
                <ul className="text-xs text-red-600 space-y-1">
                  {routeComparison.risk_analysis.planned_risks.map((risk, index) => (
                    <li key={index}>• {risk}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="safest-route bg-green-50 border-2 border-green-200 rounded-xl p-4">
              <div className="flex items-center mb-2">
                <span className="w-4 h-4 bg-green-500 rounded-full mr-2"></span>
                <h5 className="font-bold text-green-800">Recommended Safe Route</h5>
              </div>
              <div className="safety-score text-2xl font-bold text-green-600 mb-2">
                Safety Score: {routeComparison.safest_safety_score}/100
              </div>
              <div className="benefits">
                <p className="text-sm font-semibold text-green-700 mb-1">Safety Benefits:</p>
                <ul className="text-xs text-green-600 space-y-1">
                  {routeComparison.recommendations.map((rec, index) => (
                    <li key={index}>• {rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="improvement-score bg-blue-50 border-2 border-blue-200 rounded-xl p-4 text-center">
            <div className="text-lg font-bold text-blue-800">
              Safety Improvement: +{routeComparison.safest_safety_score - routeComparison.planned_safety_score} points
            </div>
            <p className="text-sm text-blue-600 mt-1">
              The recommended route is {routeComparison.safest_safety_score - routeComparison.planned_safety_score}% safer
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

// Admin Dashboard Component
const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [tourists, setTourists] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const [statsResponse, touristsResponse, alertsResponse] = await Promise.all([
        axios.get(`${API}/admin/dashboard/stats`),
        axios.get(`${API}/admin/tourists?limit=10`),
        axios.get(`${API}/admin/alerts?limit=10`)
      ]);

      setDashboardData(statsResponse.data);
      setTourists(touristsResponse.data.tourists);
      setAlerts(alertsResponse.data.alerts);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="admin-loading flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard space-y-6">
      <div className="admin-header bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-2xl p-6">
        <h2 className="text-3xl font-bold flex items-center">
          <span className="mr-2">⚡</span>
          Admin Dashboard
        </h2>
        <p className="text-purple-100 mt-2">Global tourism safety monitoring & management</p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="stat-card bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Active Tourists</p>
              <p className="text-3xl font-bold">{dashboardData?.overview.active_tourists || 0}</p>
            </div>
            <div className="text-4xl opacity-75">👥</div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm">Active Alerts</p>
              <p className="text-3xl font-bold">{dashboardData?.overview.active_alerts || 0}</p>
            </div>
            <div className="text-4xl opacity-75">🚨</div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Threat Zones</p>
              <p className="text-3xl font-bold">{dashboardData?.overview.high_threat_zones || 0}</p>
            </div>
            <div className="text-4xl opacity-75">⚠️</div>
          </div>
        </div>

        <div className="stat-card bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Active Advisories</p>
              <p className="text-3xl font-bold">{dashboardData?.overview.active_advisories || 0}</p>
            </div>
            <div className="text-4xl opacity-75">📋</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="tourists-panel bg-white rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">👤</span>
            Recent Tourist Registrations
          </h3>
          <div className="space-y-3">
            {tourists.slice(0, 5).map((tourist, index) => (
              <div key={index} className="tourist-item flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-800">{tourist.tourist_name}</p>
                  <p className="text-sm text-gray-600">{tourist.nationality} • {tourist.phone_number}</p>
                </div>
                <div className="text-right">
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    tourist.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {tourist.is_active ? 'Active' : 'Inactive'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Score: {tourist.safety_score}/100
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="alerts-panel bg-white rounded-2xl shadow-xl p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">🚨</span>
            Recent Emergency Alerts
          </h3>
          <div className="space-y-3">
            {alerts.slice(0, 5).map((alert, index) => (
              <div key={index} className="alert-item p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    alert.status === 'active' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {alert.alert_type}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(alert.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-gray-800">{alert.message || 'Emergency alert triggered'}</p>
                <p className="text-xs text-gray-600 mt-1">
                  Location: {alert.latitude.toFixed(4)}, {alert.longitude.toFixed(4)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="system-health bg-white rounded-2xl shadow-xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
          <span className="mr-2">💊</span>
          System Health
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="health-item flex items-center p-3 bg-green-50 rounded-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <div>
              <p className="font-semibold text-green-800">AI Integration</p>
              <p className="text-sm text-green-600">Operational</p>
            </div>
          </div>
          <div className="health-item flex items-center p-3 bg-green-50 rounded-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <div>
              <p className="font-semibold text-green-800">Database</p>
              <p className="text-sm text-green-600">Operational</p>
            </div>
          </div>
          <div className="health-item flex items-center p-3 bg-green-50 rounded-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <div>
              <p className="font-semibold text-green-800">Threat Database</p>
              <p className="text-sm text-green-600">Updated</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced Safety Score Component
const EnhancedSafetyScore = ({ safetyScore, route, userLocation }) => {
  const [locationThreats, setLocationThreats] = useState([]);
  const [detailedAdvisories, setDetailedAdvisories] = useState([]);

  useEffect(() => {
    if (userLocation) {
      loadLocationData();
    }
  }, [userLocation]);

  const loadLocationData = async () => {
    try {
      const [threatsResponse, advisoriesResponse] = await Promise.all([
        axios.get(`${API}/threats/nearby?lat=${userLocation.lat}&lng=${userLocation.lng}&radius=50`),
        axios.get(`${API}/advisories/detailed?lat=${userLocation.lat}&lng=${userLocation.lng}&radius=100`)
      ]);

      setLocationThreats(threatsResponse.data.threats);
      setDetailedAdvisories(advisoriesResponse.data.advisories);
    } catch (error) {
      console.error('Failed to load location data:', error);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'from-green-400 to-green-600';
    if (score >= 60) return 'from-yellow-400 to-yellow-600';
    return 'from-red-400 to-red-600';
  };

  const getScoreTextColor = (score) => {
    if (score >= 80) return 'text-green-800';
    if (score >= 60) return 'text-yellow-800';
    return 'text-red-800';
  };

  return (
    <div className="enhanced-safety-score space-y-6">
      {/* Main Safety Score */}
      <div className="safety-score-card bg-white rounded-2xl shadow-2xl p-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <span className="mr-2">🛡️</span>
          Current Safety Score
        </h3>
        
        <div className={`score-display bg-gradient-to-r ${getScoreColor(safetyScore)} rounded-2xl p-8 text-white text-center mb-6`}>
          <div className="text-6xl font-bold mb-2">{safetyScore}</div>
          <div className="text-lg opacity-90">out of 100</div>
          <div className="text-sm opacity-75 mt-2">
            {safetyScore >= 80 ? 'Excellent Safety' : safetyScore >= 60 ? 'Good Safety' : 'Exercise Caution'}
          </div>
        </div>

        {/* Route Comparison */}
        {route && (
          <div className="route-scores grid grid-cols-2 gap-4 mb-6">
            <div className="planned-score bg-red-50 border-2 border-red-200 rounded-xl p-4 text-center">
              <p className="text-sm font-semibold text-red-700 mb-1">Planned Route</p>
              <p className="text-2xl font-bold text-red-600">{route.planned_safety_score}</p>
            </div>
            <div className="safe-score bg-green-50 border-2 border-green-200 rounded-xl p-4 text-center">
              <p className="text-sm font-semibold text-green-700 mb-1">Safest Route</p>
              <p className="text-2xl font-bold text-green-600">{route.safest_safety_score}</p>
            </div>
          </div>
        )}

        {/* Nearby Threats */}
        {locationThreats.length > 0 && (
          <div className="nearby-threats">
            <h4 className="font-bold text-gray-800 mb-3">⚠️ Nearby Threats</h4>
            <div className="threats-list space-y-2 max-h-32 overflow-y-auto">
              {locationThreats.slice(0, 5).map((threat, index) => (
                <div key={index} className="threat-item flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${
                      threat.threat_level >= 8 ? 'bg-red-500' : 
                      threat.threat_level >= 6 ? 'bg-orange-500' : 'bg-yellow-500'
                    }`}></div>
                    <span className="text-sm font-medium">{threat.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{threat.threat_level}/10</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Detailed Advisories */}
      {detailedAdvisories.length > 0 && (
        <div className="detailed-advisories bg-white rounded-2xl shadow-2xl p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">📋</span>
            Location-Based Advisories
          </h3>
          <div className="advisories-list space-y-3 max-h-64 overflow-y-auto">
            {detailedAdvisories.map((advisory, index) => (
              <div key={index} className={`advisory-card p-4 rounded-xl border-l-4 ${
                advisory.severity === 'critical' ? 'bg-red-50 border-red-500' :
                advisory.severity === 'warning' ? 'bg-orange-50 border-orange-500' :
                advisory.severity === 'caution' ? 'bg-yellow-50 border-yellow-500' :
                'bg-blue-50 border-blue-500'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-bold text-gray-800">{advisory.title}</h5>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    advisory.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    advisory.severity === 'warning' ? 'bg-orange-100 text-orange-800' :
                    advisory.severity === 'caution' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {advisory.severity}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{advisory.content}</p>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{advisory.advisory_type}</span>
                  <span>{advisory.source}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('home');
  const [tourist, setTourist] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [threats, setThreats] = useState([]);
  const [routeComparison, setRouteComparison] = useState(null);
  const [safetyScore, setSafetyScore] = useState(85);

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setUserLocation(location);
          loadLocationThreats(location);
        },
        (error) => {
          console.error('Location access denied:', error);
          // Fallback to New York coordinates for demo
          const fallbackLocation = { lat: 40.7128, lng: -74.0060 };
          setUserLocation(fallbackLocation);
          loadLocationThreats(fallbackLocation);
        }
      );
    }
  }, []);

  const loadLocationThreats = async (location) => {
    try {
      const response = await axios.get(`${API}/threats/nearby?lat=${location.lat}&lng=${location.lng}&radius=200`);
      setThreats(response.data.threats);
    } catch (error) {
      console.error('Failed to load threats:', error);
    }
  };

  // Initialize global threat database
  useEffect(() => {
    const initializeThreats = async () => {
      try {
        await axios.post(`${API}/init/global-threats`);
      } catch (error) {
        console.error('Failed to initialize threats:', error);
      }
    };
    initializeThreats();
  }, []);

  const handleRegistrationSuccess = (touristData) => {
    setTourist(touristData);
    setCurrentView('dashboard');
  };

  const handleRouteComparison = (routeData) => {
    setRouteComparison(routeData);
    setSafetyScore(routeData.planned_safety_score);
  };

  const handleLocationUpdate = async (location) => {
    if (tourist) {
      try {
        await axios.post(`${API}/location/update`, {
          tourist_id: tourist.id,
          latitude: location.lat,
          longitude: location.lng,
          location_name: 'Current Location'
        });
        
        // Get updated safety analysis
        const analysisResponse = await axios.get(`${API}/safety/analysis/${tourist.id}`);
        setSafetyScore(analysisResponse.data.current_safety_score);
      } catch (error) {
        console.error('Failed to update location:', error);
      }
    }
  };

  // Update location when user location changes
  useEffect(() => {
    if (userLocation && tourist) {
      handleLocationUpdate(userLocation);
    }
  }, [userLocation, tourist]);

  const renderView = () => {
    switch (currentView) {
      case 'register':
        return <TouristRegistration onRegistrationSuccess={handleRegistrationSuccess} />;
      
      case 'admin':
        return <AdminDashboard />;
      
      case 'dashboard':
        return (
          <div className="dashboard-layout space-y-8">
            {/* Digital ID Display */}
            {tourist && (
              <div className="digital-id-section">
                <DigitalIDDisplay tourist={tourist} />
              </div>
            )}
            
            {/* Main Dashboard Grid */}
            <div className="dashboard-grid grid grid-cols-1 xl:grid-cols-3 gap-8">
              {/* Map Section */}
              <div className="xl:col-span-2">
                <InteractiveMap 
                  userLocation={userLocation}
                  threats={threats}
                  routes={routeComparison}
                  onLocationChange={setUserLocation}
                />
              </div>
              
              {/* Safety Score */}
              <div>
                <EnhancedSafetyScore 
                  safetyScore={safetyScore}
                  route={routeComparison}
                  userLocation={userLocation}
                />
              </div>
            </div>
            
            {/* Route Planner */}
            {tourist && (
              <RoutePlanner 
                tourist={tourist}
                onRouteCompare={handleRouteComparison}
              />
            )}
          </div>
        );
      
      default:
        return (
          <div className="home-view">
            {/* Hero Section */}
            <div className="hero-section mb-16">
              <div className="hero-background relative overflow-hidden rounded-3xl">
                <div className="hero-image-container mb-8">
                  <img
                    src="https://images.unsplash.com/photo-1697800937428-6aea55069bf9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxub3J0aGVhc3QlMjBpbmRpYSUyMG1vdW50YWluc3xlbnwwfHx8Ymx1ZXwxNzU3OTM1NTI5fDA&ixlib=rb-4.1.0&q=85"
                    alt="Global Tourism Safety"
                    className="w-full h-96 object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-900/80 to-purple-900/80"></div>
                </div>
                
                <div className="hero-content absolute inset-0 flex items-center justify-center">
                  <div className="text-center text-white max-w-4xl px-8">
                    <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-200 to-purple-200 bg-clip-text text-transparent">
                      Global Tourism Safety Platform
                    </h1>
                    <p className="text-xl md:text-2xl mb-8 text-blue-100">
                      AI-powered safety monitoring, blockchain digital IDs, and real-time threat detection for travelers worldwide
                    </p>
                    
                    <div className="features-showcase grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                      <div className="feature-highlight bg-white/10 backdrop-blur-sm rounded-2xl p-6 transform hover:scale-105 transition duration-300">
                        <div className="text-4xl mb-3">🔗</div>
                        <h3 className="font-bold text-lg mb-2">Blockchain ID</h3>
                        <p className="text-sm text-blue-200">Secure digital identity</p>
                      </div>
                      
                      <div className="feature-highlight bg-white/10 backdrop-blur-sm rounded-2xl p-6 transform hover:scale-105 transition duration-300">
                        <div className="text-4xl mb-3">🤖</div>
                        <h3 className="font-bold text-lg mb-2">AI Analysis</h3>
                        <p className="text-sm text-blue-200">Smart threat detection</p>
                      </div>
                      
                      <div className="feature-highlight bg-white/10 backdrop-blur-sm rounded-2xl p-6 transform hover:scale-105 transition duration-300">
                        <div className="text-4xl mb-3">🗺️</div>
                        <h3 className="font-bold text-lg mb-2">Live Maps</h3>
                        <p className="text-sm text-blue-200">Real-time threat zones</p>
                      </div>
                      
                      <div className="feature-highlight bg-white/10 backdrop-blur-sm rounded-2xl p-6 transform hover:scale-105 transition duration-300">
                        <div className="text-4xl mb-3">🛣️</div>
                        <h3 className="font-bold text-lg mb-2">Smart Routes</h3>
                        <p className="text-sm text-blue-200">Safest path planning</p>
                      </div>
                    </div>

                    <div className="cta-buttons flex flex-col sm:flex-row gap-4 justify-center">
                      <button
                        onClick={() => setCurrentView('register')}
                        className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-4 rounded-2xl hover:from-blue-700 hover:to-purple-700 transition duration-300 font-bold text-lg transform hover:scale-105 shadow-2xl"
                      >
                        🚀 Start Your Safe Journey
                      </button>
                      <button
                        onClick={() => setCurrentView('dashboard')}
                        className="bg-white/20 backdrop-blur-sm text-white border-2 border-white/30 px-10 py-4 rounded-2xl hover:bg-white/30 transition duration-300 font-bold text-lg transform hover:scale-105"
                      >
                        🎯 Explore Demo
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature Details */}
            <div className="features-details grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
              <div className="feature-card bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 shadow-xl transform hover:scale-105 transition duration-300">
                <div className="feature-icon w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center text-white text-2xl mb-6">🛡️</div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Advanced Safety Scoring</h3>
                <p className="text-gray-600">AI-powered analysis of your location and routes with real-time safety scores based on global threat intelligence.</p>
              </div>
              
              <div className="feature-card bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-8 shadow-xl transform hover:scale-105 transition duration-300">
                <div className="feature-icon w-16 h-16 bg-purple-600 rounded-2xl flex items-center justify-center text-white text-2xl mb-6">🗺️</div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Interactive Threat Maps</h3>
                <p className="text-gray-600">Live OpenStreetMap integration showing real-time threats, safe zones, and recommended routes worldwide.</p>
              </div>
              
              <div className="feature-card bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-8 shadow-xl transform hover:scale-105 transition duration-300">
                <div className="feature-icon w-16 h-16 bg-green-600 rounded-2xl flex items-center justify-center text-white text-2xl mb-6">🆘</div>
                <h3 className="text-xl font-bold text-gray-800 mb-4">Emergency Response</h3>
                <p className="text-gray-600">One-tap SOS with automated E-FIR generation and immediate notification to local authorities and emergency contacts.</p>
              </div>
            </div>

            {/* Call to Action */}
            <div className="cta-section bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-3xl p-12 text-center">
              <h2 className="text-4xl font-bold mb-4">Ready to Travel Safely?</h2>
              <p className="text-xl mb-8 text-blue-100">Join thousands of travelers using our AI-powered safety platform</p>
              <button
                onClick={() => setCurrentView('register')}
                className="bg-white text-blue-600 px-10 py-4 rounded-2xl hover:bg-blue-50 transition duration-300 font-bold text-lg transform hover:scale-105 shadow-xl"
              >
                Get Your Digital ID Now
              </button>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Enhanced Navigation */}
      <nav className="nav-bar bg-white/90 backdrop-blur-lg shadow-xl border-b border-white/20 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="logo flex items-center space-x-3">
              <div className="logo-icon w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white text-xl font-bold">🌍</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">SafeTravel AI</h1>
                <p className="text-xs text-gray-500">Global Safety Platform</p>
              </div>
            </div>
            
            <div className="nav-links flex space-x-2">
              <button
                onClick={() => setCurrentView('home')}
                className={`px-6 py-3 rounded-xl transition duration-200 font-semibold ${
                  currentView === 'home' 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Home
              </button>
              
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-6 py-3 rounded-xl transition duration-200 font-semibold ${
                  currentView === 'dashboard' 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
              
              <button
                onClick={() => setCurrentView('register')}
                className={`px-6 py-3 rounded-xl transition duration-200 font-semibold ${
                  currentView === 'register' 
                    ? 'bg-blue-600 text-white shadow-lg' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Register
              </button>

              <button
                onClick={() => setCurrentView('admin')}
                className={`px-6 py-3 rounded-xl transition duration-200 font-semibold ${
                  currentView === 'admin' 
                    ? 'bg-purple-600 text-white shadow-lg' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Admin
              </button>
            </div>

            {tourist && (
              <div className="user-info flex items-center space-x-4">
                <div className="user-details text-right">
                  <p className="text-sm font-semibold text-gray-800">{tourist.tourist_name}</p>
                  <p className="text-xs text-gray-500">ID: {tourist.id.slice(0, 8)}</p>
                </div>
                <div className={`safety-badge px-3 py-2 rounded-xl text-sm font-bold ${
                  safetyScore >= 80 
                    ? 'bg-green-100 text-green-800' 
                    : safetyScore >= 60
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  🛡️ {safetyScore}
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content container mx-auto px-6 py-8">
        {renderView()}
      </main>

      {/* Enhanced Footer */}
      <footer className="footer bg-gradient-to-r from-gray-800 to-gray-900 text-white py-12 mt-16">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="footer-brand">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">🌍</span>
                </div>
                <h3 className="text-xl font-bold">SafeTravel AI</h3>
              </div>
              <p className="text-gray-300 text-sm">
                Advanced AI-powered tourism safety platform with blockchain security and global threat intelligence.
              </p>
            </div>
            
            <div className="footer-links">
              <h4 className="font-bold mb-4">Safety Features</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Real-time Threat Detection</li>
                <li>• AI Safety Scoring</li>
                <li>• Emergency Response</li>
                <li>• Route Optimization</li>
              </ul>
            </div>
            
            <div className="footer-links">
              <h4 className="font-bold mb-4">Technology</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Blockchain Digital ID</li>
                <li>• Google Gemini AI</li>
                <li>• OpenStreetMap</li>
                <li>• Global Database</li>
              </ul>
            </div>
            
            <div className="footer-contact">
              <h4 className="font-bold mb-4">Emergency</h4>
              <div className="space-y-2 text-sm text-gray-300">
                <p>🚨 Global Emergency: 112</p>
                <p>📞 Tourist Helpline: 1363</p>
                <p>🏥 Medical Emergency: 108</p>
                <p>🚔 Police: 100</p>
              </div>
            </div>
          </div>
          
          <div className="footer-bottom border-t border-gray-700 mt-8 pt-8 text-center">
            <p className="text-gray-400 text-sm">
              © 2025 SafeTravel AI | Powered by Advanced AI & Blockchain Technology | 
              <span className="text-blue-400"> Making Travel Safer Worldwide</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;