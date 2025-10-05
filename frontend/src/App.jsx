import Layout from "./components/Layout";
import Chat from "./components/Chat";
import Map from "./components/Map";
import Navbar from "./components/Navbar";
import Travel from "./pages/Travels";
import "./App.css";
import { useState, useEffect } from "react";
import { API_BASE } from "./config";
import { BsRobot } from "react-icons/bs";

function App() {
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedAttractions, setSelectedAttractions] = useState([]);
  const [selectedCoordinates, setSelectedCoordinates] = useState(null);
  const [chatMessage, setChatMessage] = useState(null);

  const handleAttractionSelect = (attractions) => {
    setSelectedAttractions(attractions);
  };

  const handleMapClick = (coordinates) => {
    setSelectedCoordinates(coordinates);
  };

  const handleLearnMore = (trip) => {
    const message = `Tell me more about "${trip.title}" and recommend similar trips.`;

    // Set the message to be sent to chat and open the chat
    setChatMessage(message);
    setIsChatOpen(true);
  };

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

  const handleChatClose = () => {
    setIsChatOpen(false);

    setIsFormOpen(false);
  };

  return (
    <Layout>
      <Navbar onOpenForm={() => setIsFormOpen(true)} />

      <Map
        trips={trips}
        selectedTrip={selectedTrip}
        setSelectedTrip={setSelectedTrip}
        selectedAttractions={selectedAttractions}
        onMapClick={handleMapClick}
        onLearnMore={handleLearnMore}
      />

      {!isChatOpen && (
        <button
          className="open-chatbot-btn"
          onClick={() => setIsChatOpen(true)}
        >
          <span style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            Open ChatBot <BsRobot size={25} />
          </span>
        </button>
      )}

      <div className={`chat-form-wrapper ${isChatOpen ? "open" : ""}`}>
        <button
          className="close-chatbot-btn"
          onClick={() => setIsChatOpen(false)}
        >
          X
        </button>
        <Chat
          onSelectAttractions={handleAttractionSelect}
          initialMessage={chatMessage}
          onMessageSent={() => setChatMessage(null)}
        />
      </div>

      <div className={`slide-down-form ${isFormOpen ? "open" : ""}`}>
        <button className="close-form-btn" onClick={() => setIsFormOpen(false)}>
          ×
        </button>
        <Travel
          selectedCoordinates={selectedCoordinates}
          onCoordinatesUsed={() => setSelectedCoordinates(null)}
        />
      </div>
    </Layout>
  );
}

export default App;
