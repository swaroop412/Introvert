print("=" * 80)
print("ORATORIQ - CREATING ZUSTAND STORE WITH FER SUPPORT")
print("=" * 80)

store_content = """
import os

store_dir = "oratoriq/client/src/store"
os.makedirs(store_dir, exist_ok=True)

# ============================================================================
# Store Types (types.ts) - Updated with FER support
# ============================================================================
store_types = \"\"\"import { FacialEvent, FaceDetectionResult } from '../../../shared/types';

export type AppMode = 'interview' | 'speech';

export type Theme = 'light' | 'dark';

export interface SessionState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number; // milliseconds
  sessionId: string | null;
  facialEvents: FacialEvent[]; // FER events collected during session
  currentExpression: FaceDetectionResult | null; // Current real-time FER result
}

export interface AppState {
  // Theme
  theme: Theme;
  toggleTheme: () => void;
  
  // Mode
  mode: AppMode;
  setMode: (mode: AppMode) => void;
  
  // Session
  session: SessionState;
  startRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  stopRecording: () => void;
  updateDuration: (duration: number) => void;
  
  // FER Management
  addFacialEvent: (event: FacialEvent) => void;
  updateCurrentExpression: (result: FaceDetectionResult) => void;
  clearFacialEvents: () => void;
}
\"\"\"

with open(os.path.join(store_dir, "types.ts"), 'w') as f:
    f.write(store_types)
print(f"✓ Created {os.path.join(store_dir, 'types.ts')}")

# ============================================================================
# Main Store (index.ts) - Updated with FER support
# ============================================================================
store_index = \"\"\"import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppState, SessionState } from './types';
import { FacialEvent, FaceDetectionResult } from '../../../shared/types';

const initialSessionState: SessionState = {
  isRecording: false,
  isPaused: false,
  duration: 0,
  sessionId: null,
  facialEvents: [],
  currentExpression: null,
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Theme state
      theme: 'dark',
      toggleTheme: () =>
        set((state) => ({
          theme: state.theme === 'dark' ? 'light' : 'dark',
        })),

      // Mode state
      mode: 'interview',
      setMode: (mode) => set({ mode }),

      // Session state
      session: initialSessionState,
      
      startRecording: () =>
        set((state) => ({
          session: {
            ...state.session,
            isRecording: true,
            isPaused: false,
            sessionId: crypto.randomUUID(),
            duration: 0,
            facialEvents: [],
            currentExpression: null,
          },
        })),

      pauseRecording: () =>
        set((state) => ({
          session: {
            ...state.session,
            isPaused: true,
          },
        })),

      resumeRecording: () =>
        set((state) => ({
          session: {
            ...state.session,
            isPaused: false,
          },
        })),

      stopRecording: () =>
        set({
          session: initialSessionState,
        }),

      updateDuration: (duration) =>
        set((state) => ({
          session: {
            ...state.session,
            duration,
          },
        })),

      // FER Management
      addFacialEvent: (event: FacialEvent) =>
        set((state) => ({
          session: {
            ...state.session,
            facialEvents: [...state.session.facialEvents, event],
          },
        })),

      updateCurrentExpression: (result: FaceDetectionResult) =>
        set((state) => ({
          session: {
            ...state.session,
            currentExpression: result,
          },
        })),

      clearFacialEvents: () =>
        set((state) => ({
          session: {
            ...state.session,
            facialEvents: [],
            currentExpression: null,
          },
        })),
    }),
    {
      name: 'oratoriq-storage',
      partialize: (state) => ({
        theme: state.theme,
        mode: state.mode,
      }),
    }
  )
);

// Selectors for optimized re-renders
export const selectTheme = (state: AppState) => state.theme;
export const selectMode = (state: AppState) => state.mode;
export const selectSession = (state: AppState) => state.session;
export const selectIsRecording = (state: AppState) => state.session.isRecording;
export const selectFacialEvents = (state: AppState) => state.session.facialEvents;
export const selectCurrentExpression = (state: AppState) => state.session.currentExpression;
\"\"\"

with open(os.path.join(store_dir, "index.ts"), 'w') as f:
    f.write(store_index)
print(f"✓ Created {os.path.join(store_dir, 'index.ts')}")

print("\\n" + "=" * 80)
print("ZUSTAND STORE WITH FER SUPPORT CREATED")
print("=" * 80)
print("\\n✅ Features:")
print("  • Theme switching (dark/light)")
print("  • App mode selection (interview/speech)")
print("  • Session state management (recording, pause, duration)")
print("  • FER data storage: facialEvents array and currentExpression")
print("  • FER actions: addFacialEvent, updateCurrentExpression, clearFacialEvents")
print("  • Persistent storage for theme and mode preferences")
print("  • Optimized selectors for performance")

zustand_store_with_fer_created = True
"""

exec(store_content)
