import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Settings } from '../../types';

const defaultSettings: Settings = {
  theme: 'dark',
  language: 'en',
  notifications: {
    email: true,
    push: false,
    browser: true,
  },
  privacy: 'private',
  autoSave: true,
  messagePreview: true,
};

const initialState: Settings = (() => {
  try {
    const saved = localStorage.getItem('biomedChatSettings');
    return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
  } catch {
    return defaultSettings;
  }
})();

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateSettings: (state, action: PayloadAction<Partial<Settings>>) => {
      const updatedSettings = { ...state, ...action.payload, lastUpdated: new Date().toISOString() };

      // Save to localStorage
      try {
        localStorage.setItem('biomedChatSettings', JSON.stringify(updatedSettings));
      } catch (error) {
        console.error('Failed to save settings:', error);
      }

      // Apply theme immediately
      if (action.payload.theme) {
        document.documentElement.setAttribute('data-theme', action.payload.theme);
        localStorage.setItem('biomedChatTheme', action.payload.theme);
      }

      return updatedSettings;
    },
    setTheme: (state, action: PayloadAction<Settings['theme']>) => {
      state.theme = action.payload;
      document.documentElement.setAttribute('data-theme', action.payload);
      localStorage.setItem('biomedChatTheme', action.payload);

      try {
        const updatedSettings = { ...state, lastUpdated: new Date().toISOString() };
        localStorage.setItem('biomedChatSettings', JSON.stringify(updatedSettings));
      } catch (error) {
        console.error('Failed to save theme:', error);
      }
    },
    updateNotifications: (state, action: PayloadAction<Partial<Settings['notifications']>>) => {
      state.notifications = { ...state.notifications, ...action.payload };

      try {
        const updatedSettings = { ...state, lastUpdated: new Date().toISOString() };
        localStorage.setItem('biomedChatSettings', JSON.stringify(updatedSettings));
      } catch (error) {
        console.error('Failed to save notification settings:', error);
      }
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.language = action.payload;

      try {
        const updatedSettings = { ...state, lastUpdated: new Date().toISOString() };
        localStorage.setItem('biomedChatSettings', JSON.stringify(updatedSettings));
      } catch (error) {
        console.error('Failed to save language:', error);
      }
    },
    setPrivacy: (state, action: PayloadAction<Settings['privacy']>) => {
      state.privacy = action.payload;

      try {
        const updatedSettings = { ...state, lastUpdated: new Date().toISOString() };
        localStorage.setItem('biomedChatSettings', JSON.stringify(updatedSettings));
      } catch (error) {
        console.error('Failed to save privacy setting:', error);
      }
    },
    resetSettings: () => {
      try {
        localStorage.setItem('biomedChatSettings', JSON.stringify(defaultSettings));
        document.documentElement.setAttribute('data-theme', defaultSettings.theme);
        localStorage.setItem('biomedChatTheme', defaultSettings.theme);
      } catch (error) {
        console.error('Failed to reset settings:', error);
      }
      return defaultSettings;
    },
  },
});

export const {
  updateSettings,
  setTheme,
  updateNotifications,
  setLanguage,
  setPrivacy,
  resetSettings,
} = settingsSlice.actions;

export default settingsSlice.reducer;
