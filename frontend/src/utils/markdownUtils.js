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
    // Bullet points - text -> <li>text</li>
    .replace(/^- (.*$)/gim, '<li>$1</li>')
    // Numbered lists 1. text -> <li>text</li>
    .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    // Line breaks
    .replace(/\n/g, '<br/>');
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
