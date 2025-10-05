import { useState } from "react";
import { AiFillHome, AiFillQuestionCircle } from "react-icons/ai";
import { Link } from "react-router-dom";

import "./Navbar.css";

function Navbar({ onOpenForm }) {
  const [showInfo, setShowInfo] = useState(false);

  return (
    <nav className="navbar">
      <span className="navbar-title">Roamly.ai</span>
      <div className="navbar-links">
        <Link to="/">
          <AiFillHome size={30} title="Home" />
        </Link>
        <button onClick={() => setShowInfo(true)} className="icon-button">
          <AiFillQuestionCircle size={30} title="About Us" />
        </button>
        <button className="button-navbar" onClick={onOpenForm}>
          Add new trip
        </button>
      </div>

      {showInfo && (
        <div className="info-modal">
          <div className="info-content">
            <button
              className="close-info-btn"
              onClick={() => setShowInfo(false)}
            >
              ×
            </button>
            <h2>Welcome to Roamly!</h2>
            <p>
              Roamly is your personal travel companion that makes planning and
              enjoying trips <strong>stress-free, safe, and worry-free</strong>.
            </p>
            <ul>
              <li>
                🗺️ Plan your trips directly in a chat interface – simple and
                interactive.
              </li>
              <li>
                👥 Explore trips shared by other users and get inspiration for
                your next adventure.
              </li>
              <li>
                🌴 Enjoy peaceful, safe, and worry-free vacations without stress
                or uncertainty.
              </li>
            </ul>
            <p>
              With Roamly, travel planning becomes easy, fun, and completely
              tailored to your needs.
            </p>
            <p style={{ marginTop: "10px", fontWeight: "bold" }}>
              💬 Click the chat in the bottom right corner to start your next
              adventure!
            </p>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
