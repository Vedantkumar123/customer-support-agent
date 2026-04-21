import React from 'react';
import './DocumentViewer.css';

function DocumentViewer({ documents }) {
  return (
    <div className="document-viewer">
      {documents.map((doc, index) => (
        <div key={index} className="document-item">
          <div className="document-header">
            <h4 className="document-title">{doc.title}</h4>
            <span className="bm25-score">Similarity: {doc.score.toFixed(4)}</span>
          </div>
          <div className="document-content">
            Policy ID: {doc.id}
          </div>
        </div>
      ))}
    </div>
  );
}

export default DocumentViewer;
