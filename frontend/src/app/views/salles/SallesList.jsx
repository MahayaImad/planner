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
import { sallesApi } from "app/services/api";
import CrudDialog from "app/components/CrudDialog";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

const TYPES = [
  { value: "classique", label: "Salle classique", color: "default", icon: "meeting_room" },
  { value: "labo", label: "Laboratoire", color: "warning", icon: "science" },
  { value: "info", label: "Salle informatique", color: "info", icon: "computer" },
  { value: "sport", label: "Terrain / Gymnase", color: "success", icon: "sports_soccer" },
];

const EMPTY = { nom: "", capacite: 30, type: "classique" };

export default function SallesList() {
  const { enqueueSnackbar } = useSnackbar();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY);

  const load = useCallback(async () => {
    setLoading(true);
    try { const { data } = await sallesApi.liste(); setRows(data); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => { setEditing(null); setForm(EMPTY); setDialogOpen(true); };
  const openEdit = (row) => {
    setEditing(row);
    setForm({ nom: row.nom, capacite: row.capacite, type: row.type });
    setDialogOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      editing ? await sallesApi.modifier(editing.id, form) : await sallesApi.creer(form);
      enqueueSnackbar(editing ? "Salle modifiée" : "Salle ajoutée", { variant: "success" });
      setDialogOpen(false); load();
    } catch {
      enqueueSnackbar("Erreur lors de l'enregistrement", { variant: "error" });
    } finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Supprimer cette salle ?")) return;
    try { await sallesApi.supprimer(id); enqueueSnackbar("Salle supprimée", { variant: "warning" }); load(); }
    catch { enqueueSnackbar("Impossible de supprimer", { variant: "error" }); }
  };

  return (
    <ContentBox>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={600}>Salles</Typography>
          <Typography variant="body2" color="text.secondary">
            {rows.length} salle{rows.length !== 1 ? "s" : ""} enregistrée{rows.length !== 1 ? "s" : ""}
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Icon>add_business</Icon>} onClick={openCreate}>
          Ajouter
        </Button>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: "action.hover" }}>
                <TableCell><b>Nom</b></TableCell>
                <TableCell><b>Type</b></TableCell>
                <TableCell><b>Capacité</b></TableCell>
                <TableCell align="right"><b>Actions</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow><TableCell colSpan={4} align="center" sx={{ py: 4 }}><CircularProgress /></TableCell></TableRow>
              ) : rows.length === 0 ? (
                <TableRow><TableCell colSpan={4} align="center" sx={{ py: 4, color: "text.secondary" }}>
                  Aucune salle. Cliquez sur "Ajouter" pour commencer.
                </TableCell></TableRow>
              ) : rows.map((row) => {
                const t = TYPES.find((x) => x.value === row.type) ?? TYPES[0];
                return (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Icon sx={{ color: "text.secondary", fontSize: 20 }}>{t.icon}</Icon>
                        <Typography variant="body2" fontWeight={600}>{row.nom}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={t.label} size="small" color={t.color} />
                    </TableCell>
                    <TableCell>
                      <Chip label={`${row.capacite} élèves`} size="small" variant="outlined" />
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
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <CrudDialog
        open={dialogOpen} onClose={() => setDialogOpen(false)}
        title={editing ? "Modifier la salle" : "Nouvelle salle"}
        onSubmit={handleSubmit} loading={saving}
      >
        <TextField
          label="Nom de la salle" required fullWidth size="small"
          value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
        />
        <TextField
          select label="Type" fullWidth size="small"
          value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}
        >
          {TYPES.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
        </TextField>
        <TextField
          label="Capacité (nb élèves)" type="number" fullWidth size="small"
          inputProps={{ min: 1, max: 500 }}
          value={form.capacite} onChange={(e) => setForm({ ...form, capacite: +e.target.value })}
        />
      </CrudDialog>
    </ContentBox>
  );
}
