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
  // École et compte admin voyagent dans le corps de la requête : passer
  // le mot de passe en paramètre d'URL le ferait apparaître dans les
  // journaux du serveur et l'historique du navigateur.
  inscrire: (ecole, admin) => api.post("/auth/inscrire", { ecole, admin }),
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

  // Contrôle des données avant calcul : le responsable corrige ses
  // saisies sans attendre la fin d'une résolution vouée à l'échec.
  diagnostic: (id, data) => api.post(`/emplois-du-temps/${id}/diagnostic`, data),

  // La génération est asynchrone : /generer met en file et rend la
  // main, le client interroge ensuite l'avancement de la tâche.
  generer: (id, data) => api.post(`/emplois-du-temps/${id}/generer`, data),
  taches: (id) => api.get(`/emplois-du-temps/${id}/taches`),
  tache: (id, tacheId) => api.get(`/emplois-du-temps/${id}/taches/${tacheId}`),
  annulerTache: (id, tacheId) =>
    api.delete(`/emplois-du-temps/${id}/taches/${tacheId}`),
};

export default api;
