<<<<<<< HEAD
import { Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import Login from "./pages/Auth/Login"
import Layout from "./pages/ai/Layout"
import Dashboard from "./pages/ai/Dashboard"
import Analysis from "./pages/ai/Analysis"
import Summarization from "./pages/ai/Summarization"
import Reports from "./pages/ai/Reports"




function App() {
  
  return (
    <>
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/login" element={<Login/>}/>

      <Route path="/ai" element={<Layout/>}>
      <Route index element={<Dashboard/>}/>
      <Route path="/ai/text-analysis" element={<Analysis/>}/>
      <Route path="/ai/text-summarization" element={<Summarization/>}/>
      <Route path="/ai/reports" element={<Reports/>}/>
      </Route>
      
=======
import { Navigate, Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import Login from "./pages/Auth/Login"
import Navbar from "./components/Navbar"
import About from "./pages/About"
import Analysis from "./pages/analysis"
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
>>>>>>> origin/main
    </Routes>
    </>
  )
}

<<<<<<< HEAD
export default App
=======
export default App
>>>>>>> origin/main
