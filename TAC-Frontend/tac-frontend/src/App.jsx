import { BrowserRouter, Routes, Route } from "react-router-dom"
import Termes from "./Termes"
import Concepts from "./Concepts"
import Thesaurus from "./Thesaurus"
import Alignements from "./Alignements"
import Export from "./Export"



function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Termes />} />
        <Route path="/concepts" element={<Concepts />} />
        <Route path="/thesaurus" element={<Thesaurus />} />
        <Route path="/alignements" element={<Alignements/>}/>
        <Route path="/export" element={<Export/>}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App