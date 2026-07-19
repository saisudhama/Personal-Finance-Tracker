import { useState } from "react";
import { budgetsApi } from "../api/client";

const CATEGORIES = ["food", "transport", "utilities", "entertainment", "health", "other"];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value ?? 0);
}

function statusFor(utilizationPct) {
  if (utilizationPct >= 100) return "over";
  if (utilizationPct >= 80) return "warn";
  return "ok";
}

export default function BudgetTracker({ budgets, month, year, onBudgetCreated }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ category: "food", monthly_limit: "", month, year });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const update = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await budgetsApi.create({ ...form, monthly_limit: Number(form.monthly_limit), month, year });
      setForm({ category: "food", monthly_limit: "", month, year });
      setShowForm(false);
      onBudgetCreated?.();
    } catch (err) {
      setError(err.response?.data?.detail || "That budget may already exist for this month.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card card-pad">
      <div className="page-header" style={{ marginBottom: 18 }}>
        <p className="section-label" style={{ margin: 0 }}>Budgets this month</p>
        <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancel" : "+ Set budget"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="form-grid" style={{ marginBottom: 22 }}>
          <div className="field">
            <label htmlFor="budget_category">Category</label>
            <select id="budget_category" value={form.category} onChange={update("category")}>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c[0].toUpperCase() + c.slice(1)}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="monthly_limit">Monthly limit (₹)</label>
            <input id="monthly_limit" type="number" min="1" step="1" value={form.monthly_limit} onChange={update("monthly_limit")} required />
          </div>
          {error && <p style={{ color: "var(--color-danger)", fontSize: 13, gridColumn: "span 2", margin: 0 }}>{error}</p>}
          <button className="btn btn-primary field-span-2" type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Save budget"}
          </button>
        </form>
      )}

      {budgets.length === 0 ? (
        <div className="empty-state">
          <p className="empty-title">No budgets set</p>
          <p>Set a limit per category to get 80% and 100% alerts.</p>
        </div>
      ) : (
        budgets.map((b) => {
          const pct = Math.min(b.utilization_pct ?? 0, 100);
          const status = statusFor(b.utilization_pct ?? 0);
          return (
            <div className="budget-row" key={b.id}>
              <div className="budget-top">
                <span className="budget-category">{b.category}</span>
                <span className="budget-figures">
                  {formatCurrency(b.spent)} / {formatCurrency(b.monthly_limit)}
                </span>
              </div>
              <div className="budget-track">
                <div className={`budget-fill ${status}`} style={{ width: `${pct}%` }} />
              </div>
              {status === "warn" && <span className="budget-alert-tag warn">80% reached</span>}
              {status === "over" && <span className="budget-alert-tag over">Budget exceeded</span>}
            </div>
          );
        })
      )}
    </div>
  );
}
