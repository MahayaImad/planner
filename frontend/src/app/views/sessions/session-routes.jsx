import { lazy } from "react";

const NotFound       = lazy(() => import("./NotFound"));
const PlannerLogin   = lazy(() => import("./login/PlannerLogin"));
const PlannerRegister = lazy(() => import("./register/PlannerRegister"));

const sessionRoutes = [
  { path: "/session/signup",  element: <PlannerRegister /> },
  { path: "/session/signin",  element: <PlannerLogin /> },
  { path: "*",                element: <NotFound /> },
];

export default sessionRoutes;
