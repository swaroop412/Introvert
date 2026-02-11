print("=" * 80)
print("ORATORIQ - COMPREHENSIVE ERROR HANDLING & ACCESSIBILITY")
print("=" * 80)

import os

client_src = "oratoriq/client/src"
utils_dir = os.path.join(client_src, "utils")
os.makedirs(utils_dir, exist_ok=True)

# ============================================================================
# Toast Notification System with Error Handling
# ============================================================================
toast_system = """import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (toast) => {
    const id = Math.random().toString(36).substring(7);
    const newToast: Toast = { ...toast, id };
    
    set((state) => ({
      toasts: [...state.toasts, newToast],
    }));
    
    // Auto-remove after duration (default 5s)
    const duration = toast.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        }));
      }, duration);
    }
  },
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }));
  },
}));

// Convenience functions for different toast types
export const toast = {
  success: (title: string, message: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'success', title, message, duration });
  },
  error: (title: string, message: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'error', title, message, duration });
  },
  warning: (title: string, message: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'warning', title, message, duration });
  },
  info: (title: string, message: string, duration?: number) => {
    useToastStore.getState().addToast({ type: 'info', title, message, duration });
  },
};
"""

toast_path = os.path.join(utils_dir, "toast.ts")
with open(toast_path, 'w') as f:
    f.write(toast_system)
print(f"✓ Created {toast_path}")

# ============================================================================
# Toast Container Component
# ============================================================================
toast_container = """import { useEffect } from 'react';
import { useToastStore } from '../../utils/toast';

export const ToastContainer = () => {
  const { toasts, removeToast } = useToastStore();

  return (
    <div 
      className="fixed top-4 right-4 z-50 space-y-3 max-w-md"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
};

interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  onClose: () => void;
}

const Toast = ({ type, title, message, onClose }: ToastProps) => {
  const colors = {
    success: {
      bg: 'bg-green-50 dark:bg-green-900',
      border: 'border-green-400',
      text: 'text-green-800 dark:text-green-200',
      icon: '✓',
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-900',
      border: 'border-red-400',
      text: 'text-red-800 dark:text-red-200',
      icon: '✕',
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900',
      border: 'border-yellow-400',
      text: 'text-yellow-800 dark:text-yellow-200',
      icon: '⚠',
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900',
      border: 'border-blue-400',
      text: 'text-blue-800 dark:text-blue-200',
      icon: 'ℹ',
    },
  };

  const style = colors[type];

  return (
    <div
      className={`${style.bg} ${style.border} ${style.text} border-l-4 p-4 rounded-lg shadow-lg animate-slide-in`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <span className="text-2xl" aria-hidden="true">{style.icon}</span>
          <div>
            <h3 className="font-semibold">{title}</h3>
            <p className="text-sm mt-1">{message}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="ml-4 hover:opacity-70 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 rounded"
          aria-label="Close notification"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};
"""

toast_container_path = os.path.join(client_src, "components/ToastContainer.tsx")
with open(toast_container_path, 'w') as f:
    f.write(toast_container)
print(f"✓ Created {toast_container_path}")

# ============================================================================
# Error Handling Utilities
# ============================================================================
error_utils = """import { toast } from './toast';

export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public userMessage: string,
    public recoverable: boolean = true
  ) {
    super(message);
    this.name = 'AppError';
  }
}

// Permission Error Handling
export const handlePermissionError = (error: unknown): AppError => {
  const message = error instanceof Error ? error.message : 'Unknown error';
  
  if (message.includes('Permission denied') || message.includes('NotAllowedError')) {
    return new AppError(
      message,
      'PERMISSION_DENIED',
      'Camera/microphone access was denied. Please allow permissions in your browser settings.',
      true
    );
  }
  
  if (message.includes('NotFoundError')) {
    return new AppError(
      message,
      'DEVICE_NOT_FOUND',
      'No camera or microphone found. Please connect a device and try again.',
      true
    );
  }
  
  if (message.includes('NotReadableError')) {
    return new AppError(
      message,
      'DEVICE_IN_USE',
      'Camera or microphone is already in use by another application.',
      true
    );
  }
  
  return new AppError(
    message,
    'MEDIA_ERROR',
    'Failed to access camera/microphone. Please check your device and try again.',
    true
  );
};

// Network Error Handling
export const handleNetworkError = (error: unknown): AppError => {
  const message = error instanceof Error ? error.message : 'Unknown error';
  
  if (message.includes('Failed to fetch') || message.includes('NetworkError')) {
    return new AppError(
      message,
      'NETWORK_ERROR',
      'Network connection failed. Please check your internet connection.',
      true
    );
  }
  
  if (message.includes('timeout')) {
    return new AppError(
      message,
      'TIMEOUT_ERROR',
      'Request timed out. Please try again.',
      true
    );
  }
  
  return new AppError(
    message,
    'CONNECTION_ERROR',
    'Unable to connect to server. Please try again later.',
    true
  );
};

// API Error Handling
export const handleAPIError = (status: number, message: string): AppError => {
  switch (status) {
    case 400:
      return new AppError(
        message,
        'BAD_REQUEST',
        'Invalid request. Please check your input and try again.',
        true
      );
    case 401:
      return new AppError(
        message,
        'UNAUTHORIZED',
        'Authentication failed. Please log in again.',
        true
      );
    case 403:
      return new AppError(
        message,
        'FORBIDDEN',
        'You do not have permission to perform this action.',
        false
      );
    case 404:
      return new AppError(
        message,
        'NOT_FOUND',
        'The requested resource was not found.',
        true
      );
    case 429:
      return new AppError(
        message,
        'RATE_LIMIT',
        'Too many requests. Please wait a moment and try again.',
        true
      );
    case 500:
    case 502:
    case 503:
      return new AppError(
        message,
        'SERVER_ERROR',
        'Server error occurred. Please try again later.',
        true
      );
    default:
      return new AppError(
        message,
        'UNKNOWN_ERROR',
        'An unexpected error occurred. Please try again.',
        true
      );
  }
};

// Display error as toast
export const showErrorToast = (error: AppError | Error) => {
  if (error instanceof AppError) {
    toast.error(
      'Error',
      error.userMessage,
      error.recoverable ? 5000 : 0 // Don't auto-dismiss critical errors
    );
  } else {
    toast.error(
      'Error',
      'An unexpected error occurred. Please try again.',
      5000
    );
  }
};

// Retry utility with exponential backoff
export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      const delay = baseDelay * Math.pow(2, i);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw new Error('Max retries exceeded');
};
"""

error_utils_path = os.path.join(utils_dir, "errorHandling.ts")
with open(error_utils_path, 'w') as f:
    f.write(error_utils)
print(f"✓ Created {error_utils_path}")

print("\n" + "=" * 80)
print("ERROR HANDLING INFRASTRUCTURE COMPLETE")
print("=" * 80)
print("\n✅ Components created:")
print("  • Toast notification system with Zustand store")
print("  • ToastContainer component with accessibility")
print("  • Error handling utilities (permissions, network, API)")
print("  • Retry logic with exponential backoff")
print("\n🎯 Features:")
print("  • User-friendly error messages")
print("  • Auto-dismiss toasts (configurable)")
print("  • ARIA labels for screen readers")
print("  • Color-coded notifications")
print("  • Manual close buttons")
print("  • Structured error types (AppError)")

error_handling_created = True
