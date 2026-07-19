import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

const CATEGORY_COLORS = {
  food: "#C99A3E",
  transport: "#3D7A6C",
  utilities: "#6B7A75",
  entertainment: "#C1443A",
  health: "#4B8B6F",
  salary: "#1B4B43",
  other: "#A9B4AF",
};

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value ?? 0);
}

export default function SpendingChart({ data }) {
  const hasData = data && data.length > 0;

  return (
    <div className="card card-pad">
      <p className="section-label">Spending by category</p>
      {!hasData ? (
        <div className="empty-state">
          <p className="empty-title">Nothing to show yet</p>
          <p>Record a few transactions to see your breakdown.</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie
              data={data}
              dataKey="total"
              nameKey="category"
              innerRadius={60}
              outerRadius={95}
              paddingAngle={2}
            >
              {data.map((entry) => (
                <Cell key={entry.category} fill={CATEGORY_COLORS[entry.category] || "#A9B4AF"} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => formatCurrency(value)} />
            <Legend
              iconType="circle"
              formatter={(value) => <span style={{ fontSize: 12, textTransform: "capitalize" }}>{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
