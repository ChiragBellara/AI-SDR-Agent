import { useLocation } from "react-router-dom";
import Home from "./components/Home";
import SellerPage from "./pages/SellerPage";

export default function App() {
    const { pathname } = useLocation();

    return (
        <>
            <div style={{ display: pathname === "/" ? "block" : "none" }}>
                <Home />
            </div>
            <div style={{ display: pathname === "/seller" ? "block" : "none" }}>
                <SellerPage />
            </div>
        </>
    );
}
