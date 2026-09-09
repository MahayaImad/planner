/**
 * Grille horaire de référence.
 *
 * Doit rester alignée sur les valeurs par défaut de GrilleInput côté
 * backend (app/schemas/schedule.py) : c'est cette grille qui sert à
 * traduire une case cochée en créneau. Un jour ou un horaire qui ne
 * correspond à rien côté serveur est ignoré sans message — d'où ce
 * fichier unique plutôt qu'une liste recopiée dans chaque écran.
 */

// Semaine scolaire algérienne : le week-end est vendredi-samedi.
export const JOURS = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi"];

export const SEANCES = [
  { index: 0, debut: "08:00", fin: "08:55", demiJournee: "matin" },
  { index: 1, debut: "09:00", fin: "09:55", demiJournee: "matin" },
  { index: 2, debut: "10:05", fin: "11:00", demiJournee: "matin" },
  { index: 3, debut: "11:05", fin: "12:00", demiJournee: "matin" },
  { index: 4, debut: "13:00", fin: "13:55", demiJournee: "apres-midi" },
  { index: 5, debut: "14:00", fin: "14:55", demiJournee: "apres-midi" },
  { index: 6, debut: "15:05", fin: "16:00", demiJournee: "apres-midi" },
];

export const HEURES_DEBUT = SEANCES.map((s) => s.debut);

/** Libellé lisible d'une séance : « S3 · 10:05-11:00 ». */
export const libelleSeance = (s) => `S${s.index + 1} · ${s.debut}-${s.fin}`;
