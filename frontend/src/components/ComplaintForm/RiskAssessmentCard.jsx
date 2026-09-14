import React from 'react';
import './RiskAssessmentCard.css';

export default function RiskAssessmentCard({ riskAssessment }) {
  const hasSeverity = !!riskAssessment?.severity;
  const hasAnyData = hasSeverity || riskAssessment?.suggestedNextAction || riskAssessment?.initialRiskAssessment;

  const getSeverityClass = (severity) => {
    switch ((severity || '').toLowerCase()) {
      case 'critical': return 'severity-critical';
      case 'major': return 'severity-major';
      case 'minor': return 'severity-minor';
      default: return '';
    }
  };

  return (
    <div className={`risk-card ${hasAnyData ? 'risk-card-active' : ''}`}>
      <div className="risk-card-header">
        <div className="risk-card-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 12l2 2 4-4" />
            <circle cx="12" cy="12" r="10" />
          </svg>
        </div>
        <span className="risk-card-title">AI Copilot Risk Assessment</span>
      </div>

      {hasAnyData ? (
        <div className="risk-card-content">
          <div className="risk-row">
            <div className="risk-item">
              <span className="risk-label">Severity (Suggested)</span>
              <span className={`risk-severity-badge ${getSeverityClass(riskAssessment.severity)}`}>
                {riskAssessment.severity || '—'}
              </span>
            </div>
            <div className="risk-item">
              <span className="risk-label">Suggested Next Action</span>
              <span className="risk-value">{riskAssessment.suggestedNextAction || '—'}</span>
            </div>
          </div>

          {riskAssessment.initialRiskAssessment && (
            <div className="risk-item full">
              <span className="risk-label">Initial Risk Assessment</span>
              <p className="risk-narrative">{riskAssessment.initialRiskAssessment}</p>
            </div>
          )}

          {riskAssessment.rootCauseRecommendation && (
            <div className="risk-item full">
              <span className="risk-label">🔍 Root Cause Recommendation</span>
              <p className="risk-narrative">{riskAssessment.rootCauseRecommendation}</p>
            </div>
          )}

          {riskAssessment.capaRecommendation && (
            <div className="risk-item full">
              <span className="risk-label">🛠️ CAPA Recommendation</span>
              <p className="risk-narrative">{riskAssessment.capaRecommendation}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="risk-card-empty">
          <p>Risk assessment will appear here after AI processes a complaint.</p>
        </div>
      )}
    </div>
  );
}
