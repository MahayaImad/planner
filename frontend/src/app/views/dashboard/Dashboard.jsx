import { useEffect, useState } from "react";
import Grid from "@mui/material/Grid2";
import Card from "@mui/material/Card";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Icon from "@mui/material/Icon";
import Button from "@mui/material/Button";
import { styled, useTheme } from "@mui/material/styles";
import { useNavigate } from "react-router-dom";
import {
  professeursApi, matieresApi, sallesApi, classesApi, edtApi,
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
  const [counts, setCounts] = useState({ professeurs: 0, matieres: 0, salles: 0, classes: 0, edts: 0 });

  useEffect(() => {
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
  }, []);

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
          <Card sx={{ p: 3, height: "100%" }}>
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
    </ContentBox>
  );
}
