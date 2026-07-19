import { useEffect, useState, useCallback } from "react";
import { accountsApi, budgetsApi, dashboardApi, transactionsApi } from "../api/client";
import AccountList from "./AccountList";
import TransactionForm from "./TransactionForm";
import TransactionLedger from "./TransactionLedger";
import BudgetTracker from "./BudgetTracker";
import SpendingChart from "./SpendingChart";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value ?? 0);
}

const now = new Date();

export default function Dashboard() {
  const [accounts, setAccounts] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const month = now.getMonth() + 1;
  const year = now.getFullYear();

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [accRes, budgetRes, summaryRes] = await Promise.all([
        accountsApi.list(),
        budgetsApi.list(month, year),
        dashboardApi.summary(month, year),
      ]);
      setAccounts(accRes.data);
      setBudgets(budgetRes.data);
      setSummary(summaryRes.data);

      if (accRes.data.length > 0) {
        const txnLists = await Promise.all(
          accRes.data.map((a) => transactionsApi.listByAccount(a.id))
        );
        const merged = txnLists
          .flatMap((r) => r.data)
          .sort((a, b) => new Date(b.transaction_date) - new Date(a.transaction_date))
          .slice(0, 8);
        setTransactions(merged);
      } else {
        setTransactions([]);
      }
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const netFlow = summary?.income_vs_expense?.net_cash_flow ?? 0;

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">
            {now.toLocaleDateString("en-IN", { month: "long", year: "numeric" })}
          </p>
          <h1 className="page-title">Your money, at a glance</h1>
        </div>
      </div>

      <div className="summary-grid">
        <div className="summary-card">
          <p className="summary-label">Income this month</p>
          <p className="summary-value positive">{formatCurrency(summary?.income_vs_expense?.income)}</p>
        </div>
        <div className="summary-card">
          <p className="summary-label">Expenses this month</p>
          <p className="summary-value negative">{formatCurrency(summary?.income_vs_expense?.expense)}</p>
        </div>
        <div className="summary-card">
          <p className="summary-label">Net cash flow</p>
          <p className={`summary-value ${netFlow >= 0 ? "positive" : "negative"}`}>
            {formatCurrency(netFlow)}
          </p>
          <p className="summary-delta">
            savings rate {summary?.income_vs_expense?.savings_rate_pct ?? 0}%
          </p>
        </div>
      </div>

      <div className="stack" style={{ marginBottom: 20 }}>
        <AccountList accounts={accounts} onAccountCreated={loadAll} />
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        <TransactionForm accounts={accounts} onTransactionAdded={loadAll} />
        <SpendingChart data={summary?.spending_by_category} />
      </div>

      <div className="grid-2">
        <TransactionLedger transactions={transactions} />
        <BudgetTracker budgets={budgets} month={month} year={year} onBudgetCreated={loadAll} />
      </div>

      {loading && (
        <p style={{ color: "var(--color-muted)", fontSize: 12, marginTop: 24 }}>Refreshing…</p>
      )}
    </div>
  );
}
