import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Statistics.css';

function Statistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatistics();
    // Refresh stats every 10 seconds
    const interval = setInterval(fetchStatistics, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/statistics');
      if (response.data.success) {
        setStats(response.data.statistics);
      }
      setLoading(false);
    } catch (err) {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="statistics">Loading...</div>;
  }

  if (!stats) {
    return <div className="statistics">Unable to load statistics</div>;
  }

  return (
    <div className="statistics">
      <div className="stats-header">
        <h3>Usage Statistics</h3>
        <button className="refresh-button" onClick={fetchStatistics} title="Refresh">
          Refresh
        </button>
      </div>

      <div className="stat-card primary">
        <div className="stat-value">{stats.total_interactions || 0}</div>
        <div className="stat-label">Total Interactions</div>
      </div>

      {stats.by_mode && Object.entries(stats.by_mode).length > 0 ? (
        <>
          <div className="stat-card">
            <div className="stat-value">
              {stats.by_mode.strict || 0}
            </div>
            <div className="stat-label">Strict Mode</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">
              {stats.by_mode.friendly || 0}
            </div>
            <div className="stat-label">Friendly Mode</div>
          </div>

          <div className="stat-card">
            <div className="stat-value">
              {stats.by_mode.fallback || 0}
            </div>
            <div className="stat-label">Fallback Mode</div>
          </div>
        </>
      ) : (
        <div className="stat-card empty">
          <p>No interactions yet</p>
        </div>
      )}

      {stats.avg_response_length > 0 && (
        <div className="stat-card">
          <div className="stat-value">
            {Math.round(stats.avg_response_length)}
          </div>
          <div className="stat-label">Avg Response Length</div>
        </div>
      )}

      <div className="info-box">
        <p className="info-text">
          Statistics are updated every 10 seconds from server logs.
        </p>
      </div>
    </div>
  );
}

export default Statistics;
