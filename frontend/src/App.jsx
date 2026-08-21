import { useEffect } from 'react'
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
import ProvaFinal from './pages/ProvaFinal'
import Ranking from './pages/Ranking'
import Profile from './pages/Profile'
import ProfileEdit from './pages/ProfileEdit'

export default function App() {
  useEffect(() => {
    // "Acorda" o backend assim que o site carrega, antes mesmo da pessoa
    // fazer login — em produção, o Render (plano free) coloca o servidor
    // pra dormir depois de um tempo sem uso, e a primeira requisição real
    // demoraria 30-50s. Disparando isso cedo (sem esperar resposta), o
    // servidor já está acordando enquanto a pessoa lê a tela de login.
    const apiUrl = import.meta.env.VITE_API_URL || ''
    fetch(`${apiUrl}/`).catch(() => {
      // Silencioso de propósito: isso é só um "toque" pra acordar o
      // servidor, falha aqui não deve incomodar o usuário nem aparecer
      // como erro em lugar nenhum da tela.
    })
  }, [])

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
          <Route
            path="/capitulos/:capituloId/prova-final"
            element={
              <ProtectedRoute>
                <ProvaFinal />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ranking"
            element={
              <ProtectedRoute>
                <Ranking />
              </ProtectedRoute>
            }
          />
          <Route
            path="/perfil/editar"
            element={
              <ProtectedRoute>
                <ProfileEdit />
              </ProtectedRoute>
            }
          />
          <Route
            path="/perfil/:userId"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}