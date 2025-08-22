import { configureStore } from '@reduxjs/toolkit';
import chatSlice from './slices/chatSlice';
import authSlice from './slices/authSlice';
import settingsSlice from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    chat: chatSlice,
    auth: authSlice,
    settings: settingsSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
