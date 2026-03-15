import { useRoutes } from "react-router-dom";
import CssBaseline from "@mui/material/CssBaseline";
import { SnackbarProvider } from "notistack";
import { MatxTheme } from "./components";
import SettingsProvider from "./contexts/SettingsContext";
import { AuthProvider } from "./contexts/PlannerAuthContext";
import routes from "./routes";

export default function App() {
  const content = useRoutes(routes);

  return (
    <SettingsProvider>
      <AuthProvider>
        <MatxTheme>
          <SnackbarProvider
            maxSnack={4}
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            autoHideDuration={3500}
          >
            <CssBaseline />
            {content}
          </SnackbarProvider>
        </MatxTheme>
      </AuthProvider>
    </SettingsProvider>
  );
}
