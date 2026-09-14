import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateSingleField } from '../../store/complaintSlice';
import RiskAssessmentCard from './RiskAssessmentCard';
import StatusBadge from '../common/StatusBadge';
import api from '../../services/api';
import './ComplaintForm.css';

const SITE_BLOCK_OPTIONS = [
  '', 'Manufacturing', 'Packaging', 'Quality Control', 'Warehouse', 'R&D', 'API Production',
];

export default function ComplaintForm({ onCommit }) {
  const dispatch = useDispatch();
  const { formData, riskAssessment, status, isLoading, animatingFields, committedId } = useSelector(
    (state) => state.complaint
  );
  const [commitLoading, setCommitLoading] = useState(false);
  const [commitSuccess, setCommitSuccess] = useState(false);

  // Clear animation classes after animation completes
  useEffect(() => {
    if (animatingFields.length > 0) {
      const timer = setTimeout(() => {
        // Animation ends, fields stay populated
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [animatingFields]);

  const handleFieldChange = (field, value) => {
    dispatch(updateSingleField({ field, value }));
  };

  const handleCommit = async () => {
    setCommitLoading(true);
    try {
      const payload = {
        form_data: {
          complaint_source: formData.complaintSource || null,
          customer_name: formData.customerName || null,
          product_name: formData.productName || null,
          product_strength: formData.productStrength || null,
          batch_lot_number: formData.batchLotNumber || null,
          affected_quantity: formData.affectedQuantity || null,
          manufacturing_date: formData.manufacturingDate || null,
          expiry_date: formData.expiryDate || null,
          originating_site_block: formData.originatingSiteBlock || null,
          impacted_npm: formData.impactedNPM || null,
          complaint_category: formData.complaintCategory || null,
          complaint_description: formData.complaintDescription || null,
        },
        risk_assessment: {
          severity: riskAssessment.severity || null,
          suggested_next_action: riskAssessment.suggestedNextAction || null,
          initial_risk_assessment: riskAssessment.initialRiskAssessment || null,
          root_cause_recommendation: riskAssessment.rootCauseRecommendation || null,
          capa_recommendation: riskAssessment.capaRecommendation || null,
        },
      };
      const response = await api.post('/api/complaints/', payload);
      setCommitSuccess(true);
      if (onCommit) onCommit(response.data);
    } catch (error) {
      console.error('Commit error:', error);
      alert('Failed to commit complaint. Please try again.');
    } finally {
      setCommitLoading(false);
    }
  };

  const isFieldAnimating = (fieldName) => animatingFields.includes(fieldName);
  const isFieldPopulated = (fieldName) => !!formData[fieldName];
  const isPending = status === 'pending_triage';
  const isReady = status === 'ready_to_commit';

  return (
    <div className="complaint-form">
      <div className="form-header">
        <div className="form-header-text">
          <h2 className="form-title">Log Customer Complaint</h2>
          <p className="form-subtitle">API & FDF Quality Assurance Module</p>
        </div>
        <StatusBadge status={status} />
      </div>

      {/* Section 1: Origin & Customer Details */}
      <div className="form-section">
        <div className="section-label">1. ORIGIN & CUSTOMER DETAILS</div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Complaint Source</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('complaintSource') ? 'field-animate' : ''} ${isFieldPopulated('complaintSource') ? 'field-populated' : ''}`}
              value={formData.complaintSource}
              onChange={(e) => handleFieldChange('complaintSource', e.target.value)}
              placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., Pharmacy'}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Customer Name</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('customerName') ? 'field-animate' : ''} ${isFieldPopulated('customerName') ? 'field-populated' : ''}`}
              value={formData.customerName}
              onChange={(e) => handleFieldChange('customerName', e.target.value)}
              placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., Apollo Pharmacy'}
            />
          </div>
        </div>
      </div>

      {/* Section 2: Product & Batch Identification */}
      <div className="form-section">
        <div className="section-label">2. PRODUCT & BATCH IDENTIFICATION</div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Product Name (API/FDF)</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('productName') ? 'field-animate' : ''} ${isFieldPopulated('productName') ? 'field-populated' : ''}`}
              value={formData.productName}
              onChange={(e) => handleFieldChange('productName', e.target.value)}
              placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., Amoxicillin Capsules'}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Product Strength</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('productStrength') ? 'field-animate' : ''} ${isFieldPopulated('productStrength') ? 'field-populated' : ''}`}
              value={formData.productStrength}
              onChange={(e) => handleFieldChange('productStrength', e.target.value)}
              placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., 500 mg'}
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Batch / Lot Number</label>
            <div className="input-wrapper">
              <input
                type="text"
                className={`form-input ${isFieldAnimating('batchLotNumber') ? 'field-animate' : ''} ${isFieldPopulated('batchLotNumber') ? 'field-populated' : ''}`}
                value={formData.batchLotNumber}
                onChange={(e) => handleFieldChange('batchLotNumber', e.target.value)}
                placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., AMX240602'}
              />
              {isPending && !formData.batchLotNumber && (
                <span className="field-warning-icon" title="Critical field">⚠</span>
              )}
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Affected Quantity</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('affectedQuantity') ? 'field-animate' : ''} ${isFieldPopulated('affectedQuantity') ? 'field-populated' : ''}`}
              value={formData.affectedQuantity}
              onChange={(e) => handleFieldChange('affectedQuantity', e.target.value)}
              placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., 12 capsules'}
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Manufacturing Date</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('manufacturingDate') ? 'field-animate' : ''} ${isFieldPopulated('manufacturingDate') ? 'field-populated' : ''}`}
              value={formData.manufacturingDate}
              onChange={(e) => handleFieldChange('manufacturingDate', e.target.value)}
              placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., March 2026'}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Expiry Date</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('expiryDate') ? 'field-animate' : ''} ${isFieldPopulated('expiryDate') ? 'field-populated' : ''}`}
              value={formData.expiryDate}
              onChange={(e) => handleFieldChange('expiryDate', e.target.value)}
              placeholder={isPending ? 'Awaiting AI extraction...' : 'e.g., February 2028'}
            />
          </div>
        </div>
      </div>

      {/* Section 3: Facility & Material Impact */}
      <div className="form-section">
        <div className="section-label">3. FACILITY & MATERIAL IMPACT</div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Originating Site Block</label>
            <select
              className={`form-input form-select ${isFieldAnimating('originatingSiteBlock') ? 'field-animate' : ''} ${isFieldPopulated('originatingSiteBlock') ? 'field-populated' : ''}`}
              value={formData.originatingSiteBlock}
              onChange={(e) => handleFieldChange('originatingSiteBlock', e.target.value)}
            >
              {SITE_BLOCK_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt || (isPending ? 'Awaiting AI classification...' : 'Select site block...')}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Impacted Non-Product Materials (NPM)</label>
            <input
              type="text"
              className={`form-input ${isFieldAnimating('impactedNPM') ? 'field-animate' : ''} ${isFieldPopulated('impactedNPM') ? 'field-populated' : ''}`}
              value={formData.impactedNPM}
              onChange={(e) => handleFieldChange('impactedNPM', e.target.value)}
              placeholder="e.g., Primary packaging..."
            />
          </div>
        </div>
      </div>

      {/* Section 4: Defect Analysis */}
      <div className="form-section">
        <div className="section-label">4. DEFECT ANALYSIS</div>
        <div className="form-group full-width">
          <label className="form-label">Complaint Category</label>
          <input
            type="text"
            className={`form-input ${isFieldAnimating('complaintCategory') ? 'field-animate' : ''} ${isFieldPopulated('complaintCategory') ? 'field-populated' : ''}`}
            value={formData.complaintCategory}
            onChange={(e) => handleFieldChange('complaintCategory', e.target.value)}
            placeholder={isPending ? 'Awaiting AI classification...' : 'e.g., Product Defect - Discoloration'}
          />
        </div>
        <div className="form-group full-width">
          <label className="form-label">Complaint Description</label>
          <textarea
            className={`form-input form-textarea ${isFieldAnimating('complaintDescription') ? 'field-animate' : ''} ${isFieldPopulated('complaintDescription') ? 'field-populated' : ''}`}
            value={formData.complaintDescription}
            onChange={(e) => handleFieldChange('complaintDescription', e.target.value)}
            placeholder={isPending ? 'AI will synthesize the complaint into a formal QMS description...' : 'Describe the complaint...'}
            rows={3}
          />
        </div>
      </div>

      {/* AI Copilot Risk Assessment */}
      <RiskAssessmentCard riskAssessment={riskAssessment} />

      {/* Commit Button */}
      <div className="form-actions">
        {commitSuccess ? (
          <div className="commit-success">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="10" fill="#10b981" />
              <path d="M6 10L9 13L14 7" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span>Committed to QMS Ledger</span>
          </div>
        ) : (
          <button
            className={`commit-btn ${isReady ? 'commit-btn-ready' : ''}`}
            onClick={handleCommit}
            disabled={isPending || commitLoading || isLoading}
          >
            {commitLoading ? (
              <>
                <span className="btn-spinner"></span>
                Committing...
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 12l2 2 4-4" />
                  <rect x="3" y="3" width="18" height="18" rx="3" />
                </svg>
                Commit to QMS Ledger
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
