import TripPlanBox from './TripPlanBox';
import TripPlanPDF from './TripPlanPDF';
import { pdf } from '@react-pdf/renderer';

const TripPlanContainer = ({ tripPlan }) => {
  const { transport, accommodation, plan, isGenerating } = tripPlan;

  // Don't render if no content and not generating
  if (!isGenerating && !transport && !accommodation && !plan) {
    return null;
  }

  // Check if all trip plan boxes are rendered (not generating and all content exists)
  const allBoxesRendered = !isGenerating && transport && accommodation && plan;

  const handleDownloadPDF = async () => {
    try {
      const blob = await pdf(<TripPlanPDF tripPlan={tripPlan} />).toBlob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'trip-plan.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  return (
    <div className="trip-plan-container">
      <div className="trip-plan-header">
        <h3>Your Trip Plan</h3>
        <div className="trip-plan-header-controls">
          {isGenerating && (
            <div className="trip-plan-loading">
              <div className="loading-spinner"></div>
              <span>Generating your trip...</span>
            </div>
          )}
          {allBoxesRendered && (
            <button 
              className="download-pdf-btn"
              onClick={handleDownloadPDF}
              title="Download PDF"
            >
              📄 Download PDF
            </button>
          )}
        </div>
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
      </div>
    </div>
  );
};

export default TripPlanContainer;
