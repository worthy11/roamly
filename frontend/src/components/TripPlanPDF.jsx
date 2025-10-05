import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font } from '@react-pdf/renderer';

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
    gap: 10,
  },
  box: {
    width: '48%',
    marginBottom: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#e6b474',
    borderStyle: 'solid',
    overflow: 'hidden',
  },
  boxHeader: {
    backgroundColor: '#e6b474',
    padding: 8,
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
    padding: 8,
    color: '#2d4238',
    fontSize: 9,
    lineHeight: 1.3,
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
  paragraph: {
    marginBottom: 4,
    lineHeight: 1.3,
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
    marginBottom: 4,
    marginTop: 6,
    color: '#2d4238',
    borderBottomWidth: 1,
    borderBottomColor: '#e6b474',
    borderBottomStyle: 'solid',
    paddingBottom: 1,
  },
  h4: {
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 3,
    marginTop: 4,
    color: '#2d4238',
  },
  h5: {
    fontSize: 9,
    fontWeight: 'bold',
    marginBottom: 2,
    marginTop: 3,
    color: '#2d4238',
  },
  list: {
    marginLeft: 8,
    marginBottom: 4,
  },
  listItem: {
    marginBottom: 2,
    paddingLeft: 3,
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

// Helper function to parse inline formatting (bold, italic)
const parseInlineFormatting = (text) => {
  if (!text) return text;
  
  // Split text by bold markers
  const parts = text.split(/(\*\*.*?\*\*)/);
  
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
  const { transport, accommodation, plan } = tripPlan;
  
  const renderContent = (content, type) => {
    const elements = parseContentForPDF(content);
    
    return elements.map((element, index) => {
      switch (element.type) {
        case 'h3':
          return (
            <Text key={index} style={styles.h3}>
              {element.text}
            </Text>
          );
        case 'h4':
          return (
            <Text key={index} style={styles.h4}>
              {element.text}
            </Text>
          );
        case 'h5':
          return (
            <Text key={index} style={styles.h5}>
              {element.text}
            </Text>
          );
        case 'listItem':
          return (
            <Text key={index} style={styles.listItem}>
              • {element.text}
            </Text>
          );
        case 'paragraph':
        default:
          return (
            <Text key={index} style={styles.paragraph}>
              {element.text}
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
                <Text style={styles.boxTitle}>🚗 Transportation</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(transport, 'transport')}
              </View>
            </View>
          )}
          
          {accommodation && (
            <View style={[styles.box, styles.accommodationBox]}>
              <View style={styles.boxHeader}>
                <Text style={styles.boxTitle}>🏨 Accommodation</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(accommodation, 'accommodation')}
              </View>
            </View>
          )}
          
          {plan && (
            <View style={[styles.box, styles.planBox]}>
              <View style={styles.boxHeader}>
                <Text style={styles.boxTitle}>🗓️ Detailed Plan</Text>
              </View>
              <View style={styles.boxContent}>
                {renderContent(plan, 'plan')}
              </View>
            </View>
          )}
        </View>
      </Page>
    </Document>
  );
};

export default TripPlanPDF;
