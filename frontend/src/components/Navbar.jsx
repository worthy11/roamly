import { useState } from "react";
import { AiFillHome, AiFillQuestionCircle } from "react-icons/ai";
import { Link } from "react-router-dom";

import "./Navbar.css";

function Navbar({ onOpenForm }) {
  const [showInfo, setShowInfo] = useState(false);

  const handleInfoClick = () => {
    setShowInfo(true);
  };

  const closeInfo = () => {
    setShowInfo(false);
  };

  return (
    <nav className="navbar">
      <span className="navbar-title">Roamly</span>
      <div className="navbar-links">
        <Link to="/"><AiFillHome size={30} title="Home" /></Link>
        <button onClick={handleInfoClick} className="icon-button">
          <AiFillQuestionCircle size={30} title="About Us" />
        </button>

        <button 
          onClick={onOpenForm} 
          className="button-navbar"
        >
          Add a new trip
        </button>
      </div>

      {showInfo && (
        <div className="info-modal">
          <div className="info-content">
            <h2>How Roamly works</h2>
            <p>
              Roamly allows you to track your travels, add new trips, and explore other users' adventures.
            </p>
            <button className="button-info" onClick={closeInfo}>Close</button>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
