import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

// Attach the JWT to every request once the user is logged in
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If the token expires/invalidates, bounce back to a clean logged-out state
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(error);
  }
);

export default client;

// ---------- Convenience API calls ----------

export const authApi = {
  login: (email, password) => client.post("/auth/login", { email, password }),
  register: (payload) => client.post("/auth/register", payload),
};

export const accountsApi = {
  list: () => client.get("/accounts/"),
  create: (payload) => client.post("/accounts/", payload),
  remove: (id) => client.delete(`/accounts/${id}`),
};

export const transactionsApi = {
  create: (payload) => client.post("/transactions/", payload),
  listByAccount: (accountId) => client.get(`/transactions/account/${accountId}`),
};

export const budgetsApi = {
  list: (month, year) => client.get("/budgets/", { params: { month, year } }),
  create: (payload) => client.post("/budgets/", payload),
};

export const dashboardApi = {
  summary: (month, year) => client.get("/dashboard/summary", { params: { month, year } }),
};
