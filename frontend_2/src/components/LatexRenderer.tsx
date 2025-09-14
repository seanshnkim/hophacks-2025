import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

interface LatexRendererProps {
  content: string;
  displayMode?: boolean;
}

const LatexRenderer: React.FC<LatexRendererProps> = ({ content, displayMode = false }) => {
  // Extract LaTeX expressions from the content
  const renderContent = (text: string) => {
    // Split by LaTeX delimiters and process each part
    const parts = text.split(/(\$\$.*?\$\$|\$.*?\$)/g);
    
    return parts.map((part, index) => {
      // Check if this part is a LaTeX expression
      if (part.startsWith('$$') && part.endsWith('$$')) {
        // Block math (display mode)
        const latex = part.slice(2, -2).trim();
        return (
          <BlockMath key={index} math={latex} />
        );
      } else if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
        // Inline math
        const latex = part.slice(1, -1).trim();
        return (
          <InlineMath key={index} math={latex} />
        );
      } else {
        // Regular text
        return <span key={index}>{part}</span>;
      }
    });
  };

  if (displayMode) {
    // For display mode, render the entire content as a block
    return (
      <div style={{ textAlign: 'center', margin: '16px 0' }}>
        <BlockMath math={content} />
      </div>
    );
  }

  return <span>{renderContent(content)}</span>;
};

export default LatexRenderer;
