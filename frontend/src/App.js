import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import ResponseGenerator from './components/ResponseGenerator';
import Header from './components/Header';
import Statistics from './components/Statistics';

function App() {
  const [modes, setModes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch available modes on component mount
    fetchModes();
  }, []);

  const fetchModes = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/modes');
      if (response.data.success) {
        setModes(response.data.modes);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to load modes. Make sure the backend server is running on http://localhost:5000');
      setLoading(false);
      // Set default modes if API fails
      setModes({
        strict: {
          name: 'STRICT_POLICY',
          value: 'strict',
          description: 'Strict Policy Mode - Deterministic, policy-focused responses',
          temperature: 0.2,
          max_tokens: 150
        },
        friendly: {
          name: 'FRIENDLY',
          value: 'friendly',
          description: 'Friendly Mode - Empathetic, natural, friendly responses',
          temperature: 0.7,
          max_tokens: 200
        },
        fallback: {
          name: 'FALLBACK',
          value: 'fallback',
          description: 'Fallback Mode - No matching policy found',
          temperature: 0.5,
          max_tokens: 100
        }
      });
    }
  };

  if (loading && !modes) {
    return (
      <div className="app">
        <div className="loading">Loading application...</div>
      </div>
    );
  }

  return (
    <div className="app">
      <Header />
      <div className="container">
        {error && <div className="error-banner">{error}</div>}
        <div className="main-content">
          <div className="left-column">
            <ResponseGenerator modes={modes} />
          </div>
          <div className="right-column">
            <Statistics />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
