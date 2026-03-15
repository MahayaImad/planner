/**
 * Dialogue générique pour les formulaires CRUD.
 * Reçoit : open, onClose, title, children, onSubmit, loading
 */
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import LoadingButton from "@mui/lab/LoadingButton";

export default function CrudDialog({ open, onClose, title, children, onSubmit, loading }) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{title}</DialogTitle>
      <form onSubmit={onSubmit}>
        <DialogContent dividers sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}>
          {children}
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button onClick={onClose} variant="outlined" color="inherit">
            Annuler
          </Button>
          <LoadingButton type="submit" variant="contained" loading={loading}>
            Enregistrer
          </LoadingButton>
        </DialogActions>
      </form>
    </Dialog>
  );
}
