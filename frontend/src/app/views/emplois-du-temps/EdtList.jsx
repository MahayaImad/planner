import { useEffect, useState, useCallback } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid2";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Icon from "@mui/material/Icon";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import TextField from "@mui/material/TextField";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import { useNavigate } from "react-router-dom";
import { edtApi } from "app/services/api";
import CrudDialog from "app/components/CrudDialog";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

const EdtCard = styled(Card)(({ theme }) => ({
  padding: "1.5rem",
  cursor: "pointer",
  transition: "box-shadow 0.2s, transform 0.15s",
  "&:hover": {
    boxShadow: theme.shadows[6],
    transform: "translateY(-2px)",
  },
}));

const STATUT_COLOR = { brouillon: "warning", publié: "success", archivé: "default" };

const EMPTY = { nom: "", annee_scolaire: "2024-2025", notes: "" };

export default function EdtList() {
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(EMPTY);

  const load = useCallback(async () => {
    setLoading(true);
    try { const { data } = await edtApi.liste(); setRows(data); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const { data } = await edtApi.creer({ ...form, notes: form.notes || null });
      enqueueSnackbar("Emploi du temps créé", { variant: "success" });
      setDialogOpen(false);
      navigate(`/emplois-du-temps/${data.id}`);
    } catch {
      enqueueSnackbar("Erreur lors de la création", { variant: "error" });
    } finally { setSaving(false); }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Supprimer cet emploi du temps et toutes ses leçons ?")) return;
    try {
      await edtApi.supprimer(id);
      enqueueSnackbar("Emploi du temps supprimé", { variant: "warning" });
      load();
    } catch { enqueueSnackbar("Erreur lors de la suppression", { variant: "error" }); }
  };

  return (
    <ContentBox>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={600}>Emplois du temps</Typography>
          <Typography variant="body2" color="text.secondary">
            {rows.length} emploi{rows.length !== 1 ? "s" : ""} du temps
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Icon>add</Icon>} onClick={() => setDialogOpen(true)}>
          Nouveau
        </Button>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
      ) : rows.length === 0 ? (
        <Card sx={{ p: 6, textAlign: "center" }}>
          <Icon sx={{ fontSize: 64, color: "text.disabled", mb: 2 }}>calendar_today</Icon>
          <Typography variant="h6" color="text.secondary" mb={1}>
            Aucun emploi du temps
          </Typography>
          <Typography variant="body2" color="text.disabled" mb={3}>
            Créez votre premier emploi du temps et générez-le automatiquement.
          </Typography>
          <Button variant="contained" startIcon={<Icon>add</Icon>} onClick={() => setDialogOpen(true)}>
            Créer maintenant
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {rows.map((edt) => (
            <Grid key={edt.id} size={{ xs: 12, sm: 6, md: 4 }}>
              <EdtCard onClick={() => navigate(`/emplois-du-temps/${edt.id}`)}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box flex={1} mr={1}>
                    <Typography variant="h6" fontWeight={600} noWrap>{edt.nom}</Typography>
                    <Typography variant="body2" color="text.secondary">{edt.annee_scolaire}</Typography>
                  </Box>
                  <Tooltip title="Supprimer">
                    <IconButton size="small" color="error" onClick={(e) => handleDelete(e, edt.id)}>
                      <Icon fontSize="small">delete</Icon>
                    </IconButton>
                  </Tooltip>
                </Box>

                <Box display="flex" alignItems="center" gap={1} mt={2}>
                  <Chip
                    label={edt.statut}
                    size="small"
                    color={STATUT_COLOR[edt.statut] ?? "default"}
                  />
                  <Chip
                    icon={<Icon sx={{ fontSize: "14px !important" }}>event</Icon>}
                    label={`${edt.nb_lecons} leçon${edt.nb_lecons !== 1 ? "s" : ""}`}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                {edt.notes && (
                  <Typography variant="caption" color="text.secondary" mt={1} display="block" noWrap>
                    {edt.notes}
                  </Typography>
                )}

                <Box display="flex" justifyContent="flex-end" mt={2}>
                  <Button size="small" endIcon={<Icon>arrow_forward</Icon>}>
                    Ouvrir
                  </Button>
                </Box>
              </EdtCard>
            </Grid>
          ))}
        </Grid>
      )}

      <CrudDialog
        open={dialogOpen} onClose={() => setDialogOpen(false)}
        title="Nouvel emploi du temps"
        onSubmit={handleSubmit} loading={saving}
      >
        <TextField
          label="Nom (ex: Semaine type – 2024/2025)" required fullWidth size="small"
          value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
        />
        <TextField
          label="Année scolaire" required fullWidth size="small"
          value={form.annee_scolaire}
          onChange={(e) => setForm({ ...form, annee_scolaire: e.target.value })}
        />
        <TextField
          label="Notes (facultatif)" fullWidth size="small" multiline rows={2}
          value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })}
        />
      </CrudDialog>
    </ContentBox>
  );
}
