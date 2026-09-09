/**
 * Lancement d'une génération.
 *
 * Le programme annuel et les réglages sont enregistrés : le dialogue n'a
 * plus qu'à les rappeler, vérifier leur cohérence et déclencher le
 * calcul. Il ne redemande donc plus les quatre cents lignes de cours.
 */
import { useState, useEffect, useRef } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Icon from "@mui/material/Icon";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import LinearProgress from "@mui/material/LinearProgress";
import LoadingButton from "@mui/lab/LoadingButton";
import { useSnackbar } from "notistack";
import { useNavigate } from "react-router-dom";
import { edtApi, programmeApi, parametresApi } from "app/services/api";

const INTERVALLE_SUIVI = 1500; // ms entre deux interrogations de la tâche

export default function GenererDialog({ edtId, onClose, onSuccess }) {
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();
  const timerRef = useRef(null);

  const [programme, setProgramme] = useState(null);
  const [params, setParams] = useState(null);
  const [limiteSec, setLimiteSec] = useState(120);
  const [loading, setLoading] = useState(false);
  const [erreur, setErreur] = useState(null);
  const [erreursDonnees, setErreursDonnees] = useState([]);
  const [avertissements, setAvertissements] = useState([]);
  const [tache, setTache] = useState(null);

  useEffect(() => {
    Promise.all([programmeApi.liste(), parametresApi.lire()])
      .then(([p, r]) => {
        setProgramme(p.data);
        setParams(r.data);
        setLimiteSec(r.data.limite_secondes);
      })
      .catch(() => setErreur("Impossible de lire le programme enregistré."));
    // Arrêter le suivi si le dialogue est fermé pendant une génération.
    return () => clearTimeout(timerRef.current);
  }, []);

  /** Le corps ne porte que le temps de calcul : le reste est en base. */
  const corpsRequete = () => ({ limite_secondes: +limiteSec });

  const handleDiagnostic = async () => {
    setErreur(null); setErreursDonnees([]); setAvertissements([]);
    setLoading(true);
    try {
      const { data } = await edtApi.diagnostic(edtId, corpsRequete());
      setErreursDonnees(data.erreurs);
      setAvertissements(data.avertissements);
      if (data.realisable) {
        enqueueSnackbar("Données cohérentes : la génération peut être lancée.",
          { variant: "success" });
      }
    } catch (e) {
      setErreur(e.response?.data?.detail ?? "Erreur lors du contrôle des données");
    } finally { setLoading(false); }
  };

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
    } catch {
      setLoading(false);
      setErreur("Suivi de la génération interrompu.");
    }
  };

  const handleGenerer = async () => {
    setErreur(null); setErreursDonnees([]); setAvertissements([]); setTache(null);
    setLoading(true);
    try {
      const { data } = await edtApi.generer(edtId, corpsRequete());
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

  const handleAnnuler = async () => {
    if (!tache) return;
    try { await edtApi.annulerTache(edtId, tache.id); } catch { /* déjà finie */ }
  };

  // Volume par classe : un fouj n'occupe la classe qu'une fois.
  const volumes = {};
  const couplesVus = new Set();
  (programme ?? []).forEach((l) => {
    if (l.couplage_id) {
      if (couplesVus.has(l.couplage_id)) return;
      couplesVus.add(l.couplage_id);
    }
    volumes[l.classe_nom] = (volumes[l.classe_nom] ?? 0) + l.heures_par_semaine;
  });
  const nbFouj = new Set((programme ?? []).filter((l) => l.couplage_id)
    .map((l) => l.couplage_id)).size;
  const creneauxOuverts = params
    ? params.grille.jours.length * params.grille.horaires.length
      - params.grille.fermetures.reduce((n, [, ss]) => n + ss.length, 0)
    : 0;

  return (
    <Dialog open onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <Icon color="secondary">auto_fix_high</Icon>
          Générer l'emploi du temps
        </Box>
      </DialogTitle>

      <DialogContent dividers>
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

        {programme === null ? (
          <Typography color="text.secondary">Chargement du programme…</Typography>
        ) : programme.length === 0 ? (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <AlertTitle>Aucun programme enregistré</AlertTitle>
            Renseignez d'abord quelles classes suivent quelles matières.
            <Box mt={1}>
              <Button size="small" variant="outlined"
                      onClick={() => { onClose(); navigate("/programme"); }}>
                Aller au programme annuel
              </Button>
            </Box>
          </Alert>
        ) : (
          <>
            <Box display="flex" justifyContent="space-between" alignItems="baseline" mb={1}>
              <Typography variant="subtitle2" fontWeight={700}>
                Programme enregistré
              </Typography>
              <Button size="small" onClick={() => { onClose(); navigate("/programme"); }}>
                Modifier
              </Button>
            </Box>
            <Box display="flex" flexWrap="wrap" gap={0.75} mb={1}>
              {Object.entries(volumes).map(([nom, h]) => (
                <Chip key={nom} size="small" label={`${nom} — ${h} h`}
                      color={h > creneauxOuverts ? "error" : "default"} />
              ))}
            </Box>
            <Typography variant="caption" color="text.secondary">
              {programme.length} lignes ·{" "}
              {programme.reduce((n, l) => n + l.heures_par_semaine, 0)} heures-professeur
              {nbFouj > 0 && ` · ${nbFouj} fouj`} · {creneauxOuverts} créneaux
              ouverts par semaine
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Typography variant="body2" color="text.secondary" mb={2}>
              La grille horaire, les fenêtres pédagogiques et les pondérations
              viennent des réglages de l'établissement.{" "}
              <Button size="small" sx={{ p: 0, minWidth: 0 }}
                      onClick={() => { onClose(); navigate("/parametres"); }}>
                Les modifier
              </Button>
            </Typography>
          </>
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

        <Box display="flex" alignItems="center" gap={2} mt={2}>
          <TextField
            type="number" size="small" label="Limite de temps (secondes)"
            inputProps={{ min: 10, max: 900, step: 10 }}
            value={limiteSec}
            onChange={(e) => setLimiteSec(e.target.value)}
            sx={{ maxWidth: 220 }}
          />
          <Typography variant="caption" color="text.secondary">
            Le solveur s'arrête après ce délai. Plus de temps donne une
            meilleure solution, jamais une solution différente en nature.
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
                    disabled={loading || !programme?.length}
                    startIcon={<Icon>fact_check</Icon>}>
              Vérifier les données
            </Button>
            <LoadingButton
              variant="contained" color="secondary"
              startIcon={<Icon>play_arrow</Icon>}
              onClick={handleGenerer}
              loading={loading}
              disabled={!programme?.length}
            >
              Lancer le solveur
            </LoadingButton>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}
