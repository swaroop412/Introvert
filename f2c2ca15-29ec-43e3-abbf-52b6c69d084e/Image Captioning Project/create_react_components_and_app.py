import os

print("=" * 80)
print("ORATORIQ - CREATING REACT COMPONENTS AND MAIN APP")
print("=" * 80)

client_src = "oratoriq/client/src"

# ============================================================================
# Header Component (components/layout/Header.tsx)
# ============================================================================
header_component = """import { useAppStore } from '../../store';

export const Header = () => {
  const { theme, toggleTheme, mode, setMode } = useAppStore();

  return (
    <header className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              OratorIQ
            </h1>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMode('interview')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                mode === 'interview'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              Interview
            </button>
            <button
              onClick={() => setMode('speech')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                mode === 'speech'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              Speech
            </button>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <svg className="w-6 h-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
"""

header_path = os.path.join(client_src, "components/layout/Header.tsx")
with open(header_path, 'w') as f:
    f.write(header_component)
print(f"✓ Created {header_path}")

# ============================================================================
# Main Layout Component (components/layout/Layout.tsx)
# ============================================================================
layout_component = """import { ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};
"""

layout_path = os.path.join(client_src, "components/layout/Layout.tsx")
with open(layout_path, 'w') as f:
    f.write(layout_component)
print(f"✓ Created {layout_path}")

# ============================================================================
# Home Page (pages/Home.tsx)
# ============================================================================
home_page = """import { useAppStore } from '../store';

export const Home = () => {
  const { mode, session } = useAppStore();

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-4xl font-bold mb-4">
          Welcome to OratorIQ
        </h2>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          Your AI-powered speech analysis platform
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-semibold">Current Mode</h3>
          <span className="px-4 py-2 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded-lg font-medium capitalize">
            {mode}
          </span>
        </div>

        <div className="space-y-4">
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <h4 className="text-lg font-medium mb-2">Session Status</h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Recording</p>
                <p className="text-lg font-semibold">
                  {session.isRecording ? 'Active' : 'Inactive'}
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Duration</p>
                <p className="text-lg font-semibold">
                  {Math.floor(session.duration / 1000)}s
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <h4 className="text-lg font-medium mb-2">Mode Description</h4>
            <p className="text-gray-600 dark:text-gray-400">
              {mode === 'interview' 
                ? 'Practice and improve your interview skills with AI-powered feedback on your responses, body language, and communication style.'
                : 'Enhance your public speaking abilities with comprehensive analysis of your speech patterns, pace, clarity, and engagement.'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">Features</h3>
          <ul className="space-y-2 text-gray-600 dark:text-gray-400">
            <li className="flex items-start">
              <span className="text-primary-600 dark:text-primary-400 mr-2">✓</span>
              Real-time speech transcription
            </li>
            <li className="flex items-start">
              <span className="text-primary-600 dark:text-primary-400 mr-2">✓</span>
              Facial expression analysis
            </li>
            <li className="flex items-start">
              <span className="text-primary-600 dark:text-primary-400 mr-2">✓</span>
              Disfluency detection
            </li>
            <li className="flex items-start">
              <span className="text-primary-600 dark:text-primary-400 mr-2">✓</span>
              Comprehensive evaluation metrics
            </li>
          </ul>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">Getting Started</h3>
          <ol className="space-y-2 text-gray-600 dark:text-gray-400 list-decimal list-inside">
            <li>Select your mode (Interview or Speech)</li>
            <li>Start a new recording session</li>
            <li>Speak naturally and let AI analyze</li>
            <li>Review detailed feedback and insights</li>
          </ol>
        </div>
      </div>
    </div>
  );
};
"""

home_path = os.path.join(client_src, "pages/Home.tsx")
with open(home_path, 'w') as f:
    f.write(home_page)
print(f"✓ Created {home_path}")

# ============================================================================
# Main App Component (App.tsx)
# ============================================================================
app_component = """import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Home } from './pages/Home';
import { useAppStore } from './store';

function App() {
  const theme = useAppStore((state) => state.theme);

  // Apply theme class to document
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
"""

app_path = os.path.join(client_src, "App.tsx")
with open(app_path, 'w') as f:
    f.write(app_component)
print(f"✓ Created {app_path}")

# ============================================================================
# Main Entry Point (main.tsx)
# ============================================================================
main_tsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""

main_path = os.path.join(client_src, "main.tsx")
with open(main_path, 'w') as f:
    f.write(main_tsx)
print(f"✓ Created {main_path}")

# ============================================================================
# vite-env.d.ts for TypeScript
# ============================================================================
vite_env = """/// <reference types="vite/client" />
"""

vite_env_path = os.path.join(client_src, "vite-env.d.ts")
with open(vite_env_path, 'w') as f:
    f.write(vite_env)
print(f"✓ Created {vite_env_path}")

print("\n" + "=" * 80)
print("REACT COMPONENTS AND APP CREATED")
print("=" * 80)
print("\n✅ Components created:")
print("  • Header - Theme toggle + Mode switcher")
print("  • Layout - Main app layout wrapper")
print("  • Home - Landing page with session status")
print("  • App - Root component with routing")
print("  • main.tsx - Entry point")
print("\n🎨 Features implemented:")
print("  • Dark/Light theme toggle with persistence")
print("  • Interview/Speech mode switching")
print("  • Session state display")
print("  • Responsive Tailwind CSS design")
print("  • React Router for navigation")
print("\n🚀 Ready to run: cd oratoriq/client && npm install && npm run dev")

react_app_complete = True
