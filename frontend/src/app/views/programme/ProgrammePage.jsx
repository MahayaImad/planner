/**
 * Programme annuel : quelle classe suit quelle matière, avec quel
 * enseignant et combien d'heures.
 *
 * Le programme ne change qu'à la rentrée. Il est enregistré une fois,
 * et la génération le reprend seule — inutile de ressaisir quatre cents
 * lignes à chaque calcul.
 */
import { useEffect, useState, useCallback, useMemo, useRef } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Icon from "@mui/material/Icon";
import Chip from "@mui/material/Chip";
import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import Tooltip from "@mui/material/Tooltip";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import LinearProgress from "@mui/material/LinearProgress";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import {
  programmeApi, classesApi, matieresApi, professeursApi,
} from "app/services/api";

const ContentBox = styled(Box)(({ theme }) => ({
  margin: "2rem",
  [theme.breakpoints.down("sm")]: { margin: "1rem" },
}));

const LIGNE_VIDE = {
  classe_id: "", matiere_id: "", professeur_id: "",
  heures_par_semaine: 2, nb_seances_doubles: 0, max_heures_par_jour: 2,
  couplage_id: null, groupe: "",
};

/** Déclenche le téléchargement d'un contenu texte. */
const telecharger = (contenu, nom) => {
  const lien = document.createElement("a");
  lien.href = URL.createObjectURL(new Blob([contenu], { type: "text/csv;charset=utf-8" }));
  lien.download = nom;
  lien.click();
  URL.revokeObjectURL(lien.href);
};

export default function ProgrammePage() {
  const { enqueueSnackbar } = useSnackbar();
  const fichierRef = useRef(null);

  const [lignes, setLignes] = useState([]);
  const [classes, setClasses] = useState([]);
  const [matieres, setMatieres] = useState([]);
  const [professeurs, setProfesseurs] = useState([]);
  const [chargement, setChargement] = useState(true);
  const [filtreClasse, setFiltreClasse] = useState("");
  const [edition, setEdition] = useState(null);      // ligne en cours d'édition
  const [erreurs, setErreurs] = useState(null);
  const [confirmVider, setConfirmVider] = useState(false);
  const [importEnCours, setImportEnCours] = useState(false);

  const charger = useCallback(async () => {
    setChargement(true);
    try {
      const [p, c, m, e] = await Promise.all([
        programmeApi.liste(), classesApi.liste(),
        matieresApi.liste(), professeursApi.liste(),
      ]);
      setLignes(p.data); setClasses(c.data);
      setMatieres(m.data); setProfesseurs(e.data);
    } finally { setChargement(false); }
  }, []);

  useEffect(() => { charger().catch(() => {}); }, [charger]);

  /** Volume hebdomadaire par classe : le premier chiffre qu'on vérifie. */
  const volumes = useMemo(() => {
    const total = {};
    const couplesVus = new Set();
    lignes.forEach((l) => {
      // Un fouj occupe la classe une seule fois, pas deux.
      if (l.couplage_id) {
        if (couplesVus.has(l.couplage_id)) return;
        couplesVus.add(l.couplage_id);
      }
      total[l.classe_id] = (total[l.classe_id] ?? 0) + l.heures_par_semaine;
    });
    return total;
  }, [lignes]);

  const visibles = filtreClasse
    ? lignes.filter((l) => l.classe_id === filtreClasse)
    : lignes;

  const enregistrerLigne = async () => {
    const { id, ...corps } = edition;
    try {
      if (id) await programmeApi.modifier(id, corps);
      else await programmeApi.ajouter(corps);
      setEdition(null);
      await charger();
      enqueueSnackbar(id ? "Ligne modifiée" : "Ligne ajoutée", { variant: "success" });
    } catch (e) {
      enqueueSnackbar(
        typeof e.response?.data?.detail === "string"
          ? e.response.data.detail : "Enregistrement impossible",
        { variant: "error" });
    }
  };

  const supprimerLigne = async (ligne) => {
    await programmeApi.supprimer(ligne.id);
    await charger();
    enqueueSnackbar(
      ligne.couplage_id ? "Fouj supprimé (les deux demi-groupes)" : "Ligne supprimée",
      { variant: "warning" });
  };

  const importer = async (evenement) => {
    const fichier = evenement.target.files?.[0];
    evenement.target.value = "";        // permet de réimporter le même fichier
    if (!fichier) return;

    setImportEnCours(true); setErreurs(null);
    try {
      const { data } = await programmeApi.importer(fichier);
      await charger();
      enqueueSnackbar(data.message, { variant: "success" });
    } catch (e) {
      const detail = e.response?.data?.detail;
      setErreurs(typeof detail === "object" ? detail
        : { message: detail ?? "Import impossible", erreurs: [] });
    } finally { setImportEnCours(false); }
  };

  const exporter = async () => {
    const { data } = await programmeApi.exporter();
    telecharger(data, "programme.csv");
  };

  const telechargerModele = async () => {
    const { data } = await programmeApi.modele();
    telecharger(data, "modele-programme.csv");
  };

  const totalHeures = lignes.reduce((n, l) => n + l.heures_par_semaine, 0);

  return (
    <ContentBox>
      <Box mb={3}>
        <Typography variant="h5" fontWeight={600}>Programme annuel</Typography>
        <Typography variant="body2" color="text.secondary">
          Enregistré une fois pour l'année. La génération le reprend
          automatiquement : vous n'avez plus à le ressaisir.
        </Typography>
      </Box>

      {erreurs && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setErreurs(null)}>
          <AlertTitle>{erreurs.message}</AlertTitle>
          <Box component="ul" sx={{ pl: 3, m: 0 }}>
            {(erreurs.erreurs ?? []).map((m, i) => <li key={i}>{m}</li>)}
          </Box>
          {erreurs.erreurs_totales > (erreurs.erreurs ?? []).length && (
            <Typography variant="caption">
              … et {erreurs.erreurs_totales - erreurs.erreurs.length} autre(s)
            </Typography>
          )}
        </Alert>
      )}

      {/* Volume par classe : l'anomalie saute aux yeux ici. */}
      {classes.length > 0 && (
        <Card sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" fontWeight={700} mb={1}>
            Volume hebdomadaire par classe
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {classes.map((c) => (
              <Chip
                key={c.id} size="small"
                label={`${c.nom} — ${volumes[c.id] ?? 0} h`}
                color={volumes[c.id] ? "primary" : "default"}
                variant={filtreClasse === c.id ? "filled" : "outlined"}
                onClick={() => setFiltreClasse(filtreClasse === c.id ? "" : c.id)}
              />
            ))}
          </Box>
          <Typography variant="caption" color="text.secondary" mt={1} display="block">
            {lignes.length} lignes · {totalHeures} heures-professeur au total.
            Cliquez une classe pour filtrer.
          </Typography>
        </Card>
      )}

      <Card>
        <Box p={2} display="flex" gap={1} flexWrap="wrap" alignItems="center">
          <Button variant="contained" startIcon={<Icon>add</Icon>}
                  onClick={() => setEdition({ ...LIGNE_VIDE })}>
            Ajouter une ligne
          </Button>
          <Button variant="outlined" startIcon={<Icon>upload_file</Icon>}
                  onClick={() => fichierRef.current?.click()}>
            Importer un CSV
          </Button>
          <input ref={fichierRef} type="file" accept=".csv,text/csv"
                 hidden onChange={importer} />
          <Button variant="outlined" startIcon={<Icon>download</Icon>}
                  onClick={exporter} disabled={!lignes.length}>
            Exporter
          </Button>
          <Button size="small" color="inherit" onClick={telechargerModele}>
            Télécharger un modèle
          </Button>
          <Box flex={1} />
          {lignes.length > 0 && (
            <Button color="error" size="small" startIcon={<Icon>delete_sweep</Icon>}
                    onClick={() => setConfirmVider(true)}>
              Tout effacer
            </Button>
          )}
        </Box>

        {(chargement || importEnCours) && <LinearProgress />}

        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Classe</TableCell>
                <TableCell>Matière</TableCell>
                <TableCell>Enseignant</TableCell>
                <TableCell align="center">H/sem.</TableCell>
                <TableCell align="center">Blocs 2 h</TableCell>
                <TableCell align="center">Max/jour</TableCell>
                <TableCell>Fouj</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {visibles.length === 0 && !chargement && (
                <TableRow>
                  <TableCell colSpan={8}>
                    <Box py={4} textAlign="center">
                      <Typography color="text.secondary" mb={1}>
                        Aucune ligne de programme.
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Ajoutez-les une par une, ou importez un fichier CSV
                        — le modèle indique les colonnes attendues.
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              )}
              {visibles.map((l) => (
                <TableRow key={l.id} hover>
                  <TableCell>{l.classe_nom}</TableCell>
                  <TableCell>{l.matiere_nom}</TableCell>
                  <TableCell>{l.professeur_nom}</TableCell>
                  <TableCell align="center">{l.heures_par_semaine}</TableCell>
                  <TableCell align="center">{l.nb_seances_doubles || "—"}</TableCell>
                  <TableCell align="center">{l.max_heures_par_jour}</TableCell>
                  <TableCell>
                    {l.couplage_id ? (
                      <Tooltip title="Deux demi-groupes au même créneau">
                        <Chip size="small" color="secondary" variant="outlined"
                              label={`${l.couplage_id.split(":").pop()} · ${l.groupe}`} />
                      </Tooltip>
                    ) : "—"}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => setEdition({ ...l })}>
                      <Icon fontSize="small">edit</Icon>
                    </IconButton>
                    <IconButton size="small" color="error"
                                onClick={() => supprimerLigne(l)}>
                      <Icon fontSize="small">delete</Icon>
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* ── Édition d'une ligne ── */}
      <Dialog open={!!edition} onClose={() => setEdition(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{edition?.id ? "Modifier la ligne" : "Nouvelle ligne"}</DialogTitle>
        <DialogContent dividers>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <TextField select label="Classe" size="small" required
                       value={edition?.classe_id ?? ""}
                       onChange={(e) => setEdition({ ...edition, classe_id: e.target.value })}>
              {classes.map((c) => <MenuItem key={c.id} value={c.id}>{c.nom}</MenuItem>)}
            </TextField>
            <TextField select label="Matière" size="small" required
                       value={edition?.matiere_id ?? ""}
                       onChange={(e) => setEdition({ ...edition, matiere_id: e.target.value })}>
              {matieres.map((m) => <MenuItem key={m.id} value={m.id}>{m.nom}</MenuItem>)}
            </TextField>
            <TextField select label="Enseignant" size="small" required
                       value={edition?.professeur_id ?? ""}
                       onChange={(e) => setEdition({ ...edition, professeur_id: e.target.value })}>
              {professeurs.map((p) => (
                <MenuItem key={p.id} value={p.id}>{p.prenom} {p.nom}</MenuItem>
              ))}
            </TextField>
            <Box display="flex" gap={2}>
              <TextField label="Heures / semaine" type="number" size="small" fullWidth
                         inputProps={{ min: 1, max: 40 }}
                         value={edition?.heures_par_semaine ?? 2}
                         onChange={(e) => setEdition({
                           ...edition, heures_par_semaine: +e.target.value })} />
              <TextField label="Blocs de 2 h" type="number" size="small" fullWidth
                         inputProps={{ min: 0, max: 10 }}
                         value={edition?.nb_seances_doubles ?? 0}
                         onChange={(e) => setEdition({
                           ...edition, nb_seances_doubles: +e.target.value })} />
              <TextField label="Max / jour" type="number" size="small" fullWidth
                         inputProps={{ min: 1, max: 12 }}
                         value={edition?.max_heures_par_jour ?? 2}
                         onChange={(e) => setEdition({
                           ...edition, max_heures_par_jour: +e.target.value })} />
            </Box>
            {edition?.couplage_id && (
              <Alert severity="info">
                Cette ligne appartient à un fouj ({edition.groupe}). Modifier
                la classe ou le volume ici désynchroniserait les deux
                demi-groupes : passez par l'import CSV pour refaire le couple.
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setEdition(null)} color="inherit">Annuler</Button>
          <Button variant="contained" onClick={enregistrerLigne}
                  disabled={!edition?.classe_id || !edition?.matiere_id
                            || !edition?.professeur_id}>
            Enregistrer
          </Button>
        </DialogActions>
      </Dialog>

      {/* ── Effacement complet ── */}
      <Dialog open={confirmVider} onClose={() => setConfirmVider(false)}>
        <DialogTitle>Effacer tout le programme ?</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2">
            Les {lignes.length} lignes seront supprimées. Les emplois du
            temps déjà générés ne sont pas touchés.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setConfirmVider(false)} color="inherit">Annuler</Button>
          <Button variant="contained" color="error" onClick={async () => {
            await programmeApi.vider();
            setConfirmVider(false);
            await charger();
            enqueueSnackbar("Programme effacé", { variant: "warning" });
          }}>
            Effacer
          </Button>
        </DialogActions>
      </Dialog>
    </ContentBox>
  );
}
