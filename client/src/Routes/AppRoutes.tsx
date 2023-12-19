import LandingPage from "@/pages/LandingPage/LandingPage"
import PaymentPage from "@/pages/PaymentPage/PaymentPage"
import { Signup } from "@/pages/Signup/Signup"
import Success from "@/pages/Success/Success"
import { Navigate, Route, Routes } from "react-router-dom"

const AppRoutes = () => {
  return (
    <Routes>
        <Route path="/" element={<LandingPage/>}/>
        <Route path="/register" element={<Signup/>}/>
        <Route path="/pay" element={<PaymentPage/>}/>
        <Route path="/success" element={<Success/>}/>
        <Route path="*" element={<Navigate to={`/`} replace/>} />
    </Routes>
  )
}

export default AppRoutes