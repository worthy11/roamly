// Simple markdown renderer utility
export const formatMarkdown = (text) => {
  if (!text) return '';
  
  return text
    // Bold text **text** -> <strong>text</strong>
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic text *text* -> <em>text</em>
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Headers ## text -> <h3>text</h3>
    .replace(/^## (.*$)/gim, '<h3>$1</h3>')
    // Headers ### text -> <h4>text</h4>
    .replace(/^### (.*$)/gim, '<h4>$1</h4>')
    // Headers #### text -> <h5>text</h5>
    .replace(/^#### (.*$)/gim, '<h5>$1</h5>')
    // Bullet points - text -> <li>text</li> (only if not already in a list)
    .replace(/^- (.*$)/gim, '<li>$1</li>')
    // Numbered lists 1. text -> <li>text</li>
    .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    // Wrap consecutive list items in ul/ol tags only when there are multiple items
    .replace(/(<li>.*<\/li>)(\s*<li>.*<\/li>)+/g, (match) => {
      // Check if it's a numbered list (contains digits)
      if (/\d+\./.test(match)) {
        return `<ol>${match}</ol>`;
      } else {
        return `<ul>${match}</ul>`;
      }
    })
    // Convert single list items to plain text
    .replace(/<li>(.*?)<\/li>(?!\s*<li>)/g, '• $1')
    // Line breaks (but preserve double line breaks for paragraphs)
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    // Wrap in paragraph tags
    .replace(/^(.*)$/, '<p>$1</p>')
    // Clean up empty paragraphs
    .replace(/<p><\/p>/g, '')
    .replace(/<p><br\/><\/p>/g, '');
};

// Markdown renderer component
export const MarkdownRenderer = ({ content }) => {
  if (!content) return null;
  
  const formattedContent = formatMarkdown(content);
  
  return (
    <div 
      dangerouslySetInnerHTML={{ __html: formattedContent }}
      style={{ lineHeight: '1.6' }}
    />
  );
};
