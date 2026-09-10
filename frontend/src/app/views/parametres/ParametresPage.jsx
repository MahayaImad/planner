/**
 * Réglages de planification de l'établissement.
 *
 * Grille horaire, poids des contraintes souples et fenêtres pédagogiques
 * ne changent qu'une ou deux fois par an. Ils sont enregistrés ici une
 * fois pour toutes, et la génération les reprend automatiquement.
 */
import { useEffect, useState, useCallback } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Icon from "@mui/material/Icon";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import MenuItem from "@mui/material/MenuItem";
import Divider from "@mui/material/Divider";
import Slider from "@mui/material/Slider";
import ToggleButton from "@mui/material/ToggleButton";
import LoadingButton from "@mui/lab/LoadingButton";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import { parametresApi, fenetresApi, matieresApi } from "app/services/api";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

/** Poids réglables, avec ce que chacun cherche à éviter. */
const CRITERES = [
  { cle: "trous_professeurs", label: "Heure creuse d'un professeur",
    aide: "Une heure sans cours au milieu de sa journée." },
  { cle: "trous_doubles_professeurs", label: "Vide de deux heures",
    aide: "Deux heures creuses d'affilée : bien pire qu'une seule." },
  { cle: "journee_hachee_professeur", label: "Journée hachée",
    aide: "Plus d'une heure creuse dans la même journée (cours, libre, "
        + "cours, libre…). Mesuré de la première à la dernière heure de "
        + "cours, pause déjeuner comprise dans l'amplitude : une séance "
        + "libre avant midi suivie d'un cours l'après-midi compte. "
        + "Facturé par heure au-delà de la première." },
  { cle: "heure_isolee_professeur", label: "Déplacement pour une seule heure",
    aide: "Le professeur ne vient qu'une heure sur la demi-journée." },
  { cle: "jours_presence_professeurs", label: "Jour de présence",
    aide: "Chaque jour en moins est un jour libéré." },
  { cle: "recompense_permanence", label: "Permanence (récompense)",
    aide: "Bonus quand une heure creuse est comblée par de l'accueil." },
  { cle: "equite_derniere_seance", label: "Équité des fins tardives",
    aide: "Répartit les dernières séances entre les divisions." },
  { cle: "equilibrage_charge_classes", label: "Équilibre des journées",
    aide: "Évite d'alterner journées très chargées et très légères." },
  { cle: "demi_journees_travaillees_classes", label: "Demi-journée travaillée",
    aide: "Regroupe les cours sur moins de demi-journées." },
  { cle: "matieres_lourdes_apres_midi", label: "Matière lourde l'après-midi",
    aide: "Pousse les matières à fort coefficient vers le matin." },
];

export default function ParametresPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [onglet, setOnglet] = useState(0);
  const [params, setParams] = useState(null);
  const [fenetres, setFenetres] = useState([]);
  const [matieres, setMatieres] = useState([]);
  const [saving, setSaving] = useState(false);
  const [erreur, setErreur] = useState(null);
  const [nouvelle, setNouvelle] = useState({
    matiere_id: "", index_jour: 0, seances_bloquees: [], libelle: "",
  });

  const charger = useCallback(async () => {
    const [p, f, m] = await Promise.all([
      parametresApi.lire(), fenetresApi.liste(), matieresApi.liste(),
    ]);
    setParams(p.data);
    setFenetres(f.data);
    setMatieres(m.data);
  }, []);

  useEffect(() => { charger().catch(() => {}); }, [charger]);

  if (!params) return <ContentBox><Typography>Chargement…</Typography></ContentBox>;

  const { grille, ponderations } = params;
  const nbSeances = grille.horaires.length;

  const majGrille = (patch) => setParams({ ...params, grille: { ...grille, ...patch } });
  const majPoids = (cle, valeur) =>
    setParams({ ...params, ponderations: { ...ponderations, [cle]: valeur } });

  /** Une séance est-elle fermée ce jour-là ? */
  const estFermee = (jour, seance) =>
    grille.fermetures.some(([j, ss]) => j === jour && ss.includes(seance));

  const basculerFermeture = (jour, seance) => {
    const autres = grille.fermetures.filter(([j]) => j !== jour);
    const actuelles = grille.fermetures.find(([j]) => j === jour)?.[1] ?? [];
    const suivantes = actuelles.includes(seance)
      ? actuelles.filter((s) => s !== seance)
      : [...actuelles, seance].sort((a, b) => a - b);
    majGrille({
      fermetures: suivantes.length ? [...autres, [jour, suivantes]] : autres,
    });
  };

  const majHoraire = (index, position, valeur) => {
    const horaires = grille.horaires.map((h, i) =>
      i === index ? (position === 0 ? [valeur, h[1]] : [h[0], valeur]) : h);
    majGrille({ horaires });
  };

  const enregistrer = async () => {
    setSaving(true); setErreur(null);
    try {
      const { data } = await parametresApi.enregistrer(params);
      setParams(data);
      enqueueSnackbar("Réglages enregistrés", { variant: "success" });
    } catch (e) {
      setErreur(e.response?.data?.detail ?? "Enregistrement impossible");
    } finally { setSaving(false); }
  };

  const ajouterFenetre = async () => {
    setErreur(null);
    if (!nouvelle.matiere_id || !nouvelle.seances_bloquees.length) {
      setErreur("Choisissez une matière et au moins une séance à bloquer.");
      return;
    }
    try {
      await fenetresApi.creer(nouvelle);
      setNouvelle({ matiere_id: "", index_jour: 0, seances_bloquees: [], libelle: "" });
      setFenetres((await fenetresApi.liste()).data);
      enqueueSnackbar("Fenêtre ajoutée", { variant: "success" });
    } catch (e) {
      setErreur(e.response?.data?.detail ?? "Ajout impossible");
    }
  };

  const supprimerFenetre = async (id) => {
    await fenetresApi.supprimer(id);
    setFenetres((await fenetresApi.liste()).data);
  };

  const creneauxOuverts =
    grille.jours.length * nbSeances
    - grille.fermetures.reduce((n, [, ss]) => n + ss.length, 0);

  return (
    <ContentBox>
      <Box mb={3}>
        <Typography variant="h5" fontWeight={600}>Réglages de planification</Typography>
        <Typography variant="body2" color="text.secondary">
          Ces réglages s'appliquent à toutes les générations. Vous n'aurez
          plus à les saisir à chaque fois.
        </Typography>
      </Box>

      {erreur && <Alert severity="error" sx={{ mb: 2 }}>{erreur}</Alert>}

      <Card>
        <Tabs value={onglet} onChange={(_, v) => setOnglet(v)}
              sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tab label="Grille horaire" />
          <Tab label="Contraintes souples" />
          <Tab label={`Fenêtres pédagogiques (${fenetres.length})`} />
        </Tabs>

        {/* ─────────── Grille horaire ─────────── */}
        {onglet === 0 && (
          <Box p={3}>
            <Typography variant="subtitle2" fontWeight={700} mb={1}>
              Jours travaillés
            </Typography>
            <TextField
              fullWidth size="small" sx={{ mb: 3 }}
              helperText="Séparés par des virgules, dans l'ordre de la semaine."
              value={grille.jours.join(", ")}
              onChange={(e) => majGrille({
                jours: e.target.value.split(",").map((j) => j.trim()).filter(Boolean),
              })}
            />

            <Typography variant="subtitle2" fontWeight={700} mb={1}>
              Séances de la journée
            </Typography>
            <Box display="grid" sx={{
              gridTemplateColumns: "70px 1fr 1fr 130px", gap: 1.5,
              alignItems: "center", mb: 3,
            }}>
              {grille.horaires.map((h, i) => (
                <Box key={i} display="contents">
                  <Typography variant="body2" fontWeight={600}>
                    Séance {i + 1}
                  </Typography>
                  <TextField size="small" label="Début" value={h[0]}
                             onChange={(e) => majHoraire(i, 0, e.target.value)} />
                  <TextField size="small" label="Fin" value={h[1]}
                             onChange={(e) => majHoraire(i, 1, e.target.value)} />
                  <Chip size="small" variant="outlined"
                        label={grille.shifts.find(([, ss]) => ss.includes(i))?.[0] ?? "—"} />
                </Box>
              ))}
            </Box>

            <Typography variant="subtitle2" fontWeight={700} mb={0.5}>
              Fermetures
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={1.5}>
              Cliquez une case pour fermer la séance. Une séance fermée
              n'est ni remplie, ni comptée comme une heure creuse.
            </Typography>
            <Box display="grid" sx={{
              gridTemplateColumns: `120px repeat(${nbSeances}, 1fr)`,
              gap: 0.5, mb: 2, maxWidth: 720,
            }}>
              <Box />
              {Array.from({ length: nbSeances }, (_, s) => (
                <Typography key={s} variant="caption" align="center" fontWeight={700}>
                  S{s + 1}
                </Typography>
              ))}
              {grille.jours.map((jour, j) => (
                <Box key={jour} display="contents">
                  <Typography variant="body2" sx={{ alignSelf: "center" }}>{jour}</Typography>
                  {Array.from({ length: nbSeances }, (_, s) => (
                    <ToggleButton
                      key={s} size="small" value={s} selected={estFermee(j, s)}
                      onChange={() => basculerFermeture(j, s)}
                      sx={{ py: 0.5, minWidth: 0 }}
                      color={estFermee(j, s) ? "error" : "standard"}
                    >
                      {estFermee(j, s) ? "fermé" : "—"}
                    </ToggleButton>
                  ))}
                </Box>
              ))}
            </Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              {creneauxOuverts} créneaux ouverts par semaine et par division.
            </Alert>

            <Divider sx={{ my: 2 }} />
            <Box display="flex" gap={2} flexWrap="wrap">
              <TextField
                size="small" label="Présence minimale le matin" type="number"
                inputProps={{ min: 0, max: nbSeances }}
                helperText="Heures qu'une division doit suivre chaque matin."
                value={params.presence_minimale?.matin ?? 0}
                onChange={(e) => setParams({
                  ...params,
                  presence_minimale: e.target.value > 0
                    ? { ...params.presence_minimale, matin: +e.target.value }
                    : {},
                })}
              />
              <TextField
                size="small" label="Type de salle ordinaire"
                helperText="Nom du type utilisé pour les cours sans exigence."
                value={params.type_salle_ordinaire}
                onChange={(e) => setParams({ ...params, type_salle_ordinaire: e.target.value })}
              />
              <TextField
                size="small" label="Temps de calcul par défaut (s)" type="number"
                inputProps={{ min: 5, max: 3600 }}
                value={params.limite_secondes}
                onChange={(e) => setParams({ ...params, limite_secondes: +e.target.value })}
              />
            </Box>
          </Box>
        )}

        {/* ─────────── Contraintes souples ─────────── */}
        {onglet === 1 && (
          <Box p={3}>
            <Alert severity="info" sx={{ mb: 3 }}>
              Ces poids arbitrent entre des souhaits contradictoires. Un poids
              élevé signifie « évite cela en priorité » ; zéro désactive le
              critère. Ils n'empêchent jamais une génération d'aboutir.
            </Alert>

            {CRITERES.map(({ cle, label, aide }) => (
              <Box key={cle} mb={2.5}>
                <Box display="flex" justifyContent="space-between" alignItems="baseline">
                  <Typography variant="body2" fontWeight={600}>{label}</Typography>
                  <Chip size="small" label={ponderations[cle] ?? 0} />
                </Box>
                <Typography variant="caption" color="text.secondary">{aide}</Typography>
                <Slider
                  size="small" min={0} max={150} step={5}
                  value={ponderations[cle] ?? 0}
                  onChange={(_, v) => majPoids(cle, v)}
                />
              </Box>
            ))}

            <Divider sx={{ my: 3 }} />
            <Typography variant="subtitle2" fontWeight={700} mb={0.5}>
              Heure de sortie des élèves
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Coût d'occupation de chaque séance. Laissez à zéro les séances
              que vous jugez idéales ; augmentez celles que vous voulez voir
              se vider en priorité.
            </Typography>
            <Box display="grid" sx={{
              gridTemplateColumns: `repeat(${Math.min(nbSeances, 7)}, 1fr)`, gap: 1.5,
            }}>
              {grille.horaires.map((h, i) => (
                <TextField
                  key={i} size="small" type="number" label={`S${i + 1} · ${h[0]}`}
                  inputProps={{ min: 0, max: 1000 }}
                  value={ponderations.penalites_seance?.[i] ?? 0}
                  onChange={(e) => majPoids("penalites_seance", {
                    ...ponderations.penalites_seance, [i]: +e.target.value,
                  })}
                />
              ))}
            </Box>
          </Box>
        )}

        {/* ─────────── Fenêtres pédagogiques ─────────── */}
        {onglet === 2 && (
          <Box p={3}>
            <Alert severity="info" sx={{ mb: 3 }}>
              Une fenêtre interdit une matière sur une plage donnée dans tout
              l'établissement — journée d'inspection, réunion de coordination.
              Tous les professeurs de la matière sont alors libres en même temps.
            </Alert>

            {fenetres.length === 0 ? (
              <Typography variant="body2" color="text.secondary" mb={3}>
                Aucune fenêtre déclarée.
              </Typography>
            ) : (
              <Box mb={3}>
                {fenetres.map((f) => (
                  <Box key={f.id} display="flex" alignItems="center" gap={2} py={1}
                       sx={{ borderBottom: "1px solid", borderColor: "divider" }}>
                    <Chip size="small" color="secondary"
                          label={grille.jours[f.index_jour] ?? `Jour ${f.index_jour}`} />
                    <Typography variant="body2" fontWeight={600} sx={{ minWidth: 160 }}>
                      {f.matiere_nom}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" flex={1}>
                      séances {f.seances_bloquees.map((s) => s + 1).join(", ")}
                      {f.libelle ? ` — ${f.libelle}` : ""}
                    </Typography>
                    <IconButton size="small" color="error"
                                onClick={() => supprimerFenetre(f.id)}>
                      <Icon fontSize="small">delete</Icon>
                    </IconButton>
                  </Box>
                ))}
              </Box>
            )}

            <Typography variant="subtitle2" fontWeight={700} mb={1.5}>
              Ajouter une fenêtre
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap" alignItems="flex-start" mb={2}>
              <TextField select size="small" label="Matière" sx={{ minWidth: 200 }}
                         value={nouvelle.matiere_id}
                         onChange={(e) => setNouvelle({ ...nouvelle, matiere_id: e.target.value })}>
                {matieres.map((m) => (
                  <MenuItem key={m.id} value={m.id}>{m.nom}</MenuItem>
                ))}
              </TextField>
              <TextField select size="small" label="Jour" sx={{ minWidth: 150 }}
                         value={nouvelle.index_jour}
                         onChange={(e) => setNouvelle({ ...nouvelle, index_jour: +e.target.value })}>
                {grille.jours.map((j, i) => <MenuItem key={j} value={i}>{j}</MenuItem>)}
              </TextField>
              <TextField size="small" label="Libellé (facultatif)" sx={{ minWidth: 240 }}
                         value={nouvelle.libelle}
                         onChange={(e) => setNouvelle({ ...nouvelle, libelle: e.target.value })} />
            </Box>
            <Box display="flex" gap={0.5} flexWrap="wrap" mb={2}>
              {grille.horaires.map((h, i) => (
                <ToggleButton
                  key={i} size="small" value={i}
                  selected={nouvelle.seances_bloquees.includes(i)}
                  onChange={() => setNouvelle({
                    ...nouvelle,
                    seances_bloquees: nouvelle.seances_bloquees.includes(i)
                      ? nouvelle.seances_bloquees.filter((s) => s !== i)
                      : [...nouvelle.seances_bloquees, i].sort((a, b) => a - b),
                  })}
                >
                  S{i + 1} · {h[0]}
                </ToggleButton>
              ))}
            </Box>
            <Button variant="outlined" startIcon={<Icon>add</Icon>} onClick={ajouterFenetre}>
              Ajouter
            </Button>
          </Box>
        )}
      </Card>

      {onglet !== 2 && (
        <Box mt={3} display="flex" justifyContent="flex-end">
          <LoadingButton variant="contained" loading={saving} onClick={enregistrer}
                         startIcon={<Icon>save</Icon>}>
            Enregistrer les réglages
          </LoadingButton>
        </Box>
      )}
    </ContentBox>
  );
}
