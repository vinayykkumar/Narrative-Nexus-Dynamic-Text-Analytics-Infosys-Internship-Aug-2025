import { Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import Login from "./pages/Auth/Login"
import Analysis from "./pages/analysis"
import Navbar from "./components/Navbar"
import About from "./pages/About"

function App() {
  
  return (
    <>
    <Navbar/>
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/login" element={<Login/>}/>
      <Route path="/analyze" element={<Analysis/>}/>
      <Route path="/about-us" element={<About/>}/>
    </Routes>
    </>
  )
}

export default App
