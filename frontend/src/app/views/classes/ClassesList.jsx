import { useEffect, useState, useCallback } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Icon from "@mui/material/Icon";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import { classesApi } from "app/services/api";
import CrudDialog from "app/components/CrudDialog";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

const NIVEAUX = [
  { value: "primaire", label: "Primaire", color: "#2196f3" },
  { value: "moyen", label: "Moyen (CEM)", color: "#ff9800" },
  { value: "secondaire", label: "Secondaire (Lycée)", color: "#9c27b0" },
];

const EMPTY = { nom: "", niveau: "moyen", effectif: 30 };

export default function ClassesList() {
  const { enqueueSnackbar } = useSnackbar();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY);

  const load = useCallback(async () => {
    setLoading(true);
    try { const { data } = await classesApi.liste(); setRows(data); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => { setEditing(null); setForm(EMPTY); setDialogOpen(true); };
  const openEdit = (row) => {
    setEditing(row);
    setForm({ nom: row.nom, niveau: row.niveau, effectif: row.effectif });
    setDialogOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      editing ? await classesApi.modifier(editing.id, form) : await classesApi.creer(form);
      enqueueSnackbar(editing ? "Classe modifiée" : "Classe ajoutée", { variant: "success" });
      setDialogOpen(false); load();
    } catch { enqueueSnackbar("Erreur lors de l'enregistrement", { variant: "error" }); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette classe ?")) return;
    try { await classesApi.supprimer(id); enqueueSnackbar("Classe supprimée", { variant: "warning" }); load(); }
    catch { enqueueSnackbar("Impossible de supprimer", { variant: "error" }); }
  };

  // Grouper par niveau
  const grouped = NIVEAUX.map((n) => ({
    ...n,
    classes: rows.filter((r) => r.niveau === n.value),
  }));

  return (
    <ContentBox>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={600}>Classes</Typography>
          <Typography variant="body2" color="text.secondary">
            {rows.length} classe{rows.length !== 1 ? "s" : ""} enregistrée{rows.length !== 1 ? "s" : ""}
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Icon>add</Icon>} onClick={openCreate}>
          Ajouter
        </Button>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: "action.hover" }}>
                <TableCell><b>Classe</b></TableCell>
                <TableCell><b>Niveau</b></TableCell>
                <TableCell><b>Effectif</b></TableCell>
                <TableCell align="right"><b>Actions</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow><TableCell colSpan={4} align="center" sx={{ py: 4 }}><CircularProgress /></TableCell></TableRow>
              ) : rows.length === 0 ? (
                <TableRow><TableCell colSpan={4} align="center" sx={{ py: 4, color: "text.secondary" }}>
                  Aucune classe. Cliquez sur "Ajouter" pour commencer.
                </TableCell></TableRow>
              ) : grouped.map(({ value, label, color, classes }) =>
                classes.length > 0 ? [
                  <TableRow key={`group-${value}`}>
                    <TableCell colSpan={4} sx={{ bgcolor: `${color}11`, py: 0.75 }}>
                      <Typography variant="caption" fontWeight={700} sx={{ color }}>
                        {label} ({classes.length})
                      </Typography>
                    </TableCell>
                  </TableRow>,
                  ...classes.map((row) => (
                    <TableRow key={row.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Box sx={{
                            width: 32, height: 32, borderRadius: 1,
                            bgcolor: `${color}22`, display: "flex",
                            alignItems: "center", justifyContent: "center",
                          }}>
                            <Icon sx={{ color, fontSize: 18 }}>school</Icon>
                          </Box>
                          <Typography variant="body2" fontWeight={600}>{row.nom}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label={label} size="small" sx={{ bgcolor: `${color}22`, color }} />
                      </TableCell>
                      <TableCell>
                        <Chip label={`${row.effectif} élèves`} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Modifier">
                          <IconButton size="small" onClick={() => openEdit(row)}><Icon>edit</Icon></IconButton>
                        </Tooltip>
                        <Tooltip title="Supprimer">
                          <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}><Icon>delete</Icon></IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ] : []
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <CrudDialog
        open={dialogOpen} onClose={() => setDialogOpen(false)}
        title={editing ? "Modifier la classe" : "Nouvelle classe"}
        onSubmit={handleSubmit} loading={saving}
      >
        <TextField
          label="Nom de la classe (ex: 4ème A)" required fullWidth size="small"
          value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
        />
        <TextField
          select label="Niveau" fullWidth size="small"
          value={form.niveau} onChange={(e) => setForm({ ...form, niveau: e.target.value })}
        >
          {NIVEAUX.map((n) => <MenuItem key={n.value} value={n.value}>{n.label}</MenuItem>)}
        </TextField>
        <TextField
          label="Effectif (nb élèves)" type="number" fullWidth size="small"
          inputProps={{ min: 1, max: 60 }}
          value={form.effectif} onChange={(e) => setForm({ ...form, effectif: +e.target.value })}
        />
      </CrudDialog>
    </ContentBox>
  );
}
