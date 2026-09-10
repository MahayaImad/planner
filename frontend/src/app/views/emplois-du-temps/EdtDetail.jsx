/**
 * Détail d'un emploi du temps :
 *  - Bouton "Générer" → formulaire cours requis → appel solver
 *  - Grille hebdomadaire par classe / par prof / par salle
 */
import { Fragment, useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Icon from "@mui/material/Icon";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import {
  edtApi, professeursApi, matieresApi, sallesApi, classesApi, parametresApi,
} from "app/services/api";
import GenererDialog from "./GenererDialog";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

// Les jours et les séances viennent des réglages de l'établissement.
// Les recopier ici les faisait diverger : une leçon posée à 10:05 ne
// trouvait aucune ligne « 10:00 » et disparaissait de l'affichage,
// sans que rien ne le signale.

// Palette couleurs pour les matières (cyclique)
const PALETTE = [
  "#e3f2fd", "#fce4ec", "#f3e5f5", "#e8f5e9", "#fff3e0",
  "#e0f7fa", "#f9fbe7", "#ede7f6", "#fbe9e7", "#e8eaf6",
];
const BORDER_PALETTE = [
  "#1976d2", "#c2185b", "#7b1fa2", "#388e3c", "#f57c00",
  "#0097a7", "#afb42b", "#512da8", "#bf360c", "#283593",
];

export default function EdtDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [lecons, setLecons] = useState([]);
  const [professeurs, setProfesseurs] = useState([]);
  const [matieres, setMatieres] = useState([]);
  const [salles, setSalles] = useState([]);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [genererOpen, setGenererOpen] = useState(false);
  const [grille, setGrille] = useState(null);

  // Vue active : "classe", "professeur", "salle"
  const [vue, setVue] = useState("classe");
  const [filtreId, setFiltreId] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      // allSettled plutôt que all : si un appel secondaire échoue,
      // les leçons doivent rester affichées. Un écran vide alors que la
      // génération vient d'aboutir est le pire des retours.
      const [l, p, m, s, c, r] = await Promise.allSettled([
        edtApi.lecons(id),
        professeursApi.liste(),
        matieresApi.liste(),
        sallesApi.liste(),
        classesApi.liste(),
        parametresApi.lire(),
      ]);
      const valeur = (x, defaut) =>
        x.status === "fulfilled" ? x.value.data : defaut;

      setGrille(r.status === "fulfilled" ? r.value.data.grille : null);
      setLecons(valeur(l, []));
      setProfesseurs(valeur(p, []));
      setMatieres(valeur(m, []));
      setSalles(valeur(s, []));
      const listeClasses = valeur(c, []);
      setClasses(listeClasses);
      // Mise à jour fonctionnelle : lire filtreId ici obligerait à le
      // déclarer en dépendance, et tout changement de filtre
      // relancerait le chargement.
      if (listeClasses.length > 0) {
        setFiltreId((actuel) => actuel || String(listeClasses[0].id));
      }
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  // Changer de vue → réinitialiser le filtre
  const handleVue = (_, val) => {
    setVue(val);
    if (val === "classe" && classes.length > 0) setFiltreId(String(classes[0].id));
    if (val === "professeur" && professeurs.length > 0) setFiltreId(String(professeurs[0].id));
    if (val === "salle" && salles.length > 0) setFiltreId(String(salles[0].id));
  };

  /**
   * Leçons d'une case. Il peut y en avoir DEUX : lors d'un fouj, la
   * classe est dédoublée et suit deux cours au même créneau. N'en
   * afficher qu'une masquerait la moitié du programme.
   */
  const getLecons = (jour, heure) =>
    lecons.filter((l) => {
      if (l.heure_debut !== heure || l.jour !== jour) return false;
      if (vue === "classe") return String(l.classe_id) === filtreId;
      if (vue === "professeur") return String(l.professeur_id) === filtreId;
      if (vue === "salle") return String(l.salle_id) === filtreId;
      return false;
    });

  const JOURS = grille?.jours ?? [];
  const SEANCES = grille?.horaires ?? [];
  // Séances fermées : « (index du jour, index de séance) ».
  const fermees = new Set(
    (grille?.fermetures ?? []).flatMap(([j, ss]) => ss.map((s) => `${j}-${s}`)));

  // Heures effectivement affichées, pour le compteur sous le tableau.
  const heuresVisibles = JOURS.reduce(
    (n, jour) => n + SEANCES.reduce(
      (m, [debut]) => m + (getLecons(jour, debut).length ? 1 : 0), 0), 0);

  // Couleurs par matière
  const matiereColorIndex = {};
  matieres.forEach((m, i) => { matiereColorIndex[m.id] = i % PALETTE.length; });

  const options = {
    classe: classes,
    professeur: professeurs.map((p) => ({ id: p.id, nom: `${p.prenom} ${p.nom}` })),
    salle: salles,
  };

  return (
    <ContentBox>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Tooltip title="Retour">
          <IconButton onClick={() => navigate("/emplois-du-temps")}>
            <Icon>arrow_back</Icon>
          </IconButton>
        </Tooltip>
        <Box flex={1}>
          <Typography variant="h5" fontWeight={600}>Emploi du temps</Typography>
          <Typography variant="body2" color="text.secondary">
            {lecons.length} leçon{lecons.length !== 1 ? "s" : ""} planifiée{lecons.length !== 1 ? "s" : ""}
            {filtreId && ` · ${heuresVisibles} h pour la sélection`}
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="secondary"
          startIcon={<Icon>auto_fix_high</Icon>}
          onClick={() => setGenererOpen(true)}
        >
          Générer / Regénérer
        </Button>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
      ) : (
        <Card sx={{ overflow: "visible" }}>
          {/* Tabs de vue + sélecteur */}
          <Box sx={{ borderBottom: 1, borderColor: "divider", p: 2, display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center" }}>
            <Tabs value={vue} onChange={handleVue} variant="scrollable">
              <Tab label="Par classe" value="classe" icon={<Icon>school</Icon>} iconPosition="start" />
              <Tab label="Par professeur" value="professeur" icon={<Icon>person</Icon>} iconPosition="start" />
              <Tab label="Par salle" value="salle" icon={<Icon>meeting_room</Icon>} iconPosition="start" />
            </Tabs>
            <TextField
              select size="small" sx={{ minWidth: 200 }}
              label={vue === "classe" ? "Classe" : vue === "professeur" ? "Professeur" : "Salle"}
              value={filtreId}
              onChange={(e) => setFiltreId(e.target.value)}
            >
              {options[vue]?.map((o) => (
                <MenuItem key={o.id} value={String(o.id)}>{o.nom}</MenuItem>
              ))}
            </TextField>
          </Box>

          {/* Grille horaire */}
          {lecons.length === 0 ? (
            <Box sx={{ p: 6, textAlign: "center" }}>
              <Icon sx={{ fontSize: 48, color: "text.disabled", mb: 1 }}>event_busy</Icon>
              <Typography color="text.secondary">
                Aucune leçon. Cliquez sur "Générer" pour créer l'emploi du temps.
              </Typography>
            </Box>
          ) : (
            <Box sx={{ overflowX: "auto", p: 2 }}>
              <Box
                display="grid"
                sx={{
                  gridTemplateColumns: `80px repeat(${JOURS.length}, 1fr)`,
                  gap: "4px",
                  minWidth: 700,
                }}
              >
                {/* Header jours */}
                <Box />
                {JOURS.map((jour) => (
                  <Box key={jour} sx={{ textAlign: "center", py: 1, bgcolor: "primary.main", borderRadius: 1 }}>
                    <Typography variant="caption" fontWeight={700} color="white">
                      {jour}
                    </Typography>
                  </Box>
                ))}

                {/* Lignes par séance */}
                {SEANCES.map(([debut, fin], indexSeance) => (
                  <Fragment key={`s-${indexSeance}`}>
                    <Box display="flex" alignItems="center" justifyContent="flex-end" pr={1}>
                      <Typography variant="caption" color="text.secondary" fontWeight={600}>
                        {debut}
                        <Typography component="span" variant="caption"
                                    color="text.disabled" display="block">
                          {fin}
                        </Typography>
                      </Typography>
                    </Box>
                    {JOURS.map((jour, indexJour) => {
                      const cellules = getLecons(jour, debut);
                      const ferme = fermees.has(`${indexJour}-${indexSeance}`);
                      const l = cellules[0] ?? null;
                      const ci = l ? matiereColorIndex[l.matiere_id] ?? 0 : -1;
                      return (
                        <Box
                          key={`${jour}-${debut}`}
                          title={ferme ? "Séance fermée" : undefined}
                          sx={{
                            minHeight: 64,
                            borderRadius: 1,
                            bgcolor: l ? PALETTE[ci]
                              : ferme ? "action.disabledBackground" : "action.hover",
                            border: l ? `2px solid ${BORDER_PALETTE[ci]}` : "1px solid",
                            borderColor: l ? BORDER_PALETTE[ci] : "divider",
                            p: l ? "6px 8px" : 0,
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                            opacity: ferme && !l ? 0.5 : 1,
                          }}
                        >
                          {cellules.map((lecon, rang) => {
                            const couleur = matiereColorIndex[lecon.matiere_id] ?? 0;
                            return (
                              <Box key={lecon.id}
                                   sx={rang > 0 ? {
                                     mt: 0.75, pt: 0.75,
                                     borderTop: "1px dashed",
                                     borderColor: BORDER_PALETTE[couleur],
                                   } : undefined}>
                                <Typography
                                  variant="caption"
                                  fontWeight={700}
                                  sx={{ color: BORDER_PALETTE[couleur], lineHeight: 1.2,
                                        display: "block" }}
                                  noWrap
                                >
                                  {/* Deux leçons dans la case : demi-groupes d'un fouj. */}
                                  {cellules.length > 1 && `G${rang + 1} · `}
                                  {lecon.matiere_nom}
                                </Typography>
                                {vue !== "professeur" && (
                                  <Typography variant="caption" color="text.secondary"
                                              display="block" noWrap>
                                    {lecon.professeur_nom}
                                  </Typography>
                                )}
                                {vue !== "classe" && (
                                  <Typography variant="caption" color="text.secondary"
                                              display="block" noWrap>
                                    {lecon.classe_nom}
                                  </Typography>
                                )}
                                {vue !== "salle" && (
                                  <Chip
                                    label={lecon.salle_nom}
                                    size="small"
                                    sx={{
                                      height: 16, fontSize: 10, mt: 0.5,
                                      bgcolor: `${BORDER_PALETTE[couleur]}22`,
                                      color: BORDER_PALETTE[couleur],
                                    }}
                                  />
                                )}
                              </Box>
                            );
                          })}
                        </Box>
                      );
                    })}
                  </Fragment>
                ))}
              </Box>
            </Box>
          )}
        </Card>
      )}

      {genererOpen && (
        <GenererDialog
          edtId={id}
          onClose={() => setGenererOpen(false)}
          onSuccess={() => { setGenererOpen(false); load(); enqueueSnackbar("Emploi du temps généré !", { variant: "success" }); }}
        />
      )}
    </ContentBox>
  );
}
