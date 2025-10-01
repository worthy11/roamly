import Layout from "./components/Layout";
import "./App.css";
import { useState, useEffect } from "react";
import { BsRobot } from "react-icons/bs";
import {
  GoogleMap,
  LoadScript,
  MarkerF,
  InfoWindowF,
} from "@react-google-maps/api";
import { API_BASE } from "./config";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const response = await fetch(`${API_BASE}/trips/`);
        const data = await response.json();
        setTrips(data);
      } catch (err) {
        console.error("Error fetching trips:", err);
      }
    };

    fetchTrips();
  }, []);

  const handleSend = (e) => {
    e.preventDefault();
    if (message.trim() === "") return;
    setChat([...chat, { from: "user", text: message }]);
    setMessage("");
  };

  async function fetchResponse() {
    try {
      const response = await fetch(`${API_BASE}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 0,
          message: message,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log(data.response);
    } catch (error) {
      console.error("Error fetching response:", error);
      return { error: error.message };
    }
  }

  const center = {
    lat: 20,
    lng: 0,
  };

  return (
    <>
      <Layout>
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
                      scaledSize: new window.google.maps.Size(40, 40), // optional size
                    }}
                    onClick={() => setSelectedTrip({ trip, city })}
                  />
                ))
              )}

              {selectedTrip && (
                <InfoWindowF
                  position={{
                    lat: selectedTrip.city.lat,
                    lng: selectedTrip.city.lon,
                  }}
                  onCloseClick={() => setSelectedTrip(null)}
                >
                  <div className="info-window">
                    <h3>
                      {selectedTrip.city.name}, {selectedTrip.trip.country}
                    </h3>
                    {selectedTrip.trip.description && (
                      <p>{selectedTrip.trip.description}</p>
                    )}
                    {selectedTrip.trip.duration && (
                      <p>Duration: {selectedTrip.trip.duration} days</p>
                    )}
                    {selectedTrip.trip.budget && (
                      <p>Budget: ${selectedTrip.trip.budget}</p>
                    )}
                    {selectedTrip.trip.num_people && (
                      <p>People: {selectedTrip.trip.num_people}</p>
                    )}
                    {selectedTrip.trip.activity_level && (
                      <p>Activity: {selectedTrip.trip.activity_level}</p>
                    )}
                  </div>
                </InfoWindowF>
              )}
            </GoogleMap>
          </LoadScript>
        </div>

        <div className="chatbot-container">
          <h2 className="chatbot-title">
            Plan your next trip <BsRobot size={35} title="ChatBot" />
          </h2>
          <div className="chatbot-underline"></div>
          <div className="chat-window">
            {chat.length === 0 && (
              <div className="chat-placeholder">No messages</div>
            )}
            {chat.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.from}`}>
                {msg.text}
              </div>
            ))}
          </div>
          <form className="chat-input-row" onSubmit={handleSend}>
            <input
              type="text"
              placeholder="Send message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="chat-input"
            />
            <button
              type="submit"
              className="chat-send-btn"
              onClick={fetchResponse}
            >
              Send
            </button>
          </form>
        </div>
      </Layout>
    </>
  );
}

export default App;
