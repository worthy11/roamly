import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font } from '@react-pdf/renderer';

// Use default fonts with proper UTF-8 support
// The default Helvetica font in @react-pdf/renderer supports UTF-8 characters
// No need to register external fonts to avoid loading issues

// Define styles that match the website UI
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#ffffff',
    padding: 15,
    fontFamily: 'Helvetica',
  },
  header: {
    marginBottom: 15,
    paddingBottom: 8,
    borderBottomWidth: 2,
    borderBottomColor: '#e6b474',
    borderBottomStyle: 'solid',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2d4238',
    textAlign: 'center',
    marginBottom: 5,
  },
  content: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  box: {
    width: '48%',
    marginBottom: 4,
    backgroundColor: '#f8f9fa',
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#e6b474',
    borderStyle: 'solid',
    overflow: 'hidden',
  },
  boxHeader: {
    backgroundColor: '#e6b474',
    padding: 4,
    borderBottomWidth: 1,
    borderBottomColor: '#d7ab75',
    borderBottomStyle: 'solid',
  },
  boxTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#2d4238',
    textAlign: 'center',
  },
  boxContent: {
    padding: 4,
    color: '#2d4238',
    fontSize: 9,
    lineHeight: 1.1,
  },
  transportBox: {
    borderLeftWidth: 3,
    borderLeftColor: '#4CAF50',
    borderLeftStyle: 'solid',
  },
  accommodationBox: {
    borderLeftWidth: 3,
    borderLeftColor: '#2196F3',
    borderLeftStyle: 'solid',
  },
  planBox: {
    borderLeftWidth: 3,
    borderLeftColor: '#FF9800',
    borderLeftStyle: 'solid',
    width: '100%', // Full width for the plan box
  },
  tipsBox: {
    borderLeftWidth: 3,
    borderLeftColor: '#9C27B0',
    borderLeftStyle: 'solid',
  },
  risksBox: {
    borderLeftWidth: 3,
    borderLeftColor: '#F44336',
    borderLeftStyle: 'solid',
  },
  paragraph: {
    marginBottom: 1,
    lineHeight: 1.1,
  },
  strong: {
    fontWeight: 'bold',
    color: '#2d4238',
  },
  em: {
    fontStyle: 'italic',
    color: '#e6b474',
  },
  h3: {
    fontSize: 11,
    fontWeight: 'bold',
    marginBottom: 1,
    marginTop: 1,
    color: '#2d4238',
    borderBottomWidth: 1,
    borderBottomColor: '#e6b474',
    borderBottomStyle: 'solid',
    paddingBottom: 1,
    lineHeight: 1.1,
  },
  h4: {
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 0.5,
    marginTop: 1,
    color: '#2d4238',
    lineHeight: 1.1,
  },
  h5: {
    fontSize: 9,
    fontWeight: 'bold',
    marginBottom: 0.5,
    marginTop: 1,
    color: '#2d4238',
    lineHeight: 1.1,
  },
  list: {
    marginLeft: 6,
    marginBottom: 1,
    marginTop: 0.5,
  },
  listItem: {
    marginBottom: 0.5,
    paddingLeft: 2,
    lineHeight: 1.1,
  },
});

// Helper function to parse markdown-like content for PDF
const parseContentForPDF = (content) => {
  if (!content) return [];
  
  const lines = content.split('\n');
  const elements = [];
  let inList = false;
  let listItems = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Handle headers
    if (line.startsWith('## ')) {
      // Close any open list
      if (inList && listItems.length > 0) {
        elements.push({
          type: 'list',
          items: listItems,
        });
        listItems = [];
        inList = false;
      }
      elements.push({
        type: 'h3',
        text: line.substring(3),
      });
    } else if (line.startsWith('### ')) {
      // Close any open list
      if (inList && listItems.length > 0) {
        elements.push({
          type: 'list',
          items: listItems,
        });
        listItems = [];
        inList = false;
      }
      elements.push({
        type: 'h4',
        text: line.substring(4),
      });
    } else if (line.startsWith('#### ')) {
      // Close any open list
      if (inList && listItems.length > 0) {
        elements.push({
          type: 'list',
          items: listItems,
        });
        listItems = [];
        inList = false;
      }
      elements.push({
        type: 'h5',
        text: line.substring(5),
      });
    } 
    // Handle list items
    else if (line.startsWith('- ') || line.startsWith('* ')) {
      if (!inList) {
        inList = true;
        listItems = [];
      }
      listItems.push(line.substring(2));
    } else if (/^\d+\. /.test(line)) {
      if (!inList) {
        inList = true;
        listItems = [];
      }
      listItems.push(line.replace(/^\d+\. /, ''));
    } 
    // Handle regular paragraphs
    else if (line.length > 0) {
      // Close any open list
      if (inList && listItems.length > 0) {
        elements.push({
          type: 'list',
          items: listItems,
        });
        listItems = [];
        inList = false;
      }
      elements.push({
        type: 'paragraph',
        text: line,
      });
    } else if (line.length === 0) {
      // Close any open list on empty line
      if (inList && listItems.length > 0) {
        elements.push({
          type: 'list',
          items: listItems,
        });
        listItems = [];
        inList = false;
      }
    }
  }
  
  // Close any remaining list
  if (inList && listItems.length > 0) {
    elements.push({
      type: 'list',
      items: listItems,
    });
  }
  
  return elements;
};

// Helper function to parse and format JSON trip plan
const parseTripPlanJSON = (planContent) => {
  if (!planContent) return planContent;
  
  try {
    // Try to parse as JSON
    const parsed = JSON.parse(planContent);
    
    // If it's a valid JSON object, format it nicely
    if (typeof parsed === 'object' && parsed !== null) {
      let formatted = '';
      
      // Handle different trip plan structures
      if (parsed.destination) {
        formatted += `**Destination:** ${parsed.destination}\n\n`;
      }
      if (parsed.duration_days) {
        formatted += `**Duration:** ${parsed.duration_days}\n\n`;
      }
      if (parsed.travel) {
        formatted += `**Travel:** ${parsed.travel}\n\n`;
      }
      if (parsed.accommodation) {
        formatted += `**Accommodation:** ${parsed.accommodation}\n\n`;
      }
      if (parsed.costs) {
        formatted += `**Costs:** ${parsed.costs}\n\n`;
      }
      if (parsed.daily_plan && Array.isArray(parsed.daily_plan)) {
        formatted += `## Daily Itinerary\n\n`;
        parsed.daily_plan.forEach((day, index) => {
          formatted += `### Day ${day.day || index + 1}`;
          if (day.date) {
            formatted += ` - ${day.date}`;
          }
          formatted += `\n\n`;
          
          if (day.description) {
            formatted += `${day.description}\n\n`;
          }
          
          if (day.major_attractions && Array.isArray(day.major_attractions)) {
            formatted += `**Attractions:**\n`;
            day.major_attractions.forEach(attraction => {
              formatted += `- ${attraction.name}`;
              if (attraction.time_of_day) {
                formatted += ` (${attraction.time_of_day})`;
              }
              formatted += `\n`;
            });
            formatted += `\n`;
          }
          
          if (day.transport_info) {
            formatted += `**Transport:** ${day.transport_info}\n\n`;
          }
          
          if (day.time_schedule) {
            formatted += `**Schedule:** ${day.time_schedule}\n\n`;
          }
          
          if (day.notes) {
            formatted += `**Notes:** ${day.notes}\n\n`;
          }
        });
      }
      
      return formatted || planContent;
    }
    
    return planContent;
  } catch (e) {
    // If not valid JSON, return original content
    return planContent;
  }
};

// Helper function to parse inline formatting (bold, italic)
const parseInlineFormatting = (text) => {
  if (!text) return text;
  
  // Ensure text is properly encoded for Polish characters
  // NFC normalization ensures consistent character representation
  const normalizedText = text.normalize('NFC');
  
  // Split text by bold markers while preserving UTF-8 characters
  const parts = normalizedText.split(/(\*\*.*?\*\*)/);
  
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return {
        type: 'strong',
        text: part.slice(2, -2),
      };
    } else if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
      return {
        type: 'em',
        text: part.slice(1, -1),
      };
    } else {
      return {
        type: 'text',
        text: part,
      };
    }
  });
};

const TripPlanPDF = ({ tripPlan }) => {
  const { transport, accommodation, plan, tips, risks } = tripPlan;
  
  const renderText = (text) => {
    const formattedParts = parseInlineFormatting(text);
    
    return formattedParts.map((part, index) => {
      if (part.type === 'strong') {
        return (
          <Text key={index} style={styles.strong}>
            {part.text}
          </Text>
        );
      } else if (part.type === 'em') {
        return (
          <Text key={index} style={styles.em}>
            {part.text}
          </Text>
        );
      } else {
        return part.text;
      }
    });
  };

  const renderContent = (content, type) => {
    // Parse JSON for plan content
    const processedContent = type === 'plan' ? parseTripPlanJSON(content) : content;
    const elements = parseContentForPDF(processedContent);
    
    return elements.map((element, index) => {
      switch (element.type) {
        case 'h3':
          return (
            <Text key={index} style={styles.h3}>
              {renderText(element.text)}
            </Text>
          );
        case 'h4':
          return (
            <Text key={index} style={styles.h4}>
              {renderText(element.text)}
            </Text>
          );
        case 'h5':
          return (
            <Text key={index} style={styles.h5}>
              {renderText(element.text)}
            </Text>
          );
        case 'list':
          return (
            <View key={index} style={styles.list}>
              {element.items.map((item, itemIndex) => (
                <Text key={itemIndex} style={styles.listItem}>
                  • {renderText(item)}
                </Text>
              ))}
            </View>
          );
        case 'paragraph':
        default:
          return (
            <Text key={index} style={styles.paragraph}>
              {renderText(element.text)}
            </Text>
          );
      }
    });
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.title}>Your Trip Plan</Text>
        </View>
        
        <View style={styles.content}>
          {transport && (
            <View style={[styles.box, styles.transportBox]}>
              <View style={styles.boxHeader}>
                <Text style={styles.boxTitle}>Transportation</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(transport, 'transport')}
              </View>
            </View>
          )}
          
          {accommodation && (
            <View style={[styles.box, styles.accommodationBox]}>
              <View style={styles.boxHeader}>
                <Text style={styles.boxTitle}>Accommodation</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(accommodation, 'accommodation')}
              </View>
            </View>
          )}
          
          {plan && (
            <View style={[styles.box, styles.planBox]}>
              <View style={styles.boxHeader}>
                <Text style={styles.boxTitle}>Detailed Plan</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(plan, 'plan')}
              </View>
            </View>
          )}
          
          {tips && (
            <View style={[styles.box, styles.tipsBox]}>
              <View style={styles.boxHeader}>
                <Text style={styles.boxTitle}>Travel Tips</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(tips, 'tips')}
              </View>
            </View>
          )}
          
          {risks && (
            <View style={[styles.box, styles.risksBox]}>
              <View style={styles.boxHeader}>
                <Text style={styles.boxTitle}>Important Risks & Considerations</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(risks, 'risks')}
              </View>
            </View>
          )}
        </View>
      </Page>
    </Document>
  );
};

export default TripPlanPDF;
