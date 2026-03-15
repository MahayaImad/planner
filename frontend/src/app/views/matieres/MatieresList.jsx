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
import { matieresApi } from "app/services/api";
import CrudDialog from "app/components/CrudDialog";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

const TYPES_SALLE = [
  { value: "", label: "Classique (standard)" },
  { value: "labo", label: "Laboratoire" },
  { value: "info", label: "Salle informatique" },
  { value: "sport", label: "Terrain / Gymnase" },
];

const SALLE_COLORS = { labo: "warning", info: "info", sport: "success" };

const EMPTY = { nom: "", coefficient: 1, type_salle_requis: "" };

export default function MatieresList() {
  const { enqueueSnackbar } = useSnackbar();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await matieresApi.liste();
      setRows(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => { setEditing(null); setForm(EMPTY); setDialogOpen(true); };
  const openEdit = (row) => {
    setEditing(row);
    setForm({ nom: row.nom, coefficient: row.coefficient, type_salle_requis: row.type_salle_requis || "" });
    setDialogOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    const payload = { ...form, type_salle_requis: form.type_salle_requis || null };
    try {
      if (editing) {
        await matieresApi.modifier(editing.id, payload);
        enqueueSnackbar("Matière modifiée", { variant: "success" });
      } else {
        await matieresApi.creer(payload);
        enqueueSnackbar("Matière ajoutée", { variant: "success" });
      }
      setDialogOpen(false);
      load();
    } catch {
      enqueueSnackbar("Erreur lors de l'enregistrement", { variant: "error" });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette matière ?")) return;
    try {
      await matieresApi.supprimer(id);
      enqueueSnackbar("Matière supprimée", { variant: "warning" });
      load();
    } catch {
      enqueueSnackbar("Impossible de supprimer (matière utilisée ?)", { variant: "error" });
    }
  };

  return (
    <ContentBox>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={600}>Matières</Typography>
          <Typography variant="body2" color="text.secondary">
            {rows.length} matière{rows.length !== 1 ? "s" : ""} enregistrée{rows.length !== 1 ? "s" : ""}
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
                <TableCell><b>Nom</b></TableCell>
                <TableCell><b>Coefficient</b></TableCell>
                <TableCell><b>Type de salle</b></TableCell>
                <TableCell align="right"><b>Actions</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4 }}><CircularProgress /></TableCell>
                </TableRow>
              ) : rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4, color: "text.secondary" }}>
                    Aucune matière. Cliquez sur "Ajouter" pour commencer.
                  </TableCell>
                </TableRow>
              ) : rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>{row.nom}</Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={`Coef. ${row.coefficient}`} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    {row.type_salle_requis ? (
                      <Chip
                        label={TYPES_SALLE.find((t) => t.value === row.type_salle_requis)?.label ?? row.type_salle_requis}
                        size="small"
                        color={SALLE_COLORS[row.type_salle_requis] ?? "default"}
                      />
                    ) : (
                      <Typography variant="body2" color="text.secondary">Standard</Typography>
                    )}
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
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <CrudDialog
        open={dialogOpen} onClose={() => setDialogOpen(false)}
        title={editing ? "Modifier la matière" : "Nouvelle matière"}
        onSubmit={handleSubmit} loading={saving}
      >
        <TextField
          label="Nom de la matière" required fullWidth size="small"
          value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
        />
        <TextField
          label="Coefficient" type="number" fullWidth size="small"
          inputProps={{ min: 0.5, max: 10, step: 0.5 }}
          value={form.coefficient}
          onChange={(e) => setForm({ ...form, coefficient: +e.target.value })}
        />
        <TextField
          select label="Type de salle requis" fullWidth size="small"
          value={form.type_salle_requis}
          onChange={(e) => setForm({ ...form, type_salle_requis: e.target.value })}
        >
          {TYPES_SALLE.map((t) => (
            <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
          ))}
        </TextField>
      </CrudDialog>
    </ContentBox>
  );
}
