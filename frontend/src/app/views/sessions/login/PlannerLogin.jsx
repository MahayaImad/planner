import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Formik } from "formik";
import * as Yup from "yup";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid2";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import Icon from "@mui/material/Icon";
import styled from "@mui/material/styles/styled";
import useTheme from "@mui/material/styles/useTheme";
import LoadingButton from "@mui/lab/LoadingButton";
import useAuth from "app/hooks/useAuth";

const StyledRoot = styled("div")(() => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  backgroundColor: "#1A2038",
  minHeight: "100vh",
  "& .card": {
    maxWidth: 860,
    width: "100%",
    margin: "1rem",
    display: "flex",
    borderRadius: 12,
    overflow: "hidden",
  },
}));

const BrandBox = styled(Box)(() => ({
  background: "linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  padding: "3rem 2rem",
  color: "white",
}));

const FormBox = styled(Box)(() => ({
  padding: "3rem 2rem",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
}));

const validationSchema = Yup.object().shape({
  email: Yup.string().email("Email invalide").required("Email requis"),
  mot_de_passe: Yup.string().min(6, "6 caractères minimum").required("Mot de passe requis"),
});

export default function PlannerLogin() {
  const theme = useTheme();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [erreur, setErreur] = useState(null);

  const handleSubmit = async (values, { setSubmitting }) => {
    setErreur(null);
    try {
      await login(values.email, values.mot_de_passe);
      navigate("/dashboard");
    } catch {
      setErreur("Email ou mot de passe incorrect.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <StyledRoot>
      <Card className="card">
        <Grid container sx={{ width: "100%" }}>
          {/* Panneau gauche — branding */}
          <Grid size={{ xs: 0, md: 5 }} sx={{ display: { xs: "none", md: "block" } }}>
            <BrandBox height="100%">
              <Icon sx={{ fontSize: 64, mb: 2, opacity: 0.9 }}>calendar_month</Icon>
              <Typography variant="h5" fontWeight={700} textAlign="center" mb={1}>
                Emploi du temps scolaire
              </Typography>
              <Typography variant="body2" textAlign="center" sx={{ opacity: 0.8 }}>
                Planification automatique par intelligence artificielle pour les établissements algériens
              </Typography>
            </BrandBox>
          </Grid>

          {/* Panneau droit — formulaire */}
          <Grid size={{ xs: 12, md: 7 }}>
            <FormBox>
              <Typography variant="h5" fontWeight={700} mb={0.5}>
                Connexion
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                Accédez à votre espace de gestion
              </Typography>

              {erreur && <Alert severity="error" sx={{ mb: 2 }}>{erreur}</Alert>}

              <Formik
                initialValues={{ email: "", mot_de_passe: "" }}
                validationSchema={validationSchema}
                onSubmit={handleSubmit}
              >
                {({ values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit }) => (
                  <form onSubmit={handleSubmit}>
                    <TextField
                      fullWidth size="small" type="email" name="email" label="Adresse email"
                      variant="outlined" onBlur={handleBlur} value={values.email}
                      onChange={handleChange}
                      helperText={touched.email && errors.email}
                      error={Boolean(errors.email && touched.email)}
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth size="small" name="mot_de_passe" type="password" label="Mot de passe"
                      variant="outlined" onBlur={handleBlur} value={values.mot_de_passe}
                      onChange={handleChange}
                      helperText={touched.mot_de_passe && errors.mot_de_passe}
                      error={Boolean(errors.mot_de_passe && touched.mot_de_passe)}
                      sx={{ mb: 3 }}
                    />
                    <LoadingButton
                      type="submit" variant="contained" fullWidth size="large"
                      loading={isSubmitting}
                    >
                      Se connecter
                    </LoadingButton>
                  </form>
                )}
              </Formik>

              <Typography variant="body2" mt={3} textAlign="center">
                Pas encore de compte ?{" "}
                <NavLink to="/session/signup" style={{ color: theme.palette.primary.main, fontWeight: 600 }}>
                  Inscrire mon établissement
                </NavLink>
              </Typography>
            </FormBox>
          </Grid>
        </Grid>
      </Card>
    </StyledRoot>
  );
}
