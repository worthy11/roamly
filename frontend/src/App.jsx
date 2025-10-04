import Layout from "./components/Layout";
import "./App.css";
import { useState, useEffect } from "react";
import { BsRobot } from "react-icons/bs";
import { FaSuitcase } from "react-icons/fa";
import {
  GoogleMap,
  LoadScript,
  MarkerF,
  InfoBox,
} from "@react-google-maps/api";
import { API_BASE } from "./config";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);

  const [formData, setFormData] = useState({
    from: "",
    to: "",
    transport: "",
    people: "",
    dateFrom: "",
    dateTo: "",
    activity: "",
    population: "",
    budget: "",
    attractions: "",
  });

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

  const sendMessage = async (text) => {
    const userMessage = { from: "user", text };
    setChat((prev) => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE}/chat/text`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 0,
          message: text,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      const botMessage = { from: "bot", text: data.response };
      setChat((prev) => [...prev, botMessage]);

      // Log structured trip plan to console if available
      if (data.trip_plan) {
        console.log(data.trip_plan);
      }
    } catch (error) {
      console.error("Error fetching response:", error);
      setChat((prev) => [
        ...prev,
        { from: "bot", text: "Error: " + error.message },
      ]);
    }
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (message.trim() === "") return;
    const currentMessage = message;
    setMessage("");
    sendMessage(currentMessage);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const text = `I want to plan a trip with the following details:
      Where from: ${formData.from}
      Where to: ${formData.to}
      Means of transport: ${formData.transport}
      Number of people: ${formData.people}
      From: ${formData.dateFrom} to ${formData.dateTo}
      Activity level: ${formData.activity}
      Population number: ${formData.population}
      Budget: ${formData.budget}
      Key attractions / points of interest: ${formData.attractions}`;
    sendMessage(text);

    const response = await fetch(`${API_BASE}/chat/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: 0,
        message: text,
      }),
    });

    if (!response.ok) {
      console.error("Server error", response.status);
      return;
    }

    const es = response.body
      ? new ReadableStream({
          async start(controller) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              const chunk = decoder.decode(value);
              console.log("Received chunk:", chunk);
            }
            controller.close();
          },
        })
      : null;
  };

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
  options={{
    closeBoxURL: "", // disables default close
    enableEventPropagation: true,
    pixelOffset: new window.google.maps.Size(-120, -50), // adjust if needed
  }}
>
  <div className="info-window" style={{ position: "relative" }}>
    {/* Custom close button */}
    <button
      className="info-close-btn"
      onClick={() => setSelectedTrip(null)}
    >
      ×
    </button>

    <h3>
      {selectedTrip.city.name}, {selectedTrip.trip.country}
    </h3>
    {selectedTrip.trip.description && <p>{selectedTrip.trip.description}</p>}
    {selectedTrip.trip.duration && <p><span>Duration:</span> {selectedTrip.trip.duration} days</p>}
    {selectedTrip.trip.budget && <p><span>Budget:</span> ${selectedTrip.trip.budget}</p>}
    {selectedTrip.trip.num_people && <p><span>People:</span> {selectedTrip.trip.num_people}</p>}
    {selectedTrip.trip.activity_level && <p><span>Activity:</span> {selectedTrip.trip.activity_level}</p>}
  </div>
</InfoBox>
              )}
            </GoogleMap>
          </LoadScript>
        </div>

        <div className="chat-form-wrapper">
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
              <button type="submit" className="chat-send-btn">
                Send
              </button>
            </form>
          </div>
          <div className="trip-form">
            <h3 className="trip-form-title">
              Travel sheet <FaSuitcase size={28} title="Trip Form" />
            </h3>
            <form onSubmit={handleFormSubmit} className="trip-form-fields">
              <input
                type="text"
                name="from"
                placeholder="Where from"
                value={formData.from}
                onChange={handleFormChange}
              />
              <input
                type="text"
                name="to"
                placeholder="Where to"
                value={formData.to}
                onChange={handleFormChange}
              />
              <input
                type="text"
                name="transport"
                placeholder="Prefered means of transport"
                value={formData.transport}
                onChange={handleFormChange}
              />
              <input
                type="number"
                name="people"
                placeholder="Number of people"
                value={formData.people}
                onChange={handleFormChange}
                min="1"
              />
              <label>Start date:</label>
              <input
                type="date"
                name="dateFrom"
                value={formData.dateFrom}
                onChange={handleFormChange}
              />
              <label>End date:</label>
              <input
                type="date"
                name="dateTo"
                value={formData.dateTo}
                onChange={handleFormChange}
              />
              <input
                type="text"
                name="activity"
                placeholder="Activity level"
                value={formData.activity}
                onChange={handleFormChange}
              />
              <input
                type="text"
                name="population"
                placeholder="Population level"
                value={formData.population}
                onChange={handleFormChange}
              />
              <input
                type="number"
                name="budget"
                placeholder="Budget"
                value={formData.budget}
                onChange={handleFormChange}
                min="0"
              />
              <textarea
                name="attractions"
                placeholder="Key attractions / points of interest"
                value={formData.attractions}
                onChange={handleFormChange}
              ></textarea>
              <button type="submit" className="chat-send-btn">
                Send
              </button>
            </form>
          </div>
        </div>
      </Layout>
    </>
  );
}

export default App;
