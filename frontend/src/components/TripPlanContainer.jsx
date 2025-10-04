import TripPlanBox from "./TripPlanBox";

const TripPlanContainer = ({ tripPlan, onSelectAttractions }) => {
  const { transport, accommodation, plan, isGenerating } = tripPlan;

  // Don't render if no content and not generating
  if (!isGenerating && !transport && !accommodation && !plan) {
    return null;
  }

  return (
    <div className="trip-plan-container">
      <div className="trip-plan-header">
        <h3>Your Trip Plan</h3>
        {isGenerating && (
          <div className="trip-plan-loading">
            <div className="loading-spinner"></div>
            <span>Generating your trip...</span>
          </div>
        )}
      </div>

      <div className="trip-plan-content">
        <TripPlanBox
          type="transport"
          title="Transportation"
          content={transport}
          icon="🚗"
          onSelectAttractions={onSelectAttractions}
        />

        <TripPlanBox
          type="accommodation"
          title="Accommodation"
          content={accommodation}
          icon="🏨"
          onSelectAttractions={onSelectAttractions}
        />

        <TripPlanBox
          type="plan"
          title="Detailed Plan"
          content={plan}
          icon="🗓️"
          onSelectAttractions={onSelectAttractions}
        />
      </div>
    </div>
  );
};

export default TripPlanContainer;
