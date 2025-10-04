import Layout from "../components/Layout";
import { useState } from "react";
import { API_BASE } from "../config";
import "./Travels.css";

function Travel() {
  const [country, setCountry] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState(1);
  const [numPeople, setNumPeople] = useState(1);
  const [activityLevel, setActivityLevel] = useState("");
  const [budget, setBudget] = useState(1000);
  const [cities, setCities] = useState("");

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
  };

  return (
    <Layout>
      <div className="trip-form">
        <h1 className="trip-form-title">Create a new Trip</h1>
        <form className="trip-form-fields" onSubmit={handleSubmit}>
          <input placeholder="Country" value={country} onChange={e => setCountry(e.target.value)} required />
          <input placeholder="Description" value={description} onChange={e => setDescription(e.target.value)} />
          <input type="number" placeholder="Duration (days)" value={duration} onChange={e => setDuration(e.target.value)} />
          <input type="number" placeholder="Number of People" value={numPeople} onChange={e => setNumPeople(e.target.value)} />
          <input placeholder="Activity Level" value={activityLevel} onChange={e => setActivityLevel(e.target.value)} />
          <input type="number" placeholder="Budget" value={budget} onChange={e => setBudget(e.target.value)} />
          <input placeholder="Cities (comma separated)" value={cities} onChange={e => setCities(e.target.value)} />
          <button type="submit">Create Trip</button>
        </form>
      </div>
    </Layout>
  );
}

export default Travel;
