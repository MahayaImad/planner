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
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Icon from "@mui/material/Icon";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import { professeursApi, matieresApi } from "app/services/api";
import CrudDialog from "app/components/CrudDialog";
import DisponibilitesDialog from "./DisponibilitesDialog";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

const EMPTY = {
  nom: "", prenom: "", telephone: "", email: "",
  max_heures_consecutives: 3, matieres_ids: [],
};

export default function ProfesseursList() {
  const { enqueueSnackbar } = useSnackbar();
  const [rows, setRows] = useState([]);
  const [matieres, setMatieres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dispoDialogId, setDispoDialogId] = useState(null);
  const [editing, setEditing] = useState(null); // null = création
  const [form, setForm] = useState(EMPTY);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [p, m] = await Promise.all([professeursApi.liste(), matieresApi.liste()]);
      setRows(p.data);
      setMatieres(m.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => { setEditing(null); setForm(EMPTY); setDialogOpen(true); };
  const openEdit = (row) => {
    setEditing(row);
    setForm({ nom: row.nom, prenom: row.prenom, telephone: row.telephone || "",
               email: row.email || "", max_heures_consecutives: row.max_heures_consecutives,
               matieres_ids: [] });
    setDialogOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editing) {
        await professeursApi.modifier(editing.id, form);
        enqueueSnackbar("Professeur modifié", { variant: "success" });
      } else {
        await professeursApi.creer(form);
        enqueueSnackbar("Professeur ajouté", { variant: "success" });
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
    if (!window.confirm("Supprimer ce professeur ?")) return;
    try {
      await professeursApi.supprimer(id);
      enqueueSnackbar("Professeur supprimé", { variant: "warning" });
      load();
    } catch {
      enqueueSnackbar("Erreur lors de la suppression", { variant: "error" });
    }
  };

  const toggleMatiere = (id) => {
    setForm((f) => ({
      ...f,
      matieres_ids: f.matieres_ids.includes(id)
        ? f.matieres_ids.filter((x) => x !== id)
        : [...f.matieres_ids, id],
    }));
  };

  return (
    <ContentBox>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={600}>Professeurs</Typography>
          <Typography variant="body2" color="text.secondary">
            {rows.length} professeur{rows.length !== 1 ? "s" : ""} enregistré{rows.length !== 1 ? "s" : ""}
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Icon>person_add</Icon>} onClick={openCreate}>
          Ajouter
        </Button>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: "action.hover" }}>
                <TableCell><b>Nom complet</b></TableCell>
                <TableCell><b>Email</b></TableCell>
                <TableCell><b>Téléphone</b></TableCell>
                <TableCell><b>Heures consec. max</b></TableCell>
                <TableCell align="right"><b>Actions</b></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4, color: "text.secondary" }}>
                    Aucun professeur. Cliquez sur "Ajouter" pour commencer.
                  </TableCell>
                </TableRow>
              ) : rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Box sx={{
                        width: 36, height: 36, borderRadius: "50%",
                        bgcolor: "primary.main", color: "white",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontWeight: 700, fontSize: 14,
                      }}>
                        {row.prenom[0]}{row.nom[0]}
                      </Box>
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {row.prenom} {row.nom}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>{row.email || "—"}</TableCell>
                  <TableCell>{row.telephone || "—"}</TableCell>
                  <TableCell>
                    <Chip label={`${row.max_heures_consecutives}h`} size="small" color="info" variant="outlined" />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Disponibilités">
                      <IconButton size="small" onClick={() => setDispoDialogId(row.id)}>
                        <Icon>event_available</Icon>
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Modifier">
                      <IconButton size="small" onClick={() => openEdit(row)}>
                        <Icon>edit</Icon>
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Supprimer">
                      <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}>
                        <Icon>delete</Icon>
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Formulaire création/édition */}
      <CrudDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        title={editing ? "Modifier le professeur" : "Nouveau professeur"}
        onSubmit={handleSubmit}
        loading={saving}
      >
        <Box display="flex" gap={2}>
          <TextField
            label="Prénom" required fullWidth size="small"
            value={form.prenom} onChange={(e) => setForm({ ...form, prenom: e.target.value })}
          />
          <TextField
            label="Nom" required fullWidth size="small"
            value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
          />
        </Box>
        <TextField
          label="Email" type="email" fullWidth size="small"
          value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <TextField
          label="Téléphone" fullWidth size="small"
          value={form.telephone} onChange={(e) => setForm({ ...form, telephone: e.target.value })}
        />
        <TextField
          label="Heures consécutives max" type="number" fullWidth size="small"
          inputProps={{ min: 1, max: 8 }}
          value={form.max_heures_consecutives}
          onChange={(e) => setForm({ ...form, max_heures_consecutives: +e.target.value })}
        />
        <Box>
          <Typography variant="caption" color="text.secondary" mb={1} display="block">
            Matières enseignées (sélection multiple)
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {matieres.map((m) => (
              <Chip
                key={m.id} label={m.nom} size="small" clickable
                variant={form.matieres_ids.includes(m.id) ? "filled" : "outlined"}
                color={form.matieres_ids.includes(m.id) ? "primary" : "default"}
                onClick={() => toggleMatiere(m.id)}
              />
            ))}
          </Box>
        </Box>
      </CrudDialog>

      {/* Grille disponibilités */}
      {dispoDialogId && (
        <DisponibilitesDialog
          profId={dispoDialogId}
          onClose={() => setDispoDialogId(null)}
        />
      )}
    </ContentBox>
  );
}
