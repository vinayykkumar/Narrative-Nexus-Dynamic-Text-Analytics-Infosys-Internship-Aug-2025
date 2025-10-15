import { Navigate, Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import Login from "./pages/Auth/Login"
import Analysis from "./pages/Analysis"
import Navbar from "./components/Navbar"
import About from "./pages/About"
import Dashboard from "./pages/Dashboard"
import { useAuth } from "./contexts/AuthContext"

function App() {
  const { loading, isAuthenticated } = useAuth()

  const RequireAuth = ({ children }) => {
    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-black text-white">
          <p className="text-sm text-gray-400">Checking your session...</p>
        </div>
      )
    }
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />
    }
    return children
  }

  return (
    <>
    <Navbar/>
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/login" element={<Login/>}/>
      <Route path="/analyze" element={<Analysis/>}/>
      <Route path="/about-us" element={<About/>}/>
      <Route
        path="/dashboard"
        element={
          <RequireAuth>
            <Dashboard />
          </RequireAuth>
        }
      />
    </Routes>
    </>
  )
}

export default App