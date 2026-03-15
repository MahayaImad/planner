/**
 * Inscription en 2 étapes :
 *  1. Informations de l'école
 *  2. Compte administrateur
 */
import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Formik } from "formik";
import * as Yup from "yup";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid2";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import Icon from "@mui/material/Icon";
import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Button from "@mui/material/Button";
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
  padding: "2rem 1rem",
  "& .card": {
    maxWidth: 640,
    width: "100%",
    borderRadius: 12,
  },
}));

const WILAYAS = [
  "Adrar","Chlef","Laghouat","Oum El Bouaghi","Batna","Béjaïa","Biskra","Béchar",
  "Blida","Bouira","Tamanrasset","Tébessa","Tlemcen","Tiaret","Tizi Ouzou","Alger",
  "Djelfa","Jijel","Sétif","Saïda","Skikda","Sidi Bel Abbès","Annaba","Guelma",
  "Constantine","Médéa","Mostaganem","M'Sila","Mascara","Ouargla","Oran","El Bayadh",
  "Illizi","Bordj Bou Arréridj","Boumerdès","El Tarf","Tindouf","Tissemsilt",
  "El Oued","Khenchela","Souk Ahras","Tipaza","Mila","Aïn Defla","Naâma","Aïn Témouchent",
  "Ghardaïa","Relizane","Timimoun","Bordj Badji Mokhtar","Ouled Djellal","Béni Abbès",
  "In Salah","In Guezzam","Touggourt","Djanet","El M'Ghair","El Menia",
];

const schemaEcole = Yup.object().shape({
  nom: Yup.string().required("Nom de l'établissement requis"),
  email: Yup.string().email("Email invalide").required("Email requis"),
  wilaya: Yup.string().required("Wilaya requise"),
  ville: Yup.string(),
  telephone: Yup.string(),
});

const schemaAdmin = Yup.object().shape({
  prenom: Yup.string().required("Prénom requis"),
  nom: Yup.string().required("Nom requis"),
  email: Yup.string().email("Email invalide").required("Email requis"),
  mot_de_passe: Yup.string().min(6, "6 caractères minimum").required("Mot de passe requis"),
  confirmer: Yup.string()
    .oneOf([Yup.ref("mot_de_passe")], "Les mots de passe ne correspondent pas")
    .required("Confirmation requise"),
});

export default function PlannerRegister() {
  const theme = useTheme();
  const navigate = useNavigate();
  const { register } = useAuth();

  const [etape, setEtape] = useState(0);
  const [ecoleData, setEcoleData] = useState(null);
  const [erreur, setErreur] = useState(null);

  const handleEcoleSubmit = (values) => {
    setEcoleData(values);
    setEtape(1);
  };

  const handleAdminSubmit = async (values, { setSubmitting }) => {
    setErreur(null);
    try {
      await register({
        ecole: ecoleData,
        admin: {
          nom: values.nom,
          prenom: values.prenom,
          email: values.email,
          mot_de_passe: values.mot_de_passe,
        },
      });
      navigate("/dashboard");
    } catch (e) {
      setErreur(e.response?.data?.detail ?? "Erreur lors de l'inscription. Cet email est peut-être déjà utilisé.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <StyledRoot>
      <Card className="card">
        <Box p={4}>
          {/* Logo / titre */}
          <Box display="flex" alignItems="center" gap={1} mb={3}>
            <Icon color="primary" sx={{ fontSize: 32 }}>calendar_month</Icon>
            <Typography variant="h6" fontWeight={700}>Emploi du temps scolaire</Typography>
          </Box>

          <Typography variant="h5" fontWeight={700} mb={0.5}>
            Inscrire mon établissement
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Créez votre espace de gestion gratuit
          </Typography>

          <Stepper activeStep={etape} sx={{ mb: 4 }}>
            <Step><StepLabel>Établissement</StepLabel></Step>
            <Step><StepLabel>Compte administrateur</StepLabel></Step>
          </Stepper>

          {erreur && <Alert severity="error" sx={{ mb: 2 }}>{erreur}</Alert>}

          {/* Étape 1 : école */}
          {etape === 0 && (
            <Formik
              initialValues={ecoleData || { nom: "", email: "", wilaya: "", ville: "", telephone: "" }}
              validationSchema={schemaEcole}
              onSubmit={handleEcoleSubmit}
            >
              {({ values, errors, touched, handleChange, handleBlur, handleSubmit }) => (
                <form onSubmit={handleSubmit}>
                  <TextField
                    fullWidth size="small" name="nom" label="Nom de l'établissement *"
                    sx={{ mb: 2 }} value={values.nom} onBlur={handleBlur} onChange={handleChange}
                    helperText={touched.nom && errors.nom} error={Boolean(errors.nom && touched.nom)}
                  />
                  <TextField
                    fullWidth size="small" type="email" name="email" label="Email de l'établissement *"
                    sx={{ mb: 2 }} value={values.email} onBlur={handleBlur} onChange={handleChange}
                    helperText={touched.email && errors.email} error={Boolean(errors.email && touched.email)}
                  />
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid size={6}>
                      <TextField
                        select fullWidth size="small" name="wilaya" label="Wilaya *"
                        value={values.wilaya} onBlur={handleBlur} onChange={handleChange}
                        helperText={touched.wilaya && errors.wilaya} error={Boolean(errors.wilaya && touched.wilaya)}
                      >
                        {WILAYAS.map((w) => <MenuItem key={w} value={w}>{w}</MenuItem>)}
                      </TextField>
                    </Grid>
                    <Grid size={6}>
                      <TextField
                        fullWidth size="small" name="ville" label="Ville / Commune"
                        value={values.ville} onBlur={handleBlur} onChange={handleChange}
                      />
                    </Grid>
                  </Grid>
                  <TextField
                    fullWidth size="small" name="telephone" label="Téléphone"
                    sx={{ mb: 3 }} value={values.telephone} onBlur={handleBlur} onChange={handleChange}
                  />
                  <Button type="submit" variant="contained" fullWidth size="large" endIcon={<Icon>arrow_forward</Icon>}>
                    Continuer
                  </Button>
                </form>
              )}
            </Formik>
          )}

          {/* Étape 2 : admin */}
          {etape === 1 && (
            <Formik
              initialValues={{ prenom: "", nom: "", email: "", mot_de_passe: "", confirmer: "" }}
              validationSchema={schemaAdmin}
              onSubmit={handleAdminSubmit}
            >
              {({ values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit }) => (
                <form onSubmit={handleSubmit}>
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid size={6}>
                      <TextField
                        fullWidth size="small" name="prenom" label="Prénom *"
                        value={values.prenom} onBlur={handleBlur} onChange={handleChange}
                        helperText={touched.prenom && errors.prenom} error={Boolean(errors.prenom && touched.prenom)}
                      />
                    </Grid>
                    <Grid size={6}>
                      <TextField
                        fullWidth size="small" name="nom" label="Nom *"
                        value={values.nom} onBlur={handleBlur} onChange={handleChange}
                        helperText={touched.nom && errors.nom} error={Boolean(errors.nom && touched.nom)}
                      />
                    </Grid>
                  </Grid>
                  <TextField
                    fullWidth size="small" type="email" name="email" label="Email (pour connexion) *"
                    sx={{ mb: 2 }} value={values.email} onBlur={handleBlur} onChange={handleChange}
                    helperText={touched.email && errors.email} error={Boolean(errors.email && touched.email)}
                  />
                  <TextField
                    fullWidth size="small" type="password" name="mot_de_passe" label="Mot de passe *"
                    sx={{ mb: 2 }} value={values.mot_de_passe} onBlur={handleBlur} onChange={handleChange}
                    helperText={touched.mot_de_passe && errors.mot_de_passe}
                    error={Boolean(errors.mot_de_passe && touched.mot_de_passe)}
                  />
                  <TextField
                    fullWidth size="small" type="password" name="confirmer" label="Confirmer le mot de passe *"
                    sx={{ mb: 3 }} value={values.confirmer} onBlur={handleBlur} onChange={handleChange}
                    helperText={touched.confirmer && errors.confirmer}
                    error={Boolean(errors.confirmer && touched.confirmer)}
                  />
                  <Box display="flex" gap={2}>
                    <Button variant="outlined" startIcon={<Icon>arrow_back</Icon>} onClick={() => setEtape(0)}>
                      Retour
                    </Button>
                    <LoadingButton
                      type="submit" variant="contained" fullWidth size="large"
                      loading={isSubmitting} startIcon={<Icon>check_circle</Icon>}
                    >
                      Créer mon compte
                    </LoadingButton>
                  </Box>
                </form>
              )}
            </Formik>
          )}

          <Typography variant="body2" mt={3} textAlign="center">
            Déjà inscrit ?{" "}
            <NavLink to="/session/signin" style={{ color: theme.palette.primary.main, fontWeight: 600 }}>
              Se connecter
            </NavLink>
          </Typography>
        </Box>
      </Card>
    </StyledRoot>
  );
}
