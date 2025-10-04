import { useState } from 'react';
import { BsRobot } from "react-icons/bs";
import './Chat.css';
import { API_BASE } from "../config";
import TripForm from './TripForm';

function Chat() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [formOpen, setFormOpen] = useState(false); // nowy stan

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

  return (
    <div className="chatbot-container">
      <h2 className="chatbot-title">
        Plan your next trip <BsRobot size={35} title="ChatBot" />
      </h2>
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
          onChange={(e) => setMessage(e.target.value)}
          className="chat-input"
        />
        <button type="submit" className="chat-send-btn">Send</button>
        <button
          type="button"
          className="chat-send-btn open-form-btn"
          onClick={() => setFormOpen(!formOpen)}
        >
          Plan Trip
        </button>
      </form>

      <div className={`trip-form-wrapper ${formOpen ? 'open' : ''}`}>
        <TripForm onSubmit={sendMessage} />
      </div>
    </div>
  );
}

export default Chat;