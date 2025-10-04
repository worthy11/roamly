import { MarkdownRenderer } from '../utils/markdownUtils.jsx';

const TripPlanBox = ({ type, title, content, icon }) => {
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
        return 'trip-plan-box';
    }
  };

  return (
    <div className={getBoxClassName()}>
      <div className="trip-plan-box-header">
        <h4>{icon} {title}</h4>
      </div>
      <div className="trip-plan-box-content">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  );
};

export default TripPlanBox;
