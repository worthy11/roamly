import Layout from "./components/Layout";
import './App.css'
import { MapContainer, TileLayer} from 'react-leaflet'
import 'leaflet/dist/leaflet.css';
import { useState } from "react";
import { BsRobot } from "react-icons/bs";

function App() {

  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);

  const handleSend = (e) => {
    e.preventDefault();
    if (message.trim() === "") return;
    setChat([...chat, { from: "user", text: message }]);
    setMessage("");
    
  };
  
  return (
    <>
      <Layout>
      <div className="map-wrapper">
        <MapContainer center={[20, 0]} zoom={2} className="custom-map">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
        </MapContainer>
      </div>
      <div className="chatbot-container">
          <h2 className="chatbot-title">Plan your next trip <BsRobot size={35} title="ChatBot" /></h2>
          <div className="chatbot-underline"></div>
          <div className="chat-window">
            {chat.length === 0 && <div className="chat-placeholder">No messages</div>}
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
              onChange={e => setMessage(e.target.value)}
              className="chat-input"
            />
            <button type="submit" className="chat-send-btn">Send</button>
          </form>
        </div>
      
      </Layout>
    </>
  )
}

export default App
