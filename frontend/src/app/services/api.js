/**
 * Instance Axios centralisée vers le backend FastAPI.
 * Le proxy Vite redirige /api → http://localhost:8000
 */
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

// Injecter le token JWT sur chaque requête
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Déconnecter si token expiré (401)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("accessToken");
      window.location.href = "/session/signin";
    }
    return Promise.reject(err);
  }
);

// ── Auth ───────────────────────────────────────────────────────────
export const authApi = {
  login: (email, mot_de_passe) =>
    api.post("/auth/connexion", { email, mot_de_passe }),
  register: (ecole, admin) =>
    api.post("/auth/inscrire", null, { params: {}, data: undefined })
      .then(() => {}) // utilisé directement via api.post ci-dessous
    ,
  inscrire: (ecoleData, adminData) =>
    api.post("/auth/inscrire", ecoleData, { params: adminData }),
  profil: () => api.get("/auth/moi"),
};

// ── Professeurs ────────────────────────────────────────────────────
export const professeursApi = {
  liste: () => api.get("/professeurs/"),
  creer: (data) => api.post("/professeurs/", data),
  modifier: (id, data) => api.patch(`/professeurs/${id}`, data),
  supprimer: (id) => api.delete(`/professeurs/${id}`),
  indisponibilites: {
    lire: (id) => api.get(`/professeurs/${id}/indisponibilites`),
    definir: (id, creneaux) =>
      api.put(`/professeurs/${id}/indisponibilites`, {
        creneaux_indisponibles: creneaux,
      }),
  },
};

// ── Matières ───────────────────────────────────────────────────────
export const matieresApi = {
  liste: () => api.get("/matieres/"),
  creer: (data) => api.post("/matieres/", data),
  modifier: (id, data) => api.patch(`/matieres/${id}`, data),
  supprimer: (id) => api.delete(`/matieres/${id}`),
};

// ── Salles ─────────────────────────────────────────────────────────
export const sallesApi = {
  liste: () => api.get("/salles/"),
  creer: (data) => api.post("/salles/", data),
  modifier: (id, data) => api.patch(`/salles/${id}`, data),
  supprimer: (id) => api.delete(`/salles/${id}`),
};

// ── Classes ────────────────────────────────────────────────────────
export const classesApi = {
  liste: () => api.get("/classes/"),
  creer: (data) => api.post("/classes/", data),
  modifier: (id, data) => api.patch(`/classes/${id}`, data),
  supprimer: (id) => api.delete(`/classes/${id}`),
};

// ── Emplois du temps ───────────────────────────────────────────────
export const edtApi = {
  liste: () => api.get("/emplois-du-temps/"),
  creer: (data) => api.post("/emplois-du-temps/", data),
  supprimer: (id) => api.delete(`/emplois-du-temps/${id}`),
  lecons: (id) => api.get(`/emplois-du-temps/${id}/lecons`),
  generer: (id, data) => api.post(`/emplois-du-temps/${id}/generer`, data),
};

export default api;
