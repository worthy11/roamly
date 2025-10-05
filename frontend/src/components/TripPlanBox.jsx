import { useState } from "react";
import { MarkdownRenderer } from "../utils/markdownUtils.jsx";

const TripPlanBox = ({ type, title, content, icon, onSelectAttractions }) => {
  if (!content) return null;

  const getBoxClassName = () => {
    switch (type) {
      case 'transport':
        return 'trip-plan-box transport-box';
      case 'accommodation':
        return 'trip-plan-box accommodation-box';
      case 'plan':
        return 'trip-plan-box plan-box';
      case 'tips':
        return 'trip-plan-box tips-box';
      case 'risks':
        return 'trip-plan-box risks-box';
      default:
        return "trip-plan-box";
    }
  };

  let parsedContent = content;
  if (type === "plan" && typeof content === "string") {
    try {
      parsedContent = JSON.parse(content);
    } catch (err) {
      console.error("Failed to parse plan JSON:", err);
      return (
        <div className={getBoxClassName()}>
          <div className="trip-plan-box-header">
            <h4>
              {icon} {title}
            </h4>
          </div>
          <div className="trip-plan-box-content">
            <MarkdownRenderer content={content} />
          </div>
        </div>
      );
    }
  }

  const [expandedDay, setExpandedDay] = useState(null);

  const toggleDay = (dayNumber, attractions) => {
    const newDay = expandedDay === dayNumber ? null : dayNumber;
    setExpandedDay(newDay);
    if (newDay && onSelectAttractions && attractions) {
      onSelectAttractions(attractions);
      console.log(attractions);
    }
  };

  // --- Render structured plan ---
  if (type === "plan" && typeof parsedContent === "object") {
    const trip = parsedContent;

    return (
      <div className={getBoxClassName()}>
        <div className="trip-plan-box-header">
          <h4>
            {icon} {title}
          </h4>
        </div>

        <div className="trip-plan-box-content">
          <p>
            <strong>Destination:</strong> {trip.destination}
          </p>
          <p>
            <strong>Duration:</strong> {trip.duration_days} days
          </p>
          <p>
            <strong>Travel:</strong> {trip.travel}
          </p>
          <p>
            <strong>Accommodation:</strong> {trip.accommodation}
          </p>
          <p>
            <strong>Costs:</strong> {trip.costs}
          </p>

          <h5 className="daily-plan-header">Daily Plan</h5>
          {trip.daily_plan.map((day) => (
            <div key={day.day} className="daily-plan-day">
              <div
                className="daily-plan-header clickable"
                onClick={() => toggleDay(day.day, day.major_attractions)}
              >
                <strong>
                  Day {day.day}: {day.date}
                </strong>
                <p className="daily-plan-desc">{day.description}</p>
              </div>

              {expandedDay === day.day && (
                <div className="daily-plan-details">
                  {day.major_attractions?.length > 0 && (
                    <>
                      <ol>
                        {day.major_attractions.map((attr, i) => (
                          <li key={i}>
                            <strong>{attr.name}</strong> — {attr.time_of_day}
                            <br />
                          </li>
                        ))}
                      </ol>
                    </>
                  )}

                  {day.transport_info && (
                    <p>
                      <strong>Transport:</strong> {day.transport_info}
                    </p>
                  )}
                  {day.time_schedule && (
                    <p>
                      <strong>Schedule:</strong> {day.time_schedule}
                    </p>
                  )}
                  {day.notes && (
                    <p>
                      <strong>Notes:</strong> {day.notes}
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={getBoxClassName()}>
      <div className="trip-plan-box-header">
        <h4>
          {icon} {title}
        </h4>
      </div>
      <div className="trip-plan-box-content">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  );
};

export default TripPlanBox;
