import { useState } from 'react';
import { BsRobot } from "react-icons/bs";
import './Chat.css';
import { API_BASE } from "../config";
import TripForm from './TripForm';
import TripPlanContainer from './TripPlanContainer';

function Chat() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [formOpen, setFormOpen] = useState(false);
  const [tripPlan, setTripPlan] = useState({
    transport: '',
    accommodation: '',
    plan: '',
    tips: '',
    risks: '',
    isGenerating: false
  });

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

  const handleFormSubmit = async (formData) => {

    setFormOpen(false);

    const tripQuery = `I want to plan a trip with the following details:
- From: ${formData.from}
- To: ${formData.to}
- Preferred transport: ${formData.transport || 'any'}
- Number of people: ${formData.people}
- Travel dates: ${formData.dateFrom} to ${formData.dateTo}
- Activity level: ${formData.activity || 'moderate'}
- Preferred population: ${formData.population || 'any'}
- Budget: ${formData.budget ? `$${formData.budget}` : 'flexible'}
- Key attractions/interests: ${formData.attractions || 'general sightseeing'}`;

    const userMessage = { 
      from: "user", 
      text: `Planning a trip from ${formData.from} to ${formData.to}...` 
    };
    setChat((prev) => [...prev, userMessage]);

    setTripPlan({
      transport: '',
      accommodation: '',
      plan: '',
      tips: '',
      risks: '',
      isGenerating: true
    });

    try {
      const response = await fetch(`${API_BASE}/chat/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 0,
          message: tripQuery,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              setTripPlan(prev => ({ ...prev, isGenerating: false }));
              continue;
            }

            try {
              const parsed = JSON.parse(data);
              const { stage, result } = parsed;
              
              const extractOutput = (agentResult) => {
                if (typeof agentResult === 'string') {
                  return agentResult;
                }
                if (agentResult && typeof agentResult === 'object') {
                 
                  if (agentResult.output) {
                    return agentResult.output;
                  }
                  return JSON.stringify(agentResult);
                }
                return String(agentResult);
              };
              
              const outputText = extractOutput(result);
              
              if (stage === 'transport') {
                setTripPlan(prev => ({ ...prev, transport: outputText }));
              } else if (stage === 'accommodation') {
                setTripPlan(prev => ({ ...prev, accommodation: outputText }));
              } else if (stage === 'plan') {
                setTripPlan(prev => ({ ...prev, plan: outputText }));
              } else if (stage === 'tips') {
                setTripPlan(prev => ({ ...prev, tips: outputText }));
              } else if (stage === 'risks') {
                setTripPlan(prev => ({ ...prev, risks: outputText }));
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Error generating trip:", error);
      setTripPlan(prev => ({ ...prev, isGenerating: false }));
      setChat((prev) => [
        ...prev,
        { from: "bot", text: "Error generating trip: " + error.message },
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
        
        <TripPlanContainer tripPlan={tripPlan} />
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
        <TripForm onSubmit={handleFormSubmit} />
      </div>
    </div>
  );
}

export default Chat;