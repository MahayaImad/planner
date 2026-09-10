import { useEffect, useState } from "react";
import Grid from "@mui/material/Grid2";
import Card from "@mui/material/Card";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Icon from "@mui/material/Icon";
import Button from "@mui/material/Button";
import { styled, useTheme } from "@mui/material/styles";
import { useNavigate } from "react-router-dom";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import LoadingButton from "@mui/lab/LoadingButton";
import { useSnackbar } from "notistack";
import {
  professeursApi, matieresApi, sallesApi, classesApi, edtApi, demoApi,
} from "app/services/api";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

const StatCard = styled(Card)(({ color }) => ({
  padding: "1.5rem",
  display: "flex",
  alignItems: "center",
  gap: "1rem",
  borderLeft: `4px solid ${color}`,
  transition: "box-shadow 0.2s",
  "&:hover": { boxShadow: "0 4px 20px rgba(0,0,0,0.15)" },
}));

const IconCircle = styled(Box)(({ color }) => ({
  width: 56,
  height: 56,
  borderRadius: "50%",
  backgroundColor: `${color}22`,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  flexShrink: 0,
  "& .MuiIcon-root": { color, fontSize: "1.8rem" },
}));

const STATS = [
  { label: "Professeurs", icon: "person", color: "#1976d2", path: "/professeurs" },
  { label: "Matières", icon: "menu_book", color: "#388e3c", path: "/matieres" },
  { label: "Salles", icon: "meeting_room", color: "#f57c00", path: "/salles" },
  { label: "Classes", icon: "school", color: "#7b1fa2", path: "/classes" },
  { label: "Emplois du temps", icon: "calendar_today", color: "#c62828", path: "/emplois-du-temps" },
];

export default function Dashboard() {
  const theme = useTheme();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [counts, setCounts] = useState({ professeurs: 0, matieres: 0, salles: 0, classes: 0, edts: 0 });
  const [demo, setDemo] = useState(null);
  const [confirmation, setConfirmation] = useState(false);
  const [chargement, setChargement] = useState(false);

  const rafraichir = () =>
    Promise.all([
      professeursApi.liste(),
      matieresApi.liste(),
      sallesApi.liste(),
      classesApi.liste(),
      edtApi.liste(),
    ]).then(([p, m, s, c, e]) => {
      setCounts({
        professeurs: p.data.length,
        matieres: m.data.length,
        salles: s.data.length,
        classes: c.data.length,
        edts: e.data.length,
      });
    }).catch(() => {});

  useEffect(() => {
    rafraichir();
    demoApi.apercu().then(({ data }) => setDemo(data)).catch(() => {});
  }, []);

  /** Installe le jeu de démonstration, après confirmation si nécessaire. */
  const chargerDemo = async () => {
    setChargement(true);
    try {
      const { data } = await demoApi.charger(demo?.etablissement_deja_peuple);
      enqueueSnackbar(data.message, { variant: "success" });
      setConfirmation(false);
      await rafraichir();
      const { data: apercu } = await demoApi.apercu();
      setDemo(apercu);
      navigate("/emplois-du-temps");
    } catch (e) {
      enqueueSnackbar(
        e.response?.data?.detail ?? "Le chargement a échoué",
        { variant: "error" },
      );
    } finally {
      setChargement(false);
    }
  };

  const values = [counts.professeurs, counts.matieres, counts.salles, counts.classes, counts.edts];

  return (
    <ContentBox>
      <Box mb={3}>
        <Typography variant="h5" fontWeight={600}>
          Tableau de bord
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Vue d'ensemble de votre établissement scolaire
        </Typography>
      </Box>

      {/* Stat cards */}
      <Grid container spacing={3} mb={4}>
        {STATS.map((s, i) => (
          <Grid key={s.label} size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }}>
            <StatCard color={s.color} onClick={() => navigate(s.path)} sx={{ cursor: "pointer" }}>
              <IconCircle color={s.color}>
                <Icon>{s.icon}</Icon>
              </IconCircle>
              <Box>
                <Typography variant="h4" fontWeight={700} color={s.color}>
                  {values[i]}
                </Typography>
                <Typography variant="body2" color="text.secondary" noWrap>
                  {s.label}
                </Typography>
              </Box>
            </StatCard>
          </Grid>
        ))}
      </Grid>

      {/* Quick-start checklist */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Guide de démarrage rapide
            </Typography>
            {[
              { step: 1, text: "Ajouter les matières enseignées", done: counts.matieres > 0, path: "/matieres" },
              { step: 2, text: "Enregistrer les salles de classe", done: counts.salles > 0, path: "/salles" },
              { step: 3, text: "Créer les classes (niveaux)", done: counts.classes > 0, path: "/classes" },
              { step: 4, text: "Ajouter les professeurs et leurs disponibilités", done: counts.professeurs > 0, path: "/professeurs" },
              { step: 5, text: "Générer un emploi du temps automatique", done: counts.edts > 0, path: "/emplois-du-temps" },
            ].map(({ step, text, done, path }) => (
              <Box
                key={step}
                display="flex"
                alignItems="center"
                gap={2}
                py={1.5}
                sx={{ borderBottom: "1px solid", borderColor: "divider", "&:last-child": { borderBottom: 0 } }}
              >
                <Box
                  sx={{
                    width: 32, height: 32, borderRadius: "50%",
                    bgcolor: done ? "success.main" : "action.hover",
                    display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                  }}
                >
                  {done
                    ? <Icon sx={{ color: "white", fontSize: 18 }}>check</Icon>
                    : <Typography variant="caption" fontWeight={700} color="text.secondary">{step}</Typography>
                  }
                </Box>
                <Typography
                  variant="body2"
                  flex={1}
                  sx={{ textDecoration: done ? "line-through" : "none", color: done ? "text.disabled" : "text.primary" }}
                >
                  {text}
                </Typography>
                {!done && (
                  <Button size="small" variant="outlined" onClick={() => navigate(path)}>
                    Commencer
                  </Button>
                )}
              </Box>
            ))}
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          {/* Jeu de démonstration : permet de découvrir la plateforme
              et de lancer une génération sans rien saisir. */}
          <Card sx={{ p: 3, mb: 3, borderTop: "4px solid #0288d1" }}>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Icon sx={{ color: "#0288d1" }}>science</Icon>
              <Typography variant="h6" fontWeight={600}>
                Découvrir avec un exemple
              </Typography>
            </Box>

            {demo ? (
              <>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  {demo.description}
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={0.75} mb={2}>
                  <Chip size="small" label={`${demo.classes} divisions`} />
                  <Chip size="small" label={`${demo.professeurs} enseignants`} />
                  <Chip size="small" label={`${demo.matieres} matières`} />
                  <Chip size="small" label={`${demo.salles} salles`} />
                  <Chip size="small" label={`${demo.lignes_programme} lignes de programme`} />
                  <Chip size="small" color="primary" variant="outlined"
                        label={`${demo.lecons_a_placer} leçons à placer`} />
                </Box>

                {demo.etablissement_deja_peuple && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    Votre établissement contient déjà des données. Les
                    installer effacera matières, salles, classes,
                    enseignants et emplois du temps existants.
                  </Alert>
                )}

                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<Icon>auto_awesome</Icon>}
                  color={demo.etablissement_deja_peuple ? "warning" : "info"}
                  onClick={() => setConfirmation(true)}
                >
                  {demo.etablissement_deja_peuple
                    ? "Remplacer par l'exemple"
                    : "Installer le jeu d'exemple"}
                </Button>
                <Typography variant="caption" color="text.secondary"
                            display="block" mt={1}>
                  Rien n'est écrit tant que vous n'avez pas confirmé.
                </Typography>
              </>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Chargement…
              </Typography>
            )}
          </Card>

          <Card sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Accès rapide
            </Typography>
            <Box display="flex" flexDirection="column" gap={1.5}>
              {[
                { label: "Nouveau professeur", icon: "person_add", path: "/professeurs", color: "#1976d2" },
                { label: "Nouvelle matière", icon: "add_circle", path: "/matieres", color: "#388e3c" },
                { label: "Nouvelle salle", icon: "add_business", path: "/salles", color: "#f57c00" },
                { label: "Générer un emploi du temps", icon: "auto_fix_high", path: "/emplois-du-temps", color: "#c62828" },
              ].map(({ label, icon, path, color }) => (
                <Button
                  key={label}
                  variant="outlined"
                  startIcon={<Icon>{icon}</Icon>}
                  fullWidth
                  sx={{
                    justifyContent: "flex-start", borderColor: color,
                    color, "&:hover": { bgcolor: `${color}11`, borderColor: color },
                  }}
                  onClick={() => navigate(path)}
                >
                  {label}
                </Button>
              ))}
            </Box>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={confirmation} onClose={() => setConfirmation(false)}
              maxWidth="sm" fullWidth>
        <DialogTitle>
          {demo?.etablissement_deja_peuple
            ? "Remplacer les données existantes ?"
            : "Installer le jeu de démonstration ?"}
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" mb={2}>
            Cette action crée dans votre établissement :
          </Typography>
          <Box component="ul" sx={{ pl: 3, m: 0, "& li": { mb: 0.5 } }}>
            <li><b>{demo?.matieres} matières</b>, dont plusieurs exigeant une
                salle spécialisée (laboratoire, informatique, terrain)</li>
            <li><b>{demo?.salles} salles</b> de types différents</li>
            <li><b>{demo?.classes} divisions</b> de {demo?.heures_par_classe} h
                hebdomadaires, chacune avec sa salle attitrée</li>
            <li><b>{demo?.professeurs} enseignants</b>, avec leurs plafonds de
                service et leurs indisponibilités</li>
            <li>le <b>programme annuel complet</b> — {demo?.lignes_programme} lignes,
                dédoublements en demi-groupes compris</li>
            <li><b>{demo?.fenetres_pedagogiques} journées d'inspection</b> et la
                fermeture du mardi après-midi</li>
            <li>un emploi du temps vide, prêt à générer</li>
          </Box>

          <Alert severity="info" sx={{ mt: 2 }}>
            C'est un établissement réel, pas une maquette : la génération
            demande deux à cinq minutes de calcul. Elle se suit en direct
            et peut être arrêtée à tout moment.
          </Alert>

          {demo?.etablissement_deja_peuple && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Vos matières, salles, classes, enseignants et emplois du
              temps actuels seront <b>définitivement supprimés</b>.
            </Alert>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setConfirmation(false)} color="inherit">
            Annuler
          </Button>
          <LoadingButton
            variant="contained"
            color={demo?.etablissement_deja_peuple ? "error" : "primary"}
            loading={chargement}
            onClick={chargerDemo}
          >
            {demo?.etablissement_deja_peuple
              ? "Effacer et installer"
              : "Installer"}
          </LoadingButton>
        </DialogActions>
      </Dialog>
    </ContentBox>
  );
}
