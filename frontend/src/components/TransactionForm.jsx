import { useState } from "react";
import { transactionsApi } from "../api/client";

const CATEGORIES = ["food", "transport", "utilities", "entertainment", "health", "salary", "other"];

function todayIso() {
  return new Date().toISOString().slice(0, 16);
}

export default function TransactionForm({ accounts, onTransactionAdded }) {
  const [form, setForm] = useState({
    account_id: accounts[0]?.id ?? "",
    amount: "",
    type: "debit",
    category: "food",
    description: "",
    merchant: "",
    transaction_date: todayIso(),
  });
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const update = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFeedback(null);
    try {
      await transactionsApi.create({
        ...form,
        account_id: Number(form.account_id),
        amount: Number(form.amount),
        transaction_date: new Date(form.transaction_date).toISOString(),
      });
      setFeedback({ type: "ok", message: "Transaction recorded." });
      setForm((prev) => ({ ...prev, amount: "", description: "", merchant: "" }));
      onTransactionAdded?.();
    } catch (err) {
      setFeedback({ type: "error", message: err.response?.data?.detail || "Could not record the transaction." });
    } finally {
      setSubmitting(false);
    }
  };

  if (accounts.length === 0) {
    return (
      <div className="card card-pad">
        <p className="section-label">Add a transaction</p>
        <div className="empty-state">
          <p className="empty-title">Add an account first</p>
          <p>Transactions need somewhere to belong.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card card-pad">
      <p className="section-label">Add a transaction</p>

      <div className="form-toggle">
        <span
          className={`toggle-option ${form.type === "debit" ? "active debit" : ""}`}
          onClick={() => setForm((p) => ({ ...p, type: "debit" }))}
        >
          Money out
        </span>
        <span
          className={`toggle-option ${form.type === "credit" ? "active credit" : ""}`}
          onClick={() => setForm((p) => ({ ...p, type: "credit" }))}
        >
          Money in
        </span>
      </div>

      <form onSubmit={handleSubmit} className="form-grid">
        <div className="field">
          <label htmlFor="account_id">Account</label>
          <select id="account_id" value={form.account_id} onChange={update("account_id")} required>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>{a.account_name}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="amount">Amount (₹)</label>
          <input id="amount" type="number" min="0.01" step="0.01" value={form.amount} onChange={update("amount")} required />
        </div>
        <div className="field">
          <label htmlFor="category">Category</label>
          <select id="category" value={form.category} onChange={update("category")}>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c[0].toUpperCase() + c.slice(1)}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="transaction_date">Date</label>
          <input id="transaction_date" type="datetime-local" value={form.transaction_date} onChange={update("transaction_date")} required />
        </div>
        <div className="field">
          <label htmlFor="merchant">Merchant (optional)</label>
          <input id="merchant" placeholder="e.g. Swiggy" value={form.merchant} onChange={update("merchant")} />
        </div>
        <div className="field">
          <label htmlFor="description">Note (optional)</label>
          <input id="description" placeholder="e.g. Team lunch" value={form.description} onChange={update("description")} />
        </div>

        {feedback && (
          <p
            className="field-span-2"
            style={{ margin: 0, fontSize: 13, color: feedback.type === "ok" ? "var(--color-success)" : "var(--color-danger)" }}
          >
            {feedback.message}
          </p>
        )}

        <button className="btn btn-primary field-span-2" type="submit" disabled={submitting}>
          {submitting ? "Recording…" : "Record transaction"}
        </button>
      </form>
    </div>
  );
}
