/**
 * Statistiques d'un emploi du temps : service et trous de chaque
 * professeur, charge des divisions, taux d'occupation des séances.
 *
 * Les chiffres sont recalculés par le serveur à partir des leçons
 * enregistrées, pas lus dans le compte rendu de la génération : un
 * emploi du temps retouché à la main affiche ce qu'il est devenu.
 */
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Icon from "@mui/material/Icon";
import IconButton from "@mui/material/IconButton";
import LinearProgress from "@mui/material/LinearProgress";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import { styled } from "@mui/material/styles";
import { edtApi } from "app/services/api";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

/** Une valeur mise en avant, avec sa légende. */
function Indicateur({ valeur, libelle, aide, couleur }) {
  return (
    <Card sx={{ p: 2, flex: "1 1 150px", minWidth: 150 }}>
      <Tooltip title={aide || ""} placement="top">
        <Box>
          <Typography variant="h4" fontWeight={700} color={couleur}>
            {valeur}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {libelle}
          </Typography>
        </Box>
      </Tooltip>
    </Card>
  );
}

/** Distribution « 4 h : 12 journées » rendue en puces. */
function Charges({ charges }) {
  const entrees = Object.entries(charges || {}).sort(
    (a, b) => Number(a[0]) - Number(b[0]));
  if (!entrees.length) return <span>—</span>;
  return (
    <Box display="flex" gap={0.5} flexWrap="wrap">
      {entrees.map(([heures, jours]) => (
        <Chip key={heures} size="small" variant="outlined"
              label={`${heures} h × ${jours}`}
              color={Number(heures) >= 6 ? "error"
                   : Number(heures) === 5 ? "warning" : "default"} />
      ))}
    </Box>
  );
}

export default function EdtStatistiques() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [erreur, setErreur] = useState(null);

  const charger = useCallback(async () => {
    try {
      const { data } = await edtApi.statistiques(id);
      setStats(data);
    } catch (e) {
      setErreur(e.response?.data?.detail || "Statistiques indisponibles.");
    }
  }, [id]);

  useEffect(() => { charger(); }, [charger]);

  if (erreur) {
    return <ContentBox><Alert severity="error">{erreur}</Alert></ContentBox>;
  }
  if (!stats) {
    return (
      <ContentBox>
        <Box display="flex" justifyContent="center" py={6}>
          <CircularProgress />
        </Box>
      </ContentBox>
    );
  }

  const { totaux, resume, professeurs, classes, occupation_seances: seances } = stats;
  const lourdes = Object.entries(resume.charges_quotidiennes || {})
    .filter(([heures]) => Number(heures) >= 6)
    .reduce((total, [, jours]) => total + jours, 0);

  return (
    <ContentBox>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <IconButton onClick={() => navigate(`/emplois-du-temps/${id}`)}>
          <Icon>arrow_back</Icon>
        </IconButton>
        <Box>
          <Typography variant="h5" fontWeight={700}>Statistiques</Typography>
          <Typography variant="body2" color="text.secondary">{stats.nom}</Typography>
        </Box>
      </Box>

      {totaux.lecons === 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Cet emploi du temps ne contient encore aucune leçon.
        </Alert>
      )}
      {totaux.lecons_hors_grille > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {totaux.lecons_hors_grille} leçon(s) tombent en dehors de la grille
          horaire actuelle : la grille a changé depuis la génération. Elles ne
          sont pas comptées ci-dessous.
        </Alert>
      )}

      {/* ─────────── Vue d'ensemble ─────────── */}
      <Box display="flex" gap={2} flexWrap="wrap" mb={3}>
        <Indicateur valeur={totaux.lecons} libelle="heures placées"
                    aide="Chaque demi-groupe d'un fouj compte pour une heure d'enseignement." />
        <Indicateur valeur={totaux.professeurs} libelle="professeurs" />
        <Indicateur valeur={totaux.classes} libelle="divisions" />
        <Indicateur valeur={resume.trous_professeurs} libelle="trous professeurs"
                    couleur={resume.trous_professeurs ? "warning.main" : "success.main"}
                    aide="Heures creuses entre deux cours de la même demi-journée." />
        <Indicateur valeur={resume.trous_classes} libelle="trous élèves"
                    couleur={resume.trous_classes ? "error.main" : "success.main"}
                    aide="Une division ne devrait jamais avoir d'heure creuse." />
        <Indicateur valeur={resume.demi_journees_isolees}
                    libelle="demi-journées à 1 h"
                    aide="Un professeur se déplace pour une seule heure." />
        <Indicateur valeur={lourdes} libelle="journées à 6 h ou plus"
                    couleur={lourdes ? "warning.main" : "success.main"}
                    aide="Journées-professeur les plus chargées." />
        <Indicateur valeur={resume.matieres_a_trois_heures}
                    libelle="matières à 3 h le même jour"
                    couleur={resume.matieres_a_trois_heures ? "warning.main" : "success.main"}
                    aide="Une matière vue trois fois dans la même journée par une division." />
      </Box>

      {/* ─────────── Occupation des séances ─────────── */}
      <Card sx={{ mb: 3 }}>
        <Box p={3} pb={1}>
          <Typography variant="subtitle1" fontWeight={700}>
            Occupation des séances
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Part des divisions en cours à chaque séance, sur la semaine.
            Les séances fermées ne sont pas comptées.
          </Typography>
        </Box>
        <Box p={3} pt={2}>
          {seances.map((s) => {
            const taux = s.possible ? Math.round((100 * s.occupe) / s.possible) : 0;
            return (
              <Box key={s.debut} display="flex" alignItems="center" gap={2} mb={1}>
                <Typography variant="body2" sx={{ minWidth: 110 }}>
                  {s.debut} – {s.fin}
                </Typography>
                <LinearProgress variant="determinate" value={taux}
                                sx={{ flex: 1, height: 8, borderRadius: 4 }} />
                <Typography variant="body2" color="text.secondary"
                            sx={{ minWidth: 110, textAlign: "right" }}>
                  {s.occupe} / {s.possible} ({taux} %)
                </Typography>
              </Box>
            );
          })}
        </Box>
      </Card>

      {/* ─────────── Professeurs ─────────── */}
      <Card sx={{ mb: 3 }}>
        <Box p={3} pb={1}>
          <Typography variant="subtitle1" fontWeight={700}>
            Service des professeurs
          </Typography>
          <Typography variant="body2" color="text.secondary">
            De {resume.heures_par_professeur_min} à{" "}
            {resume.heures_par_professeur_max} heures par semaine.
          </Typography>
        </Box>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: "action.hover" }}>
                <TableCell><b>Professeur</b></TableCell>
                <TableCell align="right"><b>Heures</b></TableCell>
                <TableCell align="right"><b>Jours</b></TableCell>
                <TableCell align="right"><b>Trous</b></TableCell>
                <TableCell align="right"><b>Heures creuses</b></TableCell>
                <TableCell align="right"><b>1/2 j. à 1 h</b></TableCell>
                <TableCell align="right"><b>Max/jour</b></TableCell>
                <TableCell><b>Journées</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {professeurs.map((p) => (
                <TableRow key={p.id} hover>
                  <TableCell>{p.nom}</TableCell>
                  <TableCell align="right">{p.heures}</TableCell>
                  <TableCell align="right">{p.jours_presence}</TableCell>
                  <TableCell align="right">
                    {p.trous > 0
                      ? <Chip size="small" color="warning" label={p.trous} />
                      : "0"}
                  </TableCell>
                  <TableCell align="right">{p.heures_creuses_journee}</TableCell>
                  <TableCell align="right">{p.demi_journees_isolees}</TableCell>
                  <TableCell align="right">
                    {p.charge_max >= 6
                      ? <Chip size="small" color="error" label={`${p.charge_max} h`} />
                      : `${p.charge_max} h`}
                  </TableCell>
                  <TableCell><Charges charges={p.charges} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* ─────────── Divisions ─────────── */}
      <Card>
        <Box p={3} pb={1}>
          <Typography variant="subtitle1" fontWeight={700}>
            Charge des divisions
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Une heure de fouj compte une fois : la division n'occupe qu'un
            créneau même si deux enseignants interviennent.
          </Typography>
        </Box>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: "action.hover" }}>
                <TableCell><b>Division</b></TableCell>
                <TableCell align="right"><b>Heures</b></TableCell>
                <TableCell align="right"><b>Trous</b></TableCell>
                <TableCell align="right"><b>Journée la plus légère</b></TableCell>
                <TableCell align="right"><b>La plus chargée</b></TableCell>
                <TableCell align="right"><b>Fins tardives</b></TableCell>
                <TableCell align="right"><b>Matières doublées (max/jour)</b></TableCell>
                <TableCell align="right"><b>Matières à 3 h</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {classes.map((c) => (
                <TableRow key={c.id} hover>
                  <TableCell>{c.nom}</TableCell>
                  <TableCell align="right">{c.heures}</TableCell>
                  <TableCell align="right">
                    {c.trous > 0
                      ? <Chip size="small" color="error" label={c.trous} />
                      : "0"}
                  </TableCell>
                  <TableCell align="right">{c.charge_min} h</TableCell>
                  <TableCell align="right">{c.charge_max} h</TableCell>
                  <TableCell align="right">{c.journees_finissant_tard}</TableCell>
                  <TableCell align="right">{c.matieres_doublees_max}</TableCell>
                  <TableCell align="right">
                    {c.matieres_a_trois_heures > 0
                      ? <Chip size="small" color="warning"
                              label={c.matieres_a_trois_heures} />
                      : "0"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </ContentBox>
  );
}
