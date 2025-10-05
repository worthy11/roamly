import TripPlanBox from './TripPlanBox';
import TripPlanPDF from './TripPlanPDF';
import { pdf } from '@react-pdf/renderer';
import React from 'react';

const TripPlanContainer = ({ tripPlan, onSelectAttractions }) => {
  const { transport, accommodation, plan, tips, risks, isGenerating } = tripPlan;

  // Don't render if no content and not generating
  if (!isGenerating && !transport && !accommodation && !plan && !tips && !risks) {
    return null;
  }

  // Check if all trip plan boxes are rendered (not generating and all content exists)
  const allBoxesRendered = !isGenerating && transport && accommodation && plan && tips && risks;

  const handleDownloadPDF = async () => {
    try {
      console.log('Starting PDF generation...', tripPlan);
      
      // Create the PDF document
      const pdfElement = React.createElement(TripPlanPDF, { tripPlan });
      const pdfDoc = pdf(pdfElement);
      console.log('PDF document created');
      
      // Generate blob with proper UTF-8 support
      const blob = await pdfDoc.toBlob();
      console.log('PDF blob generated:', blob);
      
      // Create download link with proper encoding
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'trip-plan.pdf';
      link.setAttribute('type', 'application/pdf');
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      console.log('PDF download initiated');
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error generating PDF: ' + error.message);
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
              Download PDF
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
