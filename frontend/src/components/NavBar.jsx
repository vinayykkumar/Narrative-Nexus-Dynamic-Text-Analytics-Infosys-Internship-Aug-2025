import { Link, useLocation } from "react-router-dom";
import "./navbar.css";

export default function NavBar() {
  const { pathname } = useLocation();
  const isActive = (p) => (pathname === p ? "nav-link active" : "nav-link");

  return (
    <header className="nav">
      <div className="nav-inner">
        <Link to="/" className="brand">
          <span className="brand-dot" />
          <span className="brand-name">SmartInsights</span>
        </Link>

        <nav className="nav-links">
          <Link to="/" className={isActive("/")}>Home</Link>
          <Link to="/analyzer" className={isActive("/analyzer")}>Analyze</Link>
          <Link to="/docs" className={isActive("/docs")}>Docs</Link>
        </nav>

        <div className="nav-cta">
          <Link to="/analyzer" className="nav-btn">Start Analysis</Link>
        </div>
      </div>
    </header>
  );
}
