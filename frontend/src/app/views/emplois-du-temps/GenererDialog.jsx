/**
 * Dialogue de configuration des cours requis avant génération.
 * L'utilisateur peut charger un template officiel (volume horaire algérien)
 * ou saisir manuellement les cours à planifier.
 */
import { useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import Icon from "@mui/material/Icon";
import Divider from "@mui/material/Divider";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import Paper from "@mui/material/Paper";
import LoadingButton from "@mui/lab/LoadingButton";
import { useSnackbar } from "notistack";
import { edtApi } from "app/services/api";
import { FILIERES, TEMPLATES, trouverMatiereId } from "app/data/volumeHoraire";

const EMPTY_COURS = { classe_id: "", matiere_id: "", professeur_id: "", heures_par_semaine: 2 };

export default function GenererDialog({ edtId, professeurs, matieres, classes, onClose, onSuccess }) {
  const { enqueueSnackbar } = useSnackbar();
  const [cours, setCours] = useState([{ ...EMPTY_COURS }]);
  const [limiteSec, setLimiteSec] = useState(120);
  const [loading, setLoading] = useState(false);
  const [erreur, setErreur] = useState(null);

  // Template selector state
  const [showTemplate, setShowTemplate] = useState(false);
  const [filiereSelectionnee, setFiliereSelectionnee] = useState("");
  const [templateSelectionnee, setTemplateSelectionnee] = useState("");
  const [classeTemplate, setClasseTemplate] = useState("");

  const templatesFiltres = TEMPLATES.filter((t) => t.filiere === filiereSelectionnee);

  const chargerTemplate = () => {
    const tpl = TEMPLATES.find((t) => t.id === templateSelectionnee);
    if (!tpl) return;

    const nouvCours = tpl.cours.map((c) => ({
      classe_id: classeTemplate,
      matiere_id: trouverMatiereId(c.matiere, matieres) ?? "",
      professeur_id: "",
      heures_par_semaine: c.heures,
      _nomMatiere: c.matiere, // conservé pour affichage si non trouvée
    }));

    const nonTrouves = tpl.cours
      .filter((c) => !trouverMatiereId(c.matiere, matieres))
      .map((c) => c.matiere);

    setCours(nouvCours);
    setShowTemplate(false);

    if (nonTrouves.length > 0) {
      enqueueSnackbar(
        `Template chargé. Matières non trouvées en BDD : ${nonTrouves.join(", ")}. Vérifiez les noms.`,
        { variant: "warning", autoHideDuration: 6000 }
      );
    } else {
      enqueueSnackbar(`Template "${tpl.label}" chargé (${nouvCours.length} cours). Affectez les professeurs.`, {
        variant: "info",
      });
    }
  };

  const updateCours = (i, field, val) => {
    setCours((prev) => prev.map((c, idx) => idx === i ? { ...c, [field]: val } : c));
  };

  const addCours = () => setCours((prev) => [...prev, { ...EMPTY_COURS }]);
  const removeCours = (i) => setCours((prev) => prev.filter((_, idx) => idx !== i));

  const handleGenerer = async () => {
    setErreur(null);
    const invalid = cours.find((c) => !c.classe_id || !c.matiere_id || !c.professeur_id);
    if (invalid) { setErreur("Veuillez compléter tous les champs de chaque cours (classe, matière, professeur)."); return; }

    setLoading(true);
    try {
      const payload = {
        cours_requis: cours.map((c) => ({
          classe_id: +c.classe_id,
          matiere_id: +c.matiere_id,
          professeur_id: +c.professeur_id,
          heures_par_semaine: +c.heures_par_semaine,
        })),
        limite_secondes: +limiteSec,
      };
      const { data } = await edtApi.generer(edtId, payload);
      enqueueSnackbar(`${data.lecons_planifiees} leçons planifiées (${data.statut})`, { variant: "success" });
      onSuccess();
    } catch (e) {
      const msg = e.response?.data?.detail ?? "Erreur lors de la génération";
      setErreur(typeof msg === "string" ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Icon color="secondary">auto_fix_high</Icon>
          Générer l'emploi du temps
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Définissez les cours à planifier. Le solveur CP-SAT répartira automatiquement
          les leçons en respectant les contraintes (disponibilités, salles, chevauchements).
        </Typography>

        {/* ── Charger un template ── */}
        <Paper variant="outlined" sx={{ p: 1.5, mb: 2, borderStyle: "dashed" }}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={1}>
              <Icon color="primary" fontSize="small">library_books</Icon>
              <Typography variant="body2" fontWeight={600}>
                Charger un template officiel
              </Typography>
              <Chip label="Programme algérien" size="small" color="primary" variant="outlined" />
            </Box>
            <Button
              size="small"
              variant={showTemplate ? "contained" : "outlined"}
              color="primary"
              startIcon={<Icon fontSize="small">{showTemplate ? "expand_less" : "expand_more"}</Icon>}
              onClick={() => setShowTemplate((v) => !v)}
            >
              {showTemplate ? "Masquer" : "Choisir un template"}
            </Button>
          </Box>

          <Collapse in={showTemplate}>
            <Box mt={2} display="grid" sx={{ gridTemplateColumns: "1fr 2fr 1fr", gap: 1.5 }}>
              <TextField
                select size="small" label="Filière"
                value={filiereSelectionnee}
                onChange={(e) => { setFiliereSelectionnee(e.target.value); setTemplateSelectionnee(""); }}
              >
                {FILIERES.map((f) => (
                  <MenuItem key={f.value} value={f.value}>{f.label}</MenuItem>
                ))}
              </TextField>

              <TextField
                select size="small" label="Niveau / Section"
                value={templateSelectionnee}
                onChange={(e) => setTemplateSelectionnee(e.target.value)}
                disabled={!filiereSelectionnee}
              >
                {templatesFiltres.map((t) => (
                  <MenuItem key={t.id} value={t.id}>{t.label}</MenuItem>
                ))}
              </TextField>

              <TextField
                select size="small" label="Classe cible"
                value={classeTemplate}
                onChange={(e) => setClasseTemplate(e.target.value)}
              >
                <MenuItem value=""><em>— Sans classe —</em></MenuItem>
                {classes.map((cl) => (
                  <MenuItem key={cl.id} value={cl.id}>{cl.nom}</MenuItem>
                ))}
              </TextField>
            </Box>

            {templateSelectionnee && (
              <Box mt={1.5}>
                <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                  Aperçu — {TEMPLATES.find((t) => t.id === templateSelectionnee)?.cours.length} matières :&nbsp;
                  {TEMPLATES.find((t) => t.id === templateSelectionnee)?.cours
                    .map((c) => `${c.matiere} (${c.heures}h)`)
                    .join(" · ")}
                </Typography>
              </Box>
            )}

            <Box mt={1.5} display="flex" justifyContent="flex-end">
              <Button
                variant="contained"
                color="primary"
                size="small"
                disabled={!templateSelectionnee}
                startIcon={<Icon>download</Icon>}
                onClick={chargerTemplate}
              >
                Charger ce template
              </Button>
            </Box>
          </Collapse>
        </Paper>

        {erreur && <Alert severity="error" sx={{ mb: 2 }}>{erreur}</Alert>}

        {/* ── Liste des cours ── */}
        {cours.map((c, i) => (
          <Box key={i} mb={2}>
            <Box display="flex" alignItems="center" gap={0.5} mb={1}>
              <Typography variant="caption" fontWeight={700} color="primary">
                Cours #{i + 1}
              </Typography>
              {/* Indication si la matière n'a pas été trouvée en BDD */}
              {c._nomMatiere && !c.matiere_id && (
                <Chip
                  label={`"${c._nomMatiere}" non trouvée`}
                  size="small"
                  color="warning"
                  variant="outlined"
                  sx={{ fontSize: "0.65rem" }}
                />
              )}
              {cours.length > 1 && (
                <IconButton size="small" color="error" onClick={() => removeCours(i)} sx={{ ml: "auto" }}>
                  <Icon fontSize="small">remove_circle</Icon>
                </IconButton>
              )}
            </Box>
            <Box display="grid" sx={{ gridTemplateColumns: "1fr 1fr 1fr 100px", gap: 1.5 }}>
              <TextField
                select size="small" label="Classe" required
                value={c.classe_id} onChange={(e) => updateCours(i, "classe_id", e.target.value)}
              >
                {classes.map((cl) => <MenuItem key={cl.id} value={cl.id}>{cl.nom}</MenuItem>)}
              </TextField>
              <TextField
                select size="small" label="Matière" required
                value={c.matiere_id} onChange={(e) => updateCours(i, "matiere_id", e.target.value)}
              >
                {matieres.map((m) => <MenuItem key={m.id} value={m.id}>{m.nom}</MenuItem>)}
              </TextField>
              <TextField
                select size="small" label="Professeur" required
                value={c.professeur_id} onChange={(e) => updateCours(i, "professeur_id", e.target.value)}
              >
                {professeurs.map((p) => (
                  <MenuItem key={p.id} value={p.id}>{p.prenom} {p.nom}</MenuItem>
                ))}
              </TextField>
              <TextField
                type="number" size="small" label="H/sem."
                inputProps={{ min: 1, max: 20 }}
                value={c.heures_par_semaine}
                onChange={(e) => updateCours(i, "heures_par_semaine", e.target.value)}
              />
            </Box>
            {i < cours.length - 1 && <Divider sx={{ mt: 2 }} />}
          </Box>
        ))}

        <Button
          startIcon={<Icon>add</Icon>}
          onClick={addCours}
          variant="outlined"
          size="small"
          sx={{ mt: 1 }}
        >
          Ajouter un cours
        </Button>

        <Divider sx={{ my: 2 }} />

        <Box display="flex" alignItems="center" gap={2}>
          <TextField
            type="number" size="small" label="Limite de temps (secondes)"
            inputProps={{ min: 10, max: 600, step: 10 }}
            value={limiteSec}
            onChange={(e) => setLimiteSec(e.target.value)}
            sx={{ maxWidth: 220 }}
          />
          <Typography variant="caption" color="text.secondary">
            Le solveur s'arrête après ce délai (plus de temps = meilleure solution).
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button onClick={onClose} variant="outlined" color="inherit">Annuler</Button>
        <LoadingButton
          variant="contained"
          color="secondary"
          startIcon={<Icon>play_arrow</Icon>}
          onClick={handleGenerer}
          loading={loading}
        >
          Lancer le solveur
        </LoadingButton>
      </DialogActions>
    </Dialog>
  );
}
