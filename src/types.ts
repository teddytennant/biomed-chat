// Global type definitions for Biomed Chat

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  id?: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface Settings {
  theme: 'dark' | 'light' | 'auto';
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    browser: boolean;
  };
  privacy: 'private' | 'public';
  autoSave: boolean;
  messagePreview: boolean;
  lastUpdated?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatRequest {
  messages: Message[];
  userId?: string;
  sessionId?: string;
}

export interface ChatResponse {
  message: Message;
  sessionId?: string;
}

// Component Props
export interface ChatProps {
  user?: User;
  onSendMessage?: (message: string) => void;
}

export interface MessageBubbleProps {
  message: Message;
  isUser: boolean;
}

export interface SettingsProps {
  user?: User;
  onSettingsChange?: (settings: Partial<Settings>) => void;
}

// API Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: any;
}

// Utility Types
export type ThemeMode = 'dark' | 'light' | 'auto';
export type NotificationType = 'email' | 'push' | 'browser';
export type PrivacyLevel = 'private' | 'public';

// Redux State
export interface RootState {
  chat: ChatState;
  auth: AuthState;
  settings: Settings;
}

// Action Types
export interface Action<T = any> {
  type: string;
  payload?: T;
}
