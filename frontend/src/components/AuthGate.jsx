import { useState } from "react";
import { authApi } from "../api/client";

export default function AuthGate({ onAuthenticated }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [form, setForm] = useState({ name: "", email: "", phone: "", monthly_income: "", password: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const update = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (mode === "register") {
        await authApi.register({
          name: form.name,
          email: form.email,
          phone: form.phone || null,
          monthly_income: Number(form.monthly_income) || 0,
          password: form.password,
        });
        setMode("login");
        setError(null);
        setForm((prev) => ({ ...prev, password: "" }));
        return;
      }
      const res = await authApi.login(form.email, form.password);
      localStorage.setItem("access_token", res.data.access_token);
      onAuthenticated();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Check your details and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "var(--color-bg)" }}>
      <div className="card card-pad" style={{ width: 380 }}>
        <p className="page-eyebrow">Personal Finance Tracker</p>
        <h1 className="page-title" style={{ fontSize: 26, marginBottom: 20 }}>
          {mode === "login" ? "Welcome back" : "Create your account"}
        </h1>

        <form onSubmit={handleSubmit} className="form-grid">
          {mode === "register" && (
            <div className="field field-span-2">
              <label htmlFor="name">Full name</label>
              <input id="name" value={form.name} onChange={update("name")} required />
            </div>
          )}
          <div className="field field-span-2">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={form.email} onChange={update("email")} required />
          </div>
          {mode === "register" && (
            <>
              <div className="field">
                <label htmlFor="phone">Phone (optional)</label>
                <input id="phone" value={form.phone} onChange={update("phone")} />
              </div>
              <div className="field">
                <label htmlFor="monthly_income">Monthly income (₹)</label>
                <input id="monthly_income" type="number" min="0" value={form.monthly_income} onChange={update("monthly_income")} />
              </div>
            </>
          )}
          <div className="field field-span-2">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={form.password} onChange={update("password")} required minLength={8} />
          </div>

          {error && <p className="field-span-2" style={{ color: "var(--color-danger)", fontSize: 13, margin: 0 }}>{error}</p>}

          <button className="btn btn-primary btn-block field-span-2" type="submit" disabled={submitting}>
            {submitting ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
          </button>
        </form>

        <p style={{ fontSize: 13, color: "var(--color-muted)", marginTop: 16, textAlign: "center" }}>
          {mode === "login" ? "New here? " : "Already have an account? "}
          <span
            style={{ color: "var(--color-primary)", fontWeight: 600, cursor: "pointer" }}
            onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(null); }}
          >
            {mode === "login" ? "Create an account" : "Log in"}
          </span>
        </p>
      </div>
    </div>
  );
}
