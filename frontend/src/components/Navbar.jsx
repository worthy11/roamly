import { Link } from "react-router-dom";
import { AiFillHome } from "react-icons/ai";
import { FaPlaneDeparture } from "react-icons/fa";
import { BsRobot } from "react-icons/bs";

import "./Navbar.css";

function Navbar() {
  return (
    <nav className="navbar">
      <span className="navbar-title">Roamly</span>
      <div className="navbar-links">
        <Link to="/"><AiFillHome size={30} title="Home" /></Link>
        <Link to="/travels"><FaPlaneDeparture size={30} title="Travels" /></Link>
        <Link to="/chat"><BsRobot size={30} title="ChatBot" /></Link>
      </div>
    </nav>
  );
}

export default Navbar;