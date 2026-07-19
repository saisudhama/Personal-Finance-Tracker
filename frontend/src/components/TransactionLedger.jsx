function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value ?? 0);
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short" });
}

export default function TransactionLedger({ transactions }) {
  return (
    <div className="card card-pad">
      <p className="section-label">Recent activity</p>
      {transactions.length === 0 ? (
        <div className="empty-state">
          <p className="empty-title">No transactions yet</p>
          <p>Everything you record will show up here, most recent first.</p>
        </div>
      ) : (
        <div>
          {transactions.map((t) => (
            <div className="ledger-row" key={t.id}>
              <span className="ledger-date">{formatDate(t.transaction_date)}</span>
              <div className="ledger-desc">
                <span className="ledger-merchant">{t.merchant || t.description || "Transaction"}</span>
                <span className="ledger-category">{t.category}</span>
              </div>
              <span className={`ledger-amount ${t.type}`}>
                {t.type === "credit" ? "+" : "−"}{formatCurrency(t.amount)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
