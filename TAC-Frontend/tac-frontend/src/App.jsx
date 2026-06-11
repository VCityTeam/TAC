import { BrowserRouter, Routes, Route } from "react-router-dom"
import Termes from "./Termes"
import Concepts from "./Concepts"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Termes />} />
        <Route path="/concepts" element={<Concepts />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App