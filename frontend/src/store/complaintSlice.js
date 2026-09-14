import { createSlice } from '@reduxjs/toolkit';

const initialFormData = {
  complaintSource: '',
  customerName: '',
  productName: '',
  productStrength: '',
  batchLotNumber: '',
  affectedQuantity: '',
  manufacturingDate: '',
  expiryDate: '',
  originatingSiteBlock: '',
  impactedNPM: '',
  complaintCategory: '',
  complaintDescription: '',
};

const initialRiskAssessment = {
  severity: '',
  suggestedNextAction: '',
  initialRiskAssessment: '',
  rootCauseRecommendation: '',
  capaRecommendation: '',
};

const complaintSlice = createSlice({
  name: 'complaint',
  initialState: {
    status: 'pending_triage',
    formData: { ...initialFormData },
    riskAssessment: { ...initialRiskAssessment },
    isLoading: false,
    committedId: null,
    animatingFields: [],
  },
  reducers: {
    updateFormFields: (state, action) => {
      const updates = action.payload;
      const fieldsUpdated = [];
      // Map snake_case API keys to camelCase state keys
      const keyMap = {
        complaint_source: 'complaintSource',
        customer_name: 'customerName',
        product_name: 'productName',
        product_strength: 'productStrength',
        batch_lot_number: 'batchLotNumber',
        affected_quantity: 'affectedQuantity',
        manufacturing_date: 'manufacturingDate',
        expiry_date: 'expiryDate',
        originating_site_block: 'originatingSiteBlock',
        impacted_npm: 'impactedNPM',
        complaint_category: 'complaintCategory',
        complaint_description: 'complaintDescription',
      };

      Object.entries(updates).forEach(([key, value]) => {
        const camelKey = keyMap[key] || key;
        if (value !== null && value !== undefined && camelKey in state.formData) {
          state.formData[camelKey] = value;
          fieldsUpdated.push(camelKey);
        }
      });
      state.animatingFields = fieldsUpdated;
    },
    setRiskAssessment: (state, action) => {
      const risk = action.payload;
      if (risk) {
        state.riskAssessment = {
          severity: risk.severity || '',
          suggestedNextAction: risk.suggested_next_action || risk.suggestedNextAction || '',
          initialRiskAssessment: risk.initial_risk_assessment || risk.initialRiskAssessment || '',
          rootCauseRecommendation: risk.root_cause_recommendation || risk.rootCauseRecommendation || '',
          capaRecommendation: risk.capa_recommendation || risk.capaRecommendation || '',
        };
      }
    },
    setStatus: (state, action) => {
      state.status = action.payload;
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setCommittedId: (state, action) => {
      state.committedId = action.payload;
    },
    clearAnimatingFields: (state) => {
      state.animatingFields = [];
    },
    resetForm: (state) => {
      state.status = 'pending_triage';
      state.formData = { ...initialFormData };
      state.riskAssessment = { ...initialRiskAssessment };
      state.isLoading = false;
      state.committedId = null;
      state.animatingFields = [];
    },
    updateSingleField: (state, action) => {
      const { field, value } = action.payload;
      if (field in state.formData) {
        state.formData[field] = value;
      }
    },
  },
});

export const {
  updateFormFields,
  setRiskAssessment,
  setStatus,
  setLoading,
  setCommittedId,
  clearAnimatingFields,
  resetForm,
  updateSingleField,
} = complaintSlice.actions;

export default complaintSlice.reducer;
