import { useState } from 'react';
import { FaSuitcase } from "react-icons/fa";
import './TripForm.css';

function TripForm({ onSubmit }) {
  const [formData, setFormData] = useState({
    from: "",
    to: "",
    transport: "",
    people: "",
    dateFrom: "",
    dateTo: "",
    activity: "",
    population: "",
    budget: "",
    attractions: "",
  });

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    const text = `I want to plan a trip with the following details:
Where from: ${formData.from}
Where to: ${formData.to}
Means of transport: ${formData.transport}
Number of people: ${formData.people}
From: ${formData.dateFrom} to ${formData.dateTo}
Activity level: ${formData.activity}
Population number: ${formData.population}
Budget: ${formData.budget}
Key attractions / points of interest: ${formData.attractions}`;
    onSubmit(text);
  };

  return (
    <div className="trip-form">
      <h3 className="trip-form-title">
        Travel sheet <FaSuitcase size={28} title="Trip Form" />
      </h3>
      <form onSubmit={handleFormSubmit} className="trip-form-fields">
        <input
          type="text"
          name="from"
          placeholder="Where from"
          value={formData.from}
          onChange={handleFormChange}
        />
        <input
          type="text"
          name="to"
          placeholder="Where to"
          value={formData.to}
          onChange={handleFormChange}
        />
        <input
          type="text"
          name="transport"
          placeholder="Prefered means of transport"
          value={formData.transport}
          onChange={handleFormChange}
        />
        <input
          type="number"
          name="people"
          placeholder="Number of people"
          value={formData.people}
          onChange={handleFormChange}
          min="1"
        />
        <label>Start date:</label>
        <input
          type="date"
          name="dateFrom"
          value={formData.dateFrom}
          onChange={handleFormChange}
        />
        <label>End date:</label>
        <input
          type="date"
          name="dateTo"
          value={formData.dateTo}
          onChange={handleFormChange}
        />
        <input
          type="text"
          name="activity"
          placeholder="Activity level"
          value={formData.activity}
          onChange={handleFormChange}
        />
        <input
          type="text"
          name="population"
          placeholder="Population level"
          value={formData.population}
          onChange={handleFormChange}
        />
        <input
          type="number"
          name="budget"
          placeholder="Budget"
          value={formData.budget}
          onChange={handleFormChange}
          min="0"
        />
        <textarea
          name="attractions"
          placeholder="Key attractions / points of interest"
          value={formData.attractions}
          onChange={handleFormChange}
        ></textarea>
        <button type="submit" className="trip-form-submit">
          Send
        </button>
      </form>
    </div>
  );
}

export default TripForm;