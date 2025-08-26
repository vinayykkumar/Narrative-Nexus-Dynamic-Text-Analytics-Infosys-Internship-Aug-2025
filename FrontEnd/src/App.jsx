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
      
    </Routes>
    </>
  )
}

export default App
