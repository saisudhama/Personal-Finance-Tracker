import { useState } from "react";
import { accountsApi } from "../api/client";

const ACCOUNT_TYPES = ["savings", "checking", "credit"];

function formatCurrency(value, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

export default function AccountList({ accounts, onAccountCreated }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    account_name: "",
    account_type: "checking",
    balance: 0,
    currency: "INR",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (field) => (e) => {
    const value = field === "balance" ? Number(e.target.value) : e.target.value;
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await accountsApi.create(form);
      setForm({ account_name: "", account_type: "checking", balance: 0, currency: "INR" });
      setShowForm(false);
      onAccountCreated?.();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not add account. Check the details and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card card-pad">
      <div className="page-header" style={{ marginBottom: 18 }}>
        <p className="section-label" style={{ margin: 0 }}>Your accounts</p>
        <button className="btn btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancel" : "+ Add account"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="form-grid" style={{ marginBottom: 24 }}>
          <div className="field field-span-2">
            <label htmlFor="account_name">Account name</label>
            <input
              id="account_name"
              placeholder="e.g. HDFC Salary Account"
              value={form.account_name}
              onChange={handleChange("account_name")}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="account_type">Type</label>
            <select id="account_type" value={form.account_type} onChange={handleChange("account_type")}>
              {ACCOUNT_TYPES.map((t) => (
                <option key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="balance">Starting balance</label>
            <input id="balance" type="number" min="0" step="0.01" value={form.balance} onChange={handleChange("balance")} />
          </div>
          {error && <p style={{ color: "var(--color-danger)", fontSize: 13, gridColumn: "span 2", margin: 0 }}>{error}</p>}
          <button className="btn btn-primary field-span-2" type="submit" disabled={submitting}>
            {submitting ? "Adding…" : "Add account"}
          </button>
        </form>
      )}

      {accounts.length === 0 ? (
        <div className="empty-state">
          <p className="empty-title">No accounts yet</p>
          <p>Add your first account to start tracking transactions.</p>
        </div>
      ) : (
        <div className="account-grid">
          {accounts.map((account) => (
            <div className="passbook" key={account.id}>
              <p className="passbook-type">{account.account_type}</p>
              <p className="passbook-name">{account.account_name}</p>
              <span className="passbook-balance">{formatCurrency(account.balance, account.currency)}</span>
              <span className="passbook-currency">{account.currency}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
