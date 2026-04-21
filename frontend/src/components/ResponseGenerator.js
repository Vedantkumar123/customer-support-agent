import React, { useState } from 'react';
import axios from 'axios';
import './ResponseGenerator.css';
import DocumentViewer from './DocumentViewer';

function ResponseGenerator({ modes }) {
  const [query, setQuery] = useState('');
  const [selectedMode, setSelectedMode] = useState('friendly');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDocuments, setShowDocuments] = useState(false);

  const handleGenerateResponse = async () => {
    if (!query.trim()) {
      setError('Please enter a customer complaint');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await axios.post('http://localhost:5000/api/generate-response', {
        query: query,
        mode: selectedMode
      });

      if (result.data.success) {
        setResponse(result.data);
        setShowDocuments(false);
      } else {
        setError(result.data.error || 'Failed to generate response');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error connecting to backend server');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleGenerateResponse();
    }
  };

  const getCurrentModeConfig = () => {
    if (typeof modes === 'object' && modes[selectedMode]) {
      return modes[selectedMode];
    }
    return null;
  };

  const config = getCurrentModeConfig();

  return (
    <div className="response-generator">
      {/* Input Section */}
      <div className="input-section">
        <div className="section-header">
          <h2>Customer Complaint</h2>
          <span className="char-count">{query.length} / 1000</span>
        </div>

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value.substring(0, 1000))}
          onKeyPress={handleKeyPress}
          placeholder="Enter customer complaint here... (e.g., 'My product arrived late and damaged. Can I get a refund?')"
          className="query-input"
        />

        {/* Mode Selection */}
        <div className="mode-selection">
          <label>Support Mode</label>
          <div className="mode-options">
            {Object.keys(modes).map((modeKey) => (
              <button
                key={modeKey}
                className={`mode-button ${selectedMode === modeKey ? 'active' : ''}`}
                onClick={() => {
                  setSelectedMode(modeKey);
                  setResponse(null);
                }}
              >
                <span className="mode-name">
                  {modes[modeKey].name.replace(/_/g, ' ')}
                </span>
                <span className="mode-temp">
                  Temp: {modes[modeKey].temperature}
                </span>
              </button>
            ))}
          </div>
          {config && (
            <p className="mode-description">{config.description}</p>
          )}
        </div>

        {/* Error Message */}
        {error && <div className="error-message">{error}</div>}

        {/* Generate Button */}
        <button
          onClick={handleGenerateResponse}
          disabled={loading || !query.trim()}
          className="generate-button"
        >
          {loading ? (
            <>
              <span className="spinner"></span> Generating...
            </>
          ) : (
            'Generate Response'
          )}
        </button>
      </div>

      {/* Response Section */}
      {response && (
        <div className="response-section">
          <div className="section-header">
            <h2>AI-Generated Response</h2>
            <span className="mode-badge">{response.mode_used.toUpperCase()}</span>
          </div>

          {response.is_mock && (
            <div className="mock-notice">
              ℹ️ Using mock response (no real API key configured)
            </div>
          )}

          <div className="response-content">
            {response.response}
          </div>

          {/* Parameters Display */}
          <div className="parameters-box">
            <h4>LLM Parameters Used</h4>
            <div className="param-grid">
              <div className="param-item">
                <span className="param-label">Temperature</span>
                <span className="param-value">{response.parameters.temperature}</span>
              </div>
              <div className="param-item">
                <span className="param-label">Max Tokens</span>
                <span className="param-value">{response.parameters.max_tokens}</span>
              </div>
              <div className="param-item">
                <span className="param-label">Model</span>
                <span className="param-value">{response.model}</span>
              </div>
            </div>
          </div>

          {/* Retrieved Documents */}
          <div className="documents-section">
            <button
              className="toggle-docs-button"
              onClick={() => setShowDocuments(!showDocuments)}
            >
              {showDocuments ? '▼' : '▶'} Retrieved Documents ({response.retrieved_documents.length})
            </button>
            {showDocuments && (
              <DocumentViewer documents={response.retrieved_documents} />
            )}
          </div>

          {/* Copy Button */}
          <button
            className="copy-button"
            onClick={() => {
              navigator.clipboard.writeText(response.response);
              alert('Response copied to clipboard!');
            }}
          >
            Copy Response
          </button>
        </div>
      )}

      {/* Welcome Message */}
      {!response && !loading && (
        <div className="welcome-message">
          <h3>How it works:</h3>
          <ol>
            <li>Enter a customer complaint in the text area</li>
            <li>Select a support mode (Strict, Friendly, or Fallback)</li>
            <li>Click "Generate Response" to create an AI response</li>
            <li>View the response along with retrieved policy documents</li>
          </ol>
          <p className="example-queries">
            <strong>Example queries:</strong><br />
            "My order has been delayed for 10 days"<br />
            "I received a damaged product"<br />
            "Can I return this item after 10 days?"
          </p>
        </div>
      )}
    </div>
  );
}

export default ResponseGenerator;
