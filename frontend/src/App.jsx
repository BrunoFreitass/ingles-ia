import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import LessonDetail from './pages/LessonDetail'
import Flashcards from './pages/Flashcards'
import Quiz from './pages/Quiz'
import Conversation from './pages/Conversation'
import Immersion from './pages/Immersion'
import Review from './pages/Review'
import Speaking from './pages/Speaking'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/registro" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/niveis/:levelId/licoes/:lessonId"
            element={
              <ProtectedRoute>
                <LessonDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/niveis/:levelId/licoes/:lessonId/flashcards"
            element={
              <ProtectedRoute>
                <Flashcards />
              </ProtectedRoute>
            }
          />
          <Route
            path="/niveis/:levelId/licoes/:lessonId/quiz"
            element={
              <ProtectedRoute>
                <Quiz />
              </ProtectedRoute>
            }
          />
          <Route
            path="/niveis/:levelId/licoes/:lessonId/conversation"
            element={
              <ProtectedRoute>
                <Conversation />
              </ProtectedRoute>
            }
          />
          <Route
            path="/niveis/:levelId/licoes/:lessonId/fala"
            element={
              <ProtectedRoute>
                <Speaking />
              </ProtectedRoute>
            }
          />
          <Route
            path="/imersao"
            element={
              <ProtectedRoute>
                <Immersion />
              </ProtectedRoute>
            }
          />
          <Route
            path="/revisao"
            element={
              <ProtectedRoute>
                <Review />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
