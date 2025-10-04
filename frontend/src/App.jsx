import Layout from "./components/Layout";
import Chat from "./components/Chat";
import Map from "./components/Map";
import "./App.css";
import { useState, useEffect } from "react";
import { API_BASE } from "./config";

function App() {
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false); // nowy stan
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

  return (
    <Layout>
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
    Open ChatBot
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

    </Layout>
  );
}

export default App;