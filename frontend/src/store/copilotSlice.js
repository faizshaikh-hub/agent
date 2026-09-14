import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';

// Async thunk for sending chat messages
export const sendMessage = createAsyncThunk(
  'copilot/sendMessage',
  async ({ message, currentFormState }, { getState, rejectWithValue }) => {
    try {
      const state = getState();
      const sessionId = state.copilot.sessionId;

      // Transform camelCase form state to snake_case for API
      const formState = currentFormState ? {
        complaint_source: currentFormState.complaintSource || null,
        customer_name: currentFormState.customerName || null,
        product_name: currentFormState.productName || null,
        product_strength: currentFormState.productStrength || null,
        batch_lot_number: currentFormState.batchLotNumber || null,
        affected_quantity: currentFormState.affectedQuantity || null,
        manufacturing_date: currentFormState.manufacturingDate || null,
        expiry_date: currentFormState.expiryDate || null,
        originating_site_block: currentFormState.originatingSiteBlock || null,
        impacted_npm: currentFormState.impactedNPM || null,
        complaint_category: currentFormState.complaintCategory || null,
        complaint_description: currentFormState.complaintDescription || null,
      } : null;

      const response = await api.post('/api/copilot/chat', {
        message,
        session_id: sessionId,
        current_form_state: formState,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to process message');
    }
  }
);

// Async thunk for file upload
export const uploadFile = createAsyncThunk(
  'copilot/uploadFile',
  async (file, { getState, rejectWithValue }) => {
    try {
      const state = getState();
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', state.copilot.sessionId);

      const response = await api.post('/api/copilot/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to upload file');
    }
  }
);

const generateId = () => Math.random().toString(36).substr(2, 9);

const copilotSlice = createSlice({
  name: 'copilot',
  initialState: {
    messages: [
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Ready to process new complaints. You can paste the raw email from the customer, or upload a PDF of the complaint report. I will extract the data and run the initial risk assessment.',
        timestamp: new Date().toISOString(),
      },
    ],
    sessionId: generateId(),
    isProcessing: false,
    isConnected: true,
    error: null,
  },
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({
        id: generateId(),
        role: 'user',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    addAssistantMessage: (state, action) => {
      state.messages.push({
        id: generateId(),
        role: 'assistant',
        content: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    setProcessing: (state, action) => {
      state.isProcessing = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    resetChat: (state) => {
      state.messages = [
        {
          id: 'welcome',
          role: 'assistant',
          content: 'Ready to process new complaints. You can paste the raw email from the customer, or upload a PDF of the complaint report. I will extract the data and run the initial risk assessment.',
          timestamp: new Date().toISOString(),
        },
      ];
      state.sessionId = generateId();
      state.isProcessing = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // sendMessage
      .addCase(sendMessage.pending, (state) => {
        state.isProcessing = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isProcessing = false;
        state.messages.push({
          id: generateId(),
          role: 'assistant',
          content: action.payload.reply,
          timestamp: new Date().toISOString(),
        });
        if (action.payload.session_id) {
          state.sessionId = action.payload.session_id;
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isProcessing = false;
        state.error = action.payload || 'Unknown error';
        state.messages.push({
          id: generateId(),
          role: 'assistant',
          content: `⚠️ Error: ${action.payload || 'Failed to process your message. Please try again.'}`,
          timestamp: new Date().toISOString(),
          isError: true,
        });
      })
      // uploadFile
      .addCase(uploadFile.pending, (state) => {
        state.isProcessing = true;
        state.error = null;
      })
      .addCase(uploadFile.fulfilled, (state, action) => {
        state.isProcessing = false;
        state.messages.push({
          id: generateId(),
          role: 'assistant',
          content: action.payload.reply,
          timestamp: new Date().toISOString(),
        });
        if (action.payload.session_id) {
          state.sessionId = action.payload.session_id;
        }
      })
      .addCase(uploadFile.rejected, (state, action) => {
        state.isProcessing = false;
        state.error = action.payload || 'Unknown error';
        state.messages.push({
          id: generateId(),
          role: 'assistant',
          content: `⚠️ Error: ${action.payload || 'Failed to process the uploaded file.'}`,
          timestamp: new Date().toISOString(),
          isError: true,
        });
      });
  },
});

export const {
  addUserMessage,
  addAssistantMessage,
  setProcessing,
  clearError,
  resetChat,
} = copilotSlice.actions;

export default copilotSlice.reducer;
