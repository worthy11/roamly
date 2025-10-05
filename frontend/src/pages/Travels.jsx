import Layout from "../components/Layout";
import { useState, useEffect } from "react";
import { API_BASE } from "../config";
import styles from "./Travels.module.css";

function Travel({ selectedCoordinates, onCoordinatesUsed }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState("");
  const [numPeople, setNumPeople] = useState("");
  const [activityLevel, setActivityLevel] = useState("");
  const [budget, setBudget] = useState("");
  const [cities, setCities] = useState("");
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");

  // Update coordinates when selectedCoordinates changes
  useEffect(() => {
    if (selectedCoordinates) {
      setLat(selectedCoordinates.lat.toFixed(6));
      setLng(selectedCoordinates.lng.toFixed(6));
      // Call the callback to clear the coordinates after using them
      if (onCoordinatesUsed) {
        onCoordinatesUsed();
      }
    }
  }, [selectedCoordinates, onCoordinatesUsed]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      title,
      description,
      duration: parseInt(duration),
      num_people: parseInt(numPeople),
      activity_level: activityLevel,
      budget: parseFloat(budget),
      cities: cities, // Keep as comma-separated string
      lat: lat ? parseFloat(lat) : null,
      lng: lng ? parseFloat(lng) : null,
    };

    const res = await fetch(`${API_BASE}/trips/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    console.log("Created trip:", data);
    setTitle("");
    setDescription("");
    setDuration("");
    setNumPeople("");
    setActivityLevel("");
    setBudget("");
    setCities("");
    setLat("");
    setLng("");
  };

  return (
    <div className={styles.tripForm}>
      <h1 className={styles.tripFormTitle}>Create a new Trip</h1>
      <form className={styles.tripFormFields} onSubmit={handleSubmit}>
        <input
          placeholder="Trip Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          type="number"
          placeholder="Duration (days)"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          min="1"
        />
        <input
          type="number"
          placeholder="Number of People"
          value={numPeople}
          onChange={(e) => setNumPeople(e.target.value)}
          min="1"
        />
        <input
          placeholder="Activity Level"
          value={activityLevel}
          onChange={(e) => setActivityLevel(e.target.value)}
        />
        <input
          type="number"
          placeholder="Budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          min="1"
        />
        <input
          placeholder="Cities (comma separated)"
          value={cities}
          onChange={(e) => setCities(e.target.value)}
        />
        <input
          type="number"
          step="any"
          placeholder="Latitude (optional)"
          value={lat}
          onChange={(e) => setLat(e.target.value)}
        />
        <input
          type="number"
          step="any"
          placeholder="Longitude (optional)"
          value={lng}
          onChange={(e) => setLng(e.target.value)}
        />
        <button type="submit">Create Trip</button>
      </form>
    </div>
  );
}

export default Travel;
