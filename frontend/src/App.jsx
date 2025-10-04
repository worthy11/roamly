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
        <Chat />
      </div>

      <div className={`slide-down-form ${isFormOpen ? "open" : ""}`}>
        <button className="close-form-btn" onClick={() => setIsFormOpen(false)}>
          ×
        </button>
        <Travel />
      </div>
    </Layout>
  );
}

export default App;
