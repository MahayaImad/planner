import { lazy } from "react";
import { Navigate } from "react-router-dom";

import AuthGuard from "./auth/AuthGuard";
import Loadable from "./components/Loadable";
import MatxLayout from "./components/MatxLayout/MatxLayout";
import sessionRoutes from "./views/sessions/session-routes";

const Dashboard       = Loadable(lazy(() => import("app/views/dashboard/Dashboard")));
const Parametres      = Loadable(lazy(() => import("app/views/parametres/ParametresPage")));
const Programme       = Loadable(lazy(() => import("app/views/programme/ProgrammePage")));
const Professeurs     = Loadable(lazy(() => import("app/views/professeurs/ProfesseursList")));
const Matieres        = Loadable(lazy(() => import("app/views/matieres/MatieresList")));
const Salles          = Loadable(lazy(() => import("app/views/salles/SallesList")));
const Classes         = Loadable(lazy(() => import("app/views/classes/ClassesList")));
const EdtList         = Loadable(lazy(() => import("app/views/emplois-du-temps/EdtList")));
const EdtDetail       = Loadable(lazy(() => import("app/views/emplois-du-temps/EdtDetail")));
const EdtStats        = Loadable(lazy(() => import("app/views/emplois-du-temps/EdtStatistiques")));

const routes = [
  { path: "/", element: <Navigate to="/dashboard" /> },
  {
    element: (
      <AuthGuard>
        <MatxLayout />
      </AuthGuard>
    ),
    children: [
      { path: "/dashboard",         element: <Dashboard /> },
      { path: "/parametres",        element: <Parametres /> },
      { path: "/programme",         element: <Programme /> },
      { path: "/professeurs",       element: <Professeurs /> },
      { path: "/matieres",          element: <Matieres /> },
      { path: "/salles",            element: <Salles /> },
      { path: "/classes",           element: <Classes /> },
      { path: "/emplois-du-temps",  element: <EdtList /> },
      { path: "/emplois-du-temps/:id", element: <EdtDetail /> },
      { path: "/emplois-du-temps/:id/statistiques", element: <EdtStats /> },
    ],
  },
  ...sessionRoutes,
];

export default routes;
