/**
 * Dialogue de configuration des cours requis avant génération.
 * L'utilisateur définit : pour chaque (classe, matière, professeur) → nb d'heures/semaine
 */
import { useState, useEffect, useRef } from "react";
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
import AlertTitle from "@mui/material/AlertTitle";
import LinearProgress from "@mui/material/LinearProgress";
import LoadingButton from "@mui/lab/LoadingButton";
import { useSnackbar } from "notistack";
import { edtApi, demoApi } from "app/services/api";
import Tooltip from "@mui/material/Tooltip";

const EMPTY_COURS = {
  classe_id: "", matiere_id: "", professeur_id: "",
  heures_par_semaine: 2, nb_seances_doubles: 0, max_heures_par_jour: 2,
  // Fouj : deux lignes partageant un couplage_id sont enseignées en
  // même temps à deux demi-groupes de la classe.
  couplage_id: null, groupe: "",
};

const INTERVALLE_SUIVI = 1500; // ms entre deux interrogations de la tâche

export default function GenererDialog({ edtId, professeurs, matieres, classes, onClose, onSuccess }) {
  const { enqueueSnackbar } = useSnackbar();
  const [cours, setCours] = useState([{ ...EMPTY_COURS }]);
  const [limiteSec, setLimiteSec] = useState(120);
  const [loading, setLoading] = useState(false);
  const [erreur, setErreur] = useState(null);
  const [erreursDonnees, setErreursDonnees] = useState([]);
  const [avertissements, setAvertissements] = useState([]);
  const [tache, setTache] = useState(null);
  const timerRef = useRef(null);

  // Arrêter le suivi si le dialogue est fermé pendant une génération :
  // sans cela, l'intervalle continue de tourner sur un composant démonté.
  useEffect(() => () => clearTimeout(timerRef.current), []);

  const construirePayload = () => ({
    cours_requis: cours.map((c) => ({
      classe_id: +c.classe_id,
      matiere_id: +c.matiere_id,
      professeur_id: +c.professeur_id,
      heures_par_semaine: +c.heures_par_semaine,
      nb_seances_doubles: +c.nb_seances_doubles || 0,
      max_heures_par_jour: +c.max_heures_par_jour || 2,
      couplage_id: c.couplage_id,
      groupe: c.groupe,
    })),
    limite_secondes: +limiteSec,
    // Grille, fenêtres pédagogiques et pondérations ne sont pas envoyées :
    // la génération reprend les réglages enregistrés de l'établissement.
  });

  const champsManquants = () =>
    cours.some((c) => !c.classe_id || !c.matiere_id || !c.professeur_id);

  /** Contrôle des données sans lancer le calcul. */
  const handleDiagnostic = async () => {
    setErreur(null); setErreursDonnees([]); setAvertissements([]);
    if (champsManquants()) { setErreur("Veuillez compléter tous les champs de chaque cours."); return; }
    setLoading(true);
    try {
      const { data } = await edtApi.diagnostic(edtId, construirePayload());
      setErreursDonnees(data.erreurs);
      setAvertissements(data.avertissements);
      if (data.realisable) {
        enqueueSnackbar("Données cohérentes : la génération peut être lancée.",
          { variant: "success" });
      }
    } catch (e) {
      setErreur(e.response?.data?.detail ?? "Erreur lors du contrôle des données");
    } finally {
      setLoading(false);
    }
  };

  /** Interroge la tâche jusqu'à ce qu'elle soit terminée. */
  const suivre = async (tacheId) => {
    try {
      const { data } = await edtApi.tache(edtId, tacheId);
      setTache(data);
      if (!data.terminee) {
        timerRef.current = setTimeout(() => suivre(tacheId), INTERVALLE_SUIVI);
        return;
      }
      setLoading(false);
      if (data.statut === "terminee") {
        enqueueSnackbar(`${data.resultat.lecons_planifiees} leçons planifiées`,
          { variant: "success" });
        setAvertissements(data.resultat.avertissements ?? []);
        onSuccess();
      } else if (data.statut === "annulee") {
        enqueueSnackbar("Génération annulée", { variant: "info" });
      } else {
        setErreur(data.message);
        setErreursDonnees(data.erreurs ?? []);
      }
    } catch (e) {
      setLoading(false);
      setErreur("Suivi de la génération interrompu.");
    }
  };

  /**
   * Reprend le programme du jeu de démonstration.
   * Saisir quarante lignes à la main pour un simple essai découragerait
   * quiconque veut seulement voir tourner le solveur.
   */
  const handleProgrammeDemo = async () => {
    setErreur(null); setErreursDonnees([]);
    setLoading(true);
    try {
      const { data } = await demoApi.programme();
      setCours(data.map((c) => ({
        classe_id: c.classe_id,
        matiere_id: c.matiere_id,
        professeur_id: c.professeur_id,
        heures_par_semaine: c.heures_par_semaine,
        nb_seances_doubles: c.nb_seances_doubles ?? 0,
        max_heures_par_jour: c.max_heures_par_jour ?? 2,
      })));
      enqueueSnackbar(`${data.length} cours repris du jeu de démonstration`,
        { variant: "success" });
    } catch (e) {
      setErreur(e.response?.data?.detail
        ?? "Le programme de démonstration n'est pas disponible");
    } finally {
      setLoading(false);
    }
  };

  const handleAnnuler = async () => {
    if (!tache) return;
    try { await edtApi.annulerTache(edtId, tache.id); } catch { /* déjà terminée */ }
  };

  const updateCours = (i, field, val) => {
    setCours((prev) => prev.map((c, idx) => idx === i ? { ...c, [field]: val } : c));
  };

  const addCours = () => setCours((prev) => [...prev, { ...EMPTY_COURS }]);
  const removeCours = (i) => setCours((prev) => prev.filter((_, idx) => idx !== i));

  /**
   * Fouj : la classe est dédoublée et les deux demi-groupes suivent
   * DEUX cours différents au MÊME créneau, avec deux professeurs et
   * deux salles. Apparier la ligne i avec la suivante crée le couple.
   */
  const apparier = (i) => {
    setCours((prev) => {
      const a = prev[i];
      const suite = [...prev];
      const identifiant = `fouj-${Date.now()}-${i}`;
      const modele = {
        ...EMPTY_COURS,
        classe_id: a.classe_id,
        heures_par_semaine: a.heures_par_semaine,
        nb_seances_doubles: a.nb_seances_doubles,
        max_heures_par_jour: a.max_heures_par_jour,
        couplage_id: identifiant,
        groupe: "G2",
      };
      suite[i] = { ...a, couplage_id: identifiant, groupe: "G1" };
      suite.splice(i + 1, 0, modele);
      return suite;
    });
  };

  const detacher = (i) => {
    setCours((prev) => {
      const identifiant = prev[i].couplage_id;
      return prev
        .filter((c, idx) => !(idx !== i && c.couplage_id === identifiant))
        .map((c) => (c.couplage_id === identifiant
          ? { ...c, couplage_id: null, groupe: "" } : c));
    });
  };

  /** Volume et créneau d'un fouj sont portés par le premier demi-groupe. */
  const majCouple = (i, field, val) => {
    setCours((prev) => {
      const identifiant = prev[i].couplage_id;
      return prev.map((c, idx) =>
        idx === i || (identifiant && c.couplage_id === identifiant)
          ? { ...c, [field]: val } : c);
    });
  };

  const handleGenerer = async () => {
    setErreur(null); setErreursDonnees([]); setAvertissements([]); setTache(null);
    if (champsManquants()) { setErreur("Veuillez compléter tous les champs de chaque cours."); return; }

    setLoading(true);
    try {
      // La génération est mise en file : la réponse porte la tâche, pas
      // le résultat. Le calcul peut durer plusieurs minutes.
      const { data } = await edtApi.generer(edtId, construirePayload());
      setTache(data);
      timerRef.current = setTimeout(() => suivre(data.id), INTERVALLE_SUIVI);
    } catch (e) {
      setLoading(false);
      const detail = e.response?.data?.detail;
      if (detail?.erreurs) {
        setErreur(detail.message);
        setErreursDonnees(detail.erreurs);
      } else {
        setErreur(typeof detail === "string" ? detail : "Erreur lors de la génération");
      }
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

        <Button
          size="small"
          variant="outlined"
          color="info"
          startIcon={<Icon>science</Icon>}
          onClick={handleProgrammeDemo}
          disabled={loading}
          sx={{ mb: 2 }}
        >
          Reprendre le programme de démonstration
        </Button>

        {erreur && <Alert severity="error" sx={{ mb: 2 }}>{erreur}</Alert>}

        {erreursDonnees.length > 0 && (
          <Alert severity="error" sx={{ mb: 2 }}>
            <AlertTitle>Données à corriger</AlertTitle>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {erreursDonnees.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </Alert>
        )}

        {avertissements.length > 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <AlertTitle>Points de vigilance</AlertTitle>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {avertissements.slice(0, 6).map((m, i) => <li key={i}>{m}</li>)}
              {avertissements.length > 6 && (
                <li>… et {avertissements.length - 6} autre(s)</li>
              )}
            </ul>
          </Alert>
        )}

        {tache && !tache.terminee && (
          <Alert severity="info" icon={false} sx={{ mb: 2 }}>
            <AlertTitle>Génération en cours</AlertTitle>
            <Typography variant="body2">{tache.message}</Typography>
            {tache.cout_courant != null && (
              <Typography variant="caption" color="text.secondary">
                {tache.nb_solutions} solution(s) explorée(s) — le coût diminue
                à mesure que la qualité s'améliore.
              </Typography>
            )}
            <LinearProgress sx={{ mt: 1.5 }} />
          </Alert>
        )}

        {tache?.statut === "terminee" && tache.resultat && (
          <Alert severity="success" sx={{ mb: 2 }}>
            <AlertTitle>
              {tache.resultat.lecons_planifiees} leçons planifiées
              {" "}({tache.resultat.statut}, {tache.resultat.duree_resolution}s)
            </AlertTitle>
            <Typography variant="body2">
              Trous élèves : {tache.resultat.qualite.trous_classes} —
              {" "}trous professeurs : {tache.resultat.qualite.trous_professeurs} —
              {" "}journées de {tache.resultat.qualite.charge_journaliere_min} à
              {" "}{tache.resultat.qualite.charge_journaliere_max} h
            </Typography>
          </Alert>
        )}

        {cours.map((c, i) => (
          <Box key={i} mb={2}>
            <Box display="flex" alignItems="center" gap={0.5} mb={1}>
              <Typography variant="caption" fontWeight={700}
                          color={c.couplage_id ? "secondary" : "primary"}>
                {c.couplage_id ? `Fouj — demi-groupe ${c.groupe}` : `Cours #${i + 1}`}
              </Typography>

              {!c.couplage_id && (
                <Tooltip title="Dédoubler : la classe se scinde en deux
                                 demi-groupes qui suivent deux cours
                                 différents au même créneau">
                  <IconButton size="small" color="secondary" onClick={() => apparier(i)}>
                    <Icon fontSize="small">call_split</Icon>
                  </IconButton>
                </Tooltip>
              )}
              {c.couplage_id && c.groupe === "G1" && (
                <Tooltip title="Annuler le dédoublement">
                  <IconButton size="small" onClick={() => detacher(i)}>
                    <Icon fontSize="small">link_off</Icon>
                  </IconButton>
                </Tooltip>
              )}

              {cours.length > 1 && !c.couplage_id && (
                <IconButton size="small" color="error" onClick={() => removeCours(i)}>
                  <Icon fontSize="small">remove_circle</Icon>
                </IconButton>
              )}
            </Box>
            <Box display="grid" sx={{ gridTemplateColumns: "1fr 1fr 1fr 100px 100px", gap: 1.5 }}>
              <TextField
                select size="small" label="Classe" required
                disabled={c.groupe === "G2"}
                value={c.classe_id} onChange={(e) => majCouple(i, "classe_id", e.target.value)}
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
                type="number" size="small" label="Blocs 2h"
                title="Nombre de séances de 2 h accolées à réserver dans le volume"
                inputProps={{ min: 0, max: 10 }}
                disabled={c.groupe === "G2"}
                value={c.nb_seances_doubles}
                onChange={(e) => majCouple(i, "nb_seances_doubles", e.target.value)}
              />
              <TextField
                type="number" size="small" label="H/sem."
                inputProps={{ min: 1, max: 20 }}
                disabled={c.groupe === "G2"}
                value={c.heures_par_semaine}
                onChange={(e) => majCouple(i, "heures_par_semaine", e.target.value)}
              />
            </Box>
            {c.groupe === "G2" && (
              <Typography variant="caption" color="text.secondary"
                          display="block" mt={0.5}>
                Ces deux cours occupent le même créneau : la moitié de la
                classe suit l'un, l'autre moitié suit l'autre. Il faut donc
                deux salles disponibles en même temps.
              </Typography>
            )}
            {i < cours.length - 1 && !(c.groupe === "G1") && <Divider sx={{ mt: 2 }} />}
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
            inputProps={{ min: 10, max: 900, step: 10 }}
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
        <Button onClick={onClose} variant="outlined" color="inherit">Fermer</Button>

        {tache && !tache.terminee ? (
          <Button onClick={handleAnnuler} variant="outlined" color="error"
                  startIcon={<Icon>stop</Icon>}>
            Arrêter la génération
          </Button>
        ) : (
          <>
            <Button onClick={handleDiagnostic} variant="outlined"
                    disabled={loading} startIcon={<Icon>fact_check</Icon>}>
              Vérifier les données
            </Button>
            <LoadingButton
              variant="contained"
              color="secondary"
              startIcon={<Icon>play_arrow</Icon>}
              onClick={handleGenerer}
              loading={loading}
            >
              Lancer le solveur
            </LoadingButton>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}
