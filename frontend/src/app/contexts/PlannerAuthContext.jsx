/**
 * Contexte d'authentification JWT branché sur notre backend FastAPI.
 * Remplace FirebaseAuthContext du template.
 */
import { createContext, useEffect, useReducer } from "react";
import axios from "axios";
import Loading from "app/components/MatxLoading";

const initialState = {
  user: null,
  isInitialized: false,
  isAuthenticated: false,
};

const setSession = (token) => {
  if (token) {
    localStorage.setItem("accessToken", token);
    axios.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    localStorage.removeItem("accessToken");
    delete axios.defaults.headers.common.Authorization;
  }
};

const isTokenValid = (token) => {
  if (!token) return false;
  try {
    // Décoder le payload JWT (base64url) sans librairie externe
    const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
    return payload.exp > Date.now() / 1000;
  } catch {
    return false;
  }
};

const reducer = (state, action) => {
  switch (action.type) {
    case "INIT":
      return { ...state, isInitialized: true, ...action.payload };
    case "LOGIN":
      return { ...state, isAuthenticated: true, user: action.payload.user };
    case "LOGOUT":
      return { ...state, isAuthenticated: false, user: null };
    default:
      return state;
  }
};

const AuthContext = createContext({ ...initialState, method: "JWT" });

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  /** Connexion d'un utilisateur existant */
  const login = async (email, mot_de_passe) => {
    const { data } = await axios.post("/api/auth/connexion", { email, mot_de_passe });
    setSession(data.access_token);
    dispatch({ type: "LOGIN", payload: { user: data.utilisateur } });
  };

  /**
   * Inscription d'une nouvelle école + compte admin.
   * Appelé depuis la page register avec { ecole: {...}, admin: {...} }
   */
  const register = async ({ ecole, admin }) => {
    const params = new URLSearchParams({
      nom: admin.nom,
      prenom: admin.prenom,
      email: admin.email,
      mot_de_passe: admin.mot_de_passe,
      role: "admin",
    });
    const { data } = await axios.post(
      `/api/auth/inscrire?${params.toString()}`,
      ecole
    );
    setSession(data.access_token);
    dispatch({ type: "LOGIN", payload: { user: data.utilisateur } });
  };

  const logout = () => {
    setSession(null);
    dispatch({ type: "LOGOUT" });
  };

  // Restauration de session au chargement
  useEffect(() => {
    (async () => {
      try {
        const token = localStorage.getItem("accessToken");
        if (token && isTokenValid(token)) {
          setSession(token);
          const { data } = await axios.get("/api/auth/moi");
          dispatch({
            type: "INIT",
            payload: { isAuthenticated: true, user: data },
          });
        } else {
          setSession(null);
          dispatch({ type: "INIT", payload: { isAuthenticated: false, user: null } });
        }
      } catch {
        dispatch({ type: "INIT", payload: { isAuthenticated: false, user: null } });
      }
    })();
  }, []);

  if (!state.isInitialized) return <Loading />;

  return (
    <AuthContext.Provider value={{ ...state, method: "JWT", login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
