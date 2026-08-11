import Header from "./layouts/Header";
import BottomTabBar from "./layouts/BottomTabBar";
import Home from "./pages/Home";
import "./styles/index.css";

function App() {
    return (
        <>
            <Header />
            <Home />
            <BottomTabBar />
        </>
    );
}

export default App;