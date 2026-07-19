import { useState } from "react";
import "./styles/theme.css";
import Dashboard from "./components/Dashboard";
import AuthGate from "./components/AuthGate";

const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "accounts", label: "Accounts" },
  { key: "budgets", label: "Budgets" },
];

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("access_token"));
  const [active, setActive] = useState("dashboard");

  if (!isAuthenticated) {
    return <AuthGate onAuthenticated={() => setIsAuthenticated(true)} />;
  }

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setIsAuthenticated(false);
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">Ledger</span>
        </div>
        <p className="brand-sub" style={{ marginTop: -24 }}>Personal Finance</p>

        <ul className="nav-list">
          {NAV_ITEMS.map((item) => (
            <li
              key={item.key}
              className={`nav-item ${active === item.key ? "active" : ""}`}
              onClick={() => setActive(item.key)}
            >
              <span className="dot" />
              {item.label}
            </li>
          ))}
        </ul>

        <div className="sidebar-footer">
          <div className="nav-item" onClick={handleLogout} style={{ marginBottom: 12 }}>
            <span className="dot" />
            Log out
          </div>
          POC-02 · Phase 1
        </div>
      </aside>

      <main className="main">
        <Dashboard />
      </main>
    </div>
  );
}
