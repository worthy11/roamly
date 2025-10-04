import Layout from "../components/Layout";
import { useState } from "react";
import { API_BASE } from "../config";
import styles from "./Travels.module.css";

function Travel() {
  const [country, setCountry] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState("");
  const [numPeople, setNumPeople] = useState("");
  const [activityLevel, setActivityLevel] = useState("");
  const [budget, setBudget] = useState("");
  const [cities, setCities] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const cityList = cities.split(",").map(c => c.trim());

    const payload = {
      country,
      description,
      duration: parseInt(duration),
      num_people: parseInt(numPeople),
      activity_level: activityLevel,
      budget: parseFloat(budget),
      cities: cityList
    };

    const res = await fetch(`${API_BASE}/trips/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    console.log("Created trip:", data);
      setCountry("");
      setDescription("");
      setDuration("");
      setNumPeople("");
      setActivityLevel("");
      setBudget("");
      setCities("");
  };



  return (
      <div className={styles.tripForm}>
        <h1 className={styles.tripFormTitle}>Create a new Trip</h1>
        <form className={styles.tripFormFields} onSubmit={handleSubmit}>
          <input placeholder="Country" value={country} onChange={e => setCountry(e.target.value)} required />
          <input placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} />
          <input type="number" placeholder="Duration (days)" value={duration} onChange={e => setDuration(e.target.value)} min="1" />
          <input type="number" placeholder="Number of People" value={numPeople} onChange={e => setNumPeople(e.target.value)} min="1" />
          <input placeholder="Activity Level" value={activityLevel} onChange={e => setActivityLevel(e.target.value)} />
          <input type="number" placeholder="Budget" value={budget} onChange={e => setBudget(e.target.value)} min="1"/>
          <input placeholder="Cities (comma separated)" value={cities} onChange={e => setCities(e.target.value)} />
          <button type="submit">Create Trip</button>
        </form>
      </div>
  );
}

export default Travel;
