import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Home from './shared/pages/Home';
import Navbar from './shared/components/Navbar';
import ProtectedRoute from './shared/components/ProtectedRoute';
import ChatbotWidget from './shared/components/ChatbotWidget';
import ResumeBuilder from './features/create-resume/pages/ResumeBuilder';
import LoginPage from './features/login/LoginPage';
import SignupPage from './features/signup/SignupPage';
import MyResumesPage from './features/resume/MyResumesPage';
import AnalyzePage from './features/analyze/AnalyzePage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 text-gray-900">
          <Navbar />
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />

              {/* Protected routes — require login */}
              <Route
                path="/builder"
                element={
                  <ProtectedRoute>
                    <ResumeBuilder />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/my-resumes"
                element={
                  <ProtectedRoute>
                    <MyResumesPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/analyze"
                element={
                  <ProtectedRoute>
                    <AnalyzePage />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </main>

          {/* Global floating chatbot — available on every page */}
          <ChatbotWidget />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
