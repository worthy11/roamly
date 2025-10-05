import {
  GoogleMap,
  LoadScript,
  MarkerF,
  InfoBox,
  PolylineF,
} from "@react-google-maps/api";
import { useRef, useEffect } from "react";
import "./Map.css";

function Map({ trips, selectedTrip, setSelectedTrip, selectedAttractions }) {
  const mapRef = useRef(null);
  const center = {
    lat: 20,
    lng: 0,
  };

  const onLoad = (map) => {
    mapRef.current = map;
  };

  useEffect(() => {
    if (!mapRef.current || !selectedAttractions?.length) return;

    const bounds = new window.google.maps.LatLngBounds();
    selectedAttractions.forEach(({ lat, lon }) =>
      bounds.extend({ lat, lng: lon })
    );
    mapRef.current.fitBounds(bounds);
  }, [selectedAttractions]);

  const path =
    selectedAttractions?.map(({ lat, lon }) => ({ lat, lng: lon })) || [];

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
          onLoad={onLoad}
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

          {selectedAttractions?.map((a, idx) => (
            <MarkerF
              key={`attraction-${idx}`}
              position={{ lat: a.lat, lng: a.lon }}
              title={a.name}
              icon={{
                url: `data:image/svg+xml;utf-8,${encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">
                  <circle cx="14" cy="14" r="15" fill="#ff1e00ff" stroke="white" stroke-width="2"/>
                  <text x="14" y="20" font-size="18" font-family="Arial" fill="white" text-anchor="middle">${
                    idx + 1
                  }</text>
                </svg>
              `)}`,
                scaledSize: new window.google.maps.Size(50, 50),
              }}
            />
          ))}

          {path.length > 1 && (
            <PolylineF
              path={path}
              options={{
                strokeColor: "#ff5722",
                strokeOpacity: 0.9,
                strokeWeight: 3,
                icons: [
                  {
                    icon: {
                      path: window.google.maps.SymbolPath.FORWARD_OPEN_ARROW,
                    },
                    offset: "100%",
                  },
                ],
              }}
            />
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
