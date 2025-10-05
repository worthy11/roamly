import { useState } from "react";
import { FaSuitcase } from "react-icons/fa";
import "./TripForm.css";

function TripForm({ onSubmit, onClose }) {
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
    onSubmit(formData);
  };

  return (
    <div className="trip-form">
      <button className="close-form-btn-two" onClick={onClose}>
        ×
      </button>{" "}
      {/* Close button */}
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
        <select
          name="transport"
          value={formData.transport}
          onChange={handleFormChange}
        >
          <option value="">Select transport</option>
          <option value="plane">Plane ✈️</option>
          <option value="train">Transit 🚆</option>
          <option value="bus">Bus 🚌</option>
        </select>
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
          type="number"
          name="budget"
          placeholder="Budget"
          value={formData.budget}
          onChange={handleFormChange}
          min="0"
        />
        <select
          name="activity"
          value={formData.activity}
          onChange={handleFormChange}
        >
          <option value="">Select activity level</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <select
          name="population"
          value={formData.population}
          onChange={handleFormChange}
        >
          <option value="">Select population level</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
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
