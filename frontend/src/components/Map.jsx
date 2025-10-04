import { GoogleMap, LoadScript, MarkerF, InfoBox } from "@react-google-maps/api";
import './Map.css';

function Map({ trips, selectedTrip, setSelectedTrip }) {
  const center = {
    lat: 20,
    lng: 0,
  };

  return (
    <div className="map-wrapper">
      <LoadScript
        googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}
        language="en"
      >
        <GoogleMap
          mapContainerClassName="custom-map"
          center={center}
          zoom={2}
          mapTypeId="roadmap"
          options={{
            streetViewControl: false,
            mapTypeControl: false,
          }}
        >
          {trips.map((trip) =>
            trip.cities.map((city) => (
              <MarkerF
                key={`${trip.trip_id}-${city.name}`}
                position={{ lat: city.lat, lng: city.lon }}
                title={`${trip.country} - ${city.name}`}
                icon={{
                  url: "http://maps.google.com/mapfiles/kml/pal4/icon49.png",
                  scaledSize: new window.google.maps.Size(40, 40),
                }}
                onClick={() => setSelectedTrip({ trip, city })}
              />
            ))
          )}

          {selectedTrip && (
  <InfoBox
    position={{
      lat: selectedTrip.city.lat,
      lng: selectedTrip.city.lon,
    }}
    options={{ closeBoxURL: '', enableEventPropagation: true }}
  >
    <div className="info-window">
      {/* Twój przycisk zamknięcia */}
      <button
        style={{
          position: 'absolute',
          top: '4px',
          right: '4px',
          background: 'transparent',
          border: 'none',
          color: '#fff',
          fontSize: '16px',
          cursor: 'pointer',
        }}
        onClick={() => setSelectedTrip(null)}
      >
        ×
      </button>

      <h3>
        {selectedTrip.city.name}, {selectedTrip.trip.country}
      </h3>
      {selectedTrip.trip.description && <p>{selectedTrip.trip.description}</p>}
      {selectedTrip.trip.duration && <p>Duration: {selectedTrip.trip.duration} days</p>}
      {selectedTrip.trip.budget && <p>Budget: ${selectedTrip.trip.budget}</p>}
      {selectedTrip.trip.num_people && <p>People: {selectedTrip.trip.num_people}</p>}
      {selectedTrip.trip.activity_level && <p>Activity: {selectedTrip.trip.activity_level}</p>}
    </div>
  </InfoBox>
)}
        </GoogleMap>
      </LoadScript>
    </div>
  );
}

export default Map;