import {
  GoogleMap,
  LoadScript,
  MarkerF,
  InfoBox,
  PolylineF,
} from "@react-google-maps/api";
import { useRef, useEffect, useState } from "react";
import "./Map.css";

function Map({
  trips,
  selectedTrip,
  setSelectedTrip,
  selectedAttractions,
  onMapClick,
  onLearnMore,
  isChatOpen,
}) {
  const mapRef = useRef(null);
  const [lastSelectedTrip, setLastSelectedTrip] = useState(null);
  const [isMapReady, setIsMapReady] = useState(false);

  const center = lastSelectedTrip
    ? { lat: lastSelectedTrip.lat, lng: lastSelectedTrip.lng }
    : { lat: 20, lng: 0 };

  const onLoad = (map) => {
    mapRef.current = map;
    setIsMapReady(true);

    const handleResize = () => {
      if (mapRef.current) {
        setTimeout(() => {
          window.google.maps.event.trigger(mapRef.current, "resize");
        }, 50);
      }
    };

    window.addEventListener("resize", handleResize);

    map._resizeHandler = handleResize;
  };

  const handleMapClick = (event) => {
    if (onMapClick) {
      const lat = event.latLng.lat();
      const lng = event.latLng.lng();
      onMapClick({ lat, lng });
    }
  };

  useEffect(() => {
    if (selectedTrip) {
      setLastSelectedTrip(selectedTrip);
    }
  }, [selectedTrip]);

  useEffect(() => {
    if (!mapRef.current || !selectedAttractions?.length) return;

    const bounds = new window.google.maps.LatLngBounds();
    selectedAttractions.forEach(({ lat, lon }) =>
      bounds.extend({ lat, lng: lon })
    );
    mapRef.current.fitBounds(bounds);
  }, [selectedAttractions]);

  useEffect(() => {
    if (!isChatOpen && mapRef.current && selectedAttractions?.length > 0) {
      setTimeout(() => {
        if (window.google && window.google.maps && mapRef.current) {
          window.google.maps.event.trigger(mapRef.current, "resize");

          const bounds = new window.google.maps.LatLngBounds();
          selectedAttractions.forEach(({ lat, lon }) =>
            bounds.extend({ lat, lng: lon })
          );
          mapRef.current.fitBounds(bounds);
        }
      }, 150);
    } else if (
      !isChatOpen &&
      mapRef.current &&
      lastSelectedTrip &&
      !selectedAttractions?.length
    ) {
      setTimeout(() => {
        if (window.google && window.google.maps && mapRef.current) {
          window.google.maps.event.trigger(mapRef.current, "resize");

          mapRef.current.setCenter({
            lat: lastSelectedTrip.lat,
            lng: lastSelectedTrip.lng,
          });
          mapRef.current.setZoom(8);
        }
      }, 150);
    }
  }, [isChatOpen, selectedAttractions, lastSelectedTrip]);

  useEffect(() => {
    return () => {
      if (mapRef.current && mapRef.current._resizeHandler) {
        window.removeEventListener("resize", mapRef.current._resizeHandler);
      }
    };
  }, []);

  const path =
    selectedAttractions?.map(({ lat, lon }) => ({ lat, lng: lon })) || [];

  const createSize = (width, height) => {
    if (
      isMapReady &&
      window.google &&
      window.google.maps &&
      window.google.maps.Size
    ) {
      return new window.google.maps.Size(width, height);
    }
    return null;
  };

  return (
    <div className="map-wrapper">
      {!isMapReady && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "rgba(255, 255, 255, 0.9)",
            padding: "20px",
            borderRadius: "10px",
            zIndex: 1000,
            fontSize: "16px",
            color: "#2d4238",
          }}
        >
          Loading map...
        </div>
      )}
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
          onClick={handleMapClick}
          options={{
            streetViewControl: false,
            mapTypeControl: false,
          }}
        >
          {trips.map((trip) => (
            <MarkerF
              key={`${trip.trip_id}`}
              position={{ lat: trip.lat, lng: trip.lng }}
              title={`${trip.title}`}
              icon={{
                url: "http://maps.google.com/mapfiles/kml/pal4/icon49.png",
                scaledSize: createSize(40, 40),
              }}
              onClick={() => setSelectedTrip(trip)}
            />
          ))}

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
                scaledSize: createSize(50, 50),
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
                lat: selectedTrip.lat,
                lng: selectedTrip.lng,
              }}
              options={{ closeBoxURL: "", enableEventPropagation: true }}
            >
              <div className="info-window">
                <button
                  style={{
                    position: "absolute",
                    top: "4px",
                    right: "4px",
                    background: "transparent",
                    border: "none",
                    color: "#fff",
                    fontSize: "16px",
                    cursor: "pointer",
                  }}
                  onClick={() => setSelectedTrip(null)}
                >
                  ×
                </button>

                <h3>{selectedTrip.title}</h3>
                {selectedTrip.cities && (
                  <p>
                    <strong>Cities:</strong> {selectedTrip.cities}
                  </p>
                )}
                {selectedTrip.description && <p>{selectedTrip.description}</p>}
                {selectedTrip.duration && (
                  <p>Duration: {selectedTrip.duration} days</p>
                )}
                {selectedTrip.budget && <p>Budget: ${selectedTrip.budget}</p>}
                {selectedTrip.num_people && (
                  <p>People: {selectedTrip.num_people}</p>
                )}
                {selectedTrip.activity_level && (
                  <p>Activity: {selectedTrip.activity_level}</p>
                )}
                <button
                  style={{
                    background: "#e6b474",
                    color: "#2d4238",
                    border: "none",
                    borderRadius: "15px",
                    padding: "8px 16px",
                    marginTop: "10px",
                    cursor: "pointer",
                    fontWeight: "bold",
                    fontSize: "14px",
                  }}
                  onClick={() => {
                    if (onLearnMore) {
                      onLearnMore(selectedTrip);
                    }
                  }}
                >
                  Learn more
                </button>
              </div>
            </InfoBox>
          )}
        </GoogleMap>
      </LoadScript>
    </div>
  );
}

export default Map;
