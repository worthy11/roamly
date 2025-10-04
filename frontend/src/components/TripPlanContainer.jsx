import TripPlanBox from './TripPlanBox';

const TripPlanContainer = ({ tripPlan }) => {
  const { transport, accommodation, plan, tips, risks, isGenerating } = tripPlan;

  // Don't render if no content and not generating
  if (!isGenerating && !transport && !accommodation && !plan && !tips && !risks) {
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
        />
        
        <TripPlanBox
          type="accommodation"
          title="Accommodation"
          content={accommodation}
          icon="🏨"
        />
        
        <TripPlanBox
          type="plan"
          title="Detailed Plan"
          content={plan}
          icon="🗓️"
        />
        
        <TripPlanBox
          type="tips"
          title="Travel Tips"
          content={tips}
          icon="💡"
        />
        
        <TripPlanBox
          type="risks"
          title="Safety & Risks"
          content={risks}
          icon="⚠️"
        />
      </div>
    </div>
  );
};

export default TripPlanContainer;
