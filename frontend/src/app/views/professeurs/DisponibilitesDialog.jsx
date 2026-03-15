/**
 * Grille hebdomadaire pour cocher les créneaux d'indisponibilité d'un professeur.
 */
import { useEffect, useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";
import CircularProgress from "@mui/material/CircularProgress";
import LoadingButton from "@mui/lab/LoadingButton";
import { useSnackbar } from "notistack";
import { professeursApi } from "app/services/api";

const JOURS = ["Samedi", "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"];
const HEURES = [
  "08:00", "09:00", "10:00", "11:00",
  "13:00", "14:00", "15:00", "16:00",
];

export default function DisponibilitesDialog({ profId, onClose }) {
  const { enqueueSnackbar } = useSnackbar();
  const [indispos, setIndispos] = useState(new Set()); // "Lundi-08:00"
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    professeursApi.indisponibilites.lire(profId).then(({ data }) => {
      setIndispos(new Set(data.map((d) => `${d.jour}-${d.heure_debut}`)));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [profId]);

  const toggle = (jour, heure) => {
    const key = `${jour}-${heure}`;
    setIndispos((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const creneaux = [...indispos].map((k) => {
        const [jour, heure_debut] = k.split("-");
        return { jour, heure_debut };
      });
      await professeursApi.indisponibilites.definir(profId, creneaux);
      enqueueSnackbar("Disponibilités enregistrées", { variant: "success" });
      onClose();
    } catch {
      enqueueSnackbar("Erreur lors de l'enregistrement", { variant: "error" });
    } finally {
      setSaving(false);
    }
  };

  const CELL_SIZE = 48;

  return (
    <Dialog open onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Indisponibilités du professeur</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Cliquez sur un créneau pour le marquer comme <b>indisponible</b> (rouge).
          Les créneaux blancs sont disponibles.
        </Typography>

        {loading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ overflowX: "auto" }}>
            <Box display="grid"
              sx={{ gridTemplateColumns: `80px repeat(${JOURS.length}, ${CELL_SIZE}px)`, gap: "2px" }}>

              {/* Header jours */}
              <Box />
              {JOURS.map((j) => (
                <Box key={j} sx={{ textAlign: "center", pb: 0.5 }}>
                  <Typography variant="caption" fontWeight={700}>{j}</Typography>
                </Box>
              ))}

              {/* Lignes heures */}
              {HEURES.map((heure) => (
                <>
                  <Box key={`h-${heure}`} display="flex" alignItems="center">
                    <Typography variant="caption" color="text.secondary">{heure}</Typography>
                  </Box>
                  {JOURS.map((jour) => {
                    const key = `${jour}-${heure}`;
                    const indispo = indispos.has(key);
                    return (
                      <Tooltip key={key} title={indispo ? "Indisponible (cliquer pour libérer)" : "Disponible (cliquer pour bloquer)"}>
                        <Box
                          onClick={() => toggle(jour, heure)}
                          sx={{
                            width: CELL_SIZE, height: CELL_SIZE,
                            borderRadius: 1, cursor: "pointer",
                            bgcolor: indispo ? "error.light" : "success.light",
                            border: "2px solid",
                            borderColor: indispo ? "error.main" : "success.main",
                            transition: "all 0.15s",
                            "&:hover": { opacity: 0.75 },
                          }}
                        />
                      </Tooltip>
                    );
                  })}
                </>
              ))}
            </Box>

            <Box display="flex" gap={2} mt={2}>
              <Box display="flex" alignItems="center" gap={0.5}>
                <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: "success.light", border: "2px solid", borderColor: "success.main" }} />
                <Typography variant="caption">Disponible</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={0.5}>
                <Box sx={{ width: 16, height: 16, borderRadius: 0.5, bgcolor: "error.light", border: "2px solid", borderColor: "error.main" }} />
                <Typography variant="caption">Indisponible</Typography>
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button onClick={onClose} variant="outlined" color="inherit">Annuler</Button>
        <LoadingButton onClick={handleSave} variant="contained" loading={saving}>
          Enregistrer
        </LoadingButton>
      </DialogActions>
    </Dialog>
  );
}
