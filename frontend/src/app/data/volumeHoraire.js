/**
 * Templates de volume horaire hebdomadaire pour le système scolaire algérien.
 * Basés sur les programmes officiels de l'Education Nationale.
 *
 * Chaque template définit le nombre d'heures par semaine pour chaque matière.
 * Les noms de matières sont normalisés pour faciliter la correspondance avec la BDD.
 */

export const FILIERES = [
  { value: "primaire",    label: "Primaire" },
  { value: "moyen",       label: "Moyen (CEM)" },
  { value: "secondaire",  label: "Secondaire (Lycée)" },
];

export const TEMPLATES = [
  // ─────────────────────────── PRIMAIRE ───────────────────────────
  {
    id: "primaire-1",
    label: "1ère Année Primaire",
    filiere: "primaire",
    cours: [
      { matiere: "Langue Arabe",     heures: 10 },
      { matiere: "Tamazight",        heures: 3  },
      { matiere: "Mathématiques",    heures: 5  },
      { matiere: "Éveil (Sciences)", heures: 2  },
      { matiere: "Éducation Islamique", heures: 3 },
      { matiere: "Éducation Physique",  heures: 3 },
      { matiere: "Activités Artistiques", heures: 2 },
    ],
  },
  {
    id: "primaire-2",
    label: "2ème Année Primaire",
    filiere: "primaire",
    cours: [
      { matiere: "Langue Arabe",     heures: 10 },
      { matiere: "Tamazight",        heures: 3  },
      { matiere: "Mathématiques",    heures: 5  },
      { matiere: "Éveil (Sciences)", heures: 2  },
      { matiere: "Éducation Islamique", heures: 3 },
      { matiere: "Éducation Physique",  heures: 3 },
      { matiere: "Activités Artistiques", heures: 2 },
    ],
  },
  {
    id: "primaire-3",
    label: "3ème Année Primaire",
    filiere: "primaire",
    cours: [
      { matiere: "Langue Arabe",    heures: 8 },
      { matiere: "Français",        heures: 4 },
      { matiere: "Tamazight",       heures: 3 },
      { matiere: "Mathématiques",   heures: 5 },
      { matiere: "Éveil Scientifique et Technologique", heures: 2 },
      { matiere: "Histoire & Géographie", heures: 1 },
      { matiere: "Éducation Islamique",   heures: 3 },
      { matiere: "Éducation Physique",    heures: 3 },
      { matiere: "Activités Artistiques", heures: 2 },
    ],
  },
  {
    id: "primaire-4",
    label: "4ème Année Primaire",
    filiere: "primaire",
    cours: [
      { matiere: "Langue Arabe",    heures: 8 },
      { matiere: "Français",        heures: 4 },
      { matiere: "Tamazight",       heures: 3 },
      { matiere: "Mathématiques",   heures: 5 },
      { matiere: "Éveil Scientifique et Technologique", heures: 2 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 3 },
      { matiere: "Éducation Physique",    heures: 3 },
      { matiere: "Activités Artistiques", heures: 2 },
    ],
  },
  {
    id: "primaire-5",
    label: "5ème Année Primaire",
    filiere: "primaire",
    cours: [
      { matiere: "Langue Arabe",    heures: 8 },
      { matiere: "Français",        heures: 4 },
      { matiere: "Tamazight",       heures: 3 },
      { matiere: "Mathématiques",   heures: 5 },
      { matiere: "Éveil Scientifique et Technologique", heures: 2 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 3 },
      { matiere: "Éducation Physique",    heures: 3 },
      { matiere: "Activités Artistiques", heures: 2 },
    ],
  },

  // ─────────────────────────── MOYEN (CEM) ───────────────────────────
  {
    id: "moyen-1",
    label: "1ère Année Moyenne",
    filiere: "moyen",
    cours: [
      { matiere: "Langue Arabe",          heures: 6 },
      { matiere: "Français",              heures: 5 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Tamazight",             heures: 3 },
      { matiere: "Mathématiques",         heures: 5 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 2 },
      { matiere: "Sciences Physiques",    heures: 2 },
      { matiere: "Histoire & Géographie", heures: 3 },
      { matiere: "Éducation Islamique",   heures: 3 },
      { matiere: "Technologie",           heures: 2 },
      { matiere: "Éducation Physique",    heures: 3 },
      { matiere: "Arts Plastiques",       heures: 1 },
      { matiere: "Musique",               heures: 1 },
    ],
  },
  {
    id: "moyen-2",
    label: "2ème Année Moyenne",
    filiere: "moyen",
    cours: [
      { matiere: "Langue Arabe",          heures: 6 },
      { matiere: "Français",              heures: 5 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Tamazight",             heures: 3 },
      { matiere: "Mathématiques",         heures: 5 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 2 },
      { matiere: "Sciences Physiques",    heures: 2 },
      { matiere: "Histoire & Géographie", heures: 3 },
      { matiere: "Éducation Islamique",   heures: 3 },
      { matiere: "Technologie",           heures: 2 },
      { matiere: "Éducation Physique",    heures: 3 },
      { matiere: "Arts Plastiques",       heures: 1 },
      { matiere: "Musique",               heures: 1 },
    ],
  },
  {
    id: "moyen-3",
    label: "3ème Année Moyenne",
    filiere: "moyen",
    cours: [
      { matiere: "Langue Arabe",          heures: 6 },
      { matiere: "Français",              heures: 5 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Tamazight",             heures: 3 },
      { matiere: "Mathématiques",         heures: 5 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 2 },
      { matiere: "Sciences Physiques",    heures: 2 },
      { matiere: "Histoire & Géographie", heures: 3 },
      { matiere: "Éducation Islamique",   heures: 3 },
      { matiere: "Technologie",           heures: 2 },
      { matiere: "Éducation Physique",    heures: 3 },
      { matiere: "Arts Plastiques",       heures: 1 },
      { matiere: "Musique",               heures: 1 },
    ],
  },
  {
    id: "moyen-4",
    label: "4ème Année Moyenne",
    filiere: "moyen",
    cours: [
      { matiere: "Langue Arabe",          heures: 6 },
      { matiere: "Français",              heures: 5 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Tamazight",             heures: 3 },
      { matiere: "Mathématiques",         heures: 5 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 2 },
      { matiere: "Sciences Physiques",    heures: 2 },
      { matiere: "Histoire & Géographie", heures: 3 },
      { matiere: "Éducation Islamique",   heures: 3 },
      { matiere: "Technologie",           heures: 2 },
      { matiere: "Éducation Physique",    heures: 3 },
      { matiere: "Arts Plastiques",       heures: 1 },
      { matiere: "Musique",               heures: 1 },
    ],
  },

  // ───────────── SECONDAIRE — 1ère Année (Troncs communs) ─────────────
  {
    id: "sec-1-tc-sciences",
    label: "1ère Année Secondaire – Tronc Commun Sciences",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 5 },
      { matiere: "Français",              heures: 4 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 6 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 3 },
      { matiere: "Sciences Physiques",    heures: 4 },
      { matiere: "Informatique",          heures: 2 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-1-tc-lettres",
    label: "1ère Année Secondaire – Tronc Commun Lettres & Sciences Humaines",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 6 },
      { matiere: "Français",              heures: 5 },
      { matiere: "Anglais",               heures: 4 },
      { matiere: "Sciences Islamiques",   heures: 3 },
      { matiere: "Histoire & Géographie", heures: 4 },
      { matiere: "Mathématiques",         heures: 3 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 2 },
      { matiere: "Sciences Physiques",    heures: 2 },
      { matiere: "Informatique",          heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },

  // ───────────── SECONDAIRE — 2ème Année ─────────────
  {
    id: "sec-2-sciences",
    label: "2ème Année Secondaire – Sciences de la Nature et de la Vie",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 4 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 5 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 6 },
      { matiere: "Sciences Physiques",    heures: 4 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-2-maths",
    label: "2ème Année Secondaire – Mathématiques",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 4 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 7 },
      { matiere: "Sciences Physiques",    heures: 5 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 2 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-2-lettres",
    label: "2ème Année Secondaire – Lettres & Sciences Humaines",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 7 },
      { matiere: "Français",              heures: 5 },
      { matiere: "Anglais",               heures: 4 },
      { matiere: "Sciences Islamiques",   heures: 3 },
      { matiere: "Histoire & Géographie", heures: 5 },
      { matiere: "Philosophie",           heures: 2 },
      { matiere: "Mathématiques",         heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-2-langues",
    label: "2ème Année Secondaire – Langues Étrangères",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 5 },
      { matiere: "Français",              heures: 6 },
      { matiere: "Anglais",               heures: 6 },
      { matiere: "Espagnol / Allemand / Italien", heures: 4 },
      { matiere: "Mathématiques",         heures: 2 },
      { matiere: "Histoire & Géographie", heures: 3 },
      { matiere: "Éducation Islamique",   heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-2-gestion",
    label: "2ème Année Secondaire – Gestion & Économie",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 4 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 4 },
      { matiere: "Économie & Gestion",    heures: 5 },
      { matiere: "Comptabilité",          heures: 4 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 2 },
      { matiere: "Droit",                 heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-2-technique",
    label: "2ème Année Secondaire – Technique Mathématique",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 4 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 6 },
      { matiere: "Sciences Physiques",    heures: 5 },
      { matiere: "Technologie",           heures: 4 },
      { matiere: "Dessin Technique",      heures: 2 },
      { matiere: "Éducation Islamique",   heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },

  // ───────────── SECONDAIRE — 3ème Année (Terminale) ─────────────
  {
    id: "sec-3-sciences",
    label: "3ème Année Secondaire (Terminale) – Sciences de la Nature et de la Vie",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 3 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 5 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 7 },
      { matiere: "Sciences Physiques",    heures: 4 },
      { matiere: "Philosophie",           heures: 2 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 1 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-3-maths",
    label: "3ème Année Secondaire (Terminale) – Mathématiques",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 3 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 8 },
      { matiere: "Sciences Physiques",    heures: 6 },
      { matiere: "Sciences de la Nature et de la Vie", heures: 1 },
      { matiere: "Philosophie",           heures: 2 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Islamique",   heures: 1 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-3-lettres",
    label: "3ème Année Secondaire (Terminale) – Lettres & Sciences Humaines",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 7 },
      { matiere: "Français",              heures: 4 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Sciences Islamiques",   heures: 3 },
      { matiere: "Histoire & Géographie", heures: 5 },
      { matiere: "Philosophie",           heures: 3 },
      { matiere: "Sociologie",            heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-3-langues",
    label: "3ème Année Secondaire (Terminale) – Langues Étrangères",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 4 },
      { matiere: "Français",              heures: 6 },
      { matiere: "Anglais",               heures: 6 },
      { matiere: "Espagnol / Allemand / Italien", heures: 4 },
      { matiere: "Philosophie",           heures: 2 },
      { matiere: "Histoire & Géographie", heures: 3 },
      { matiere: "Éducation Islamique",   heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-3-gestion",
    label: "3ème Année Secondaire (Terminale) – Gestion & Économie",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 3 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 4 },
      { matiere: "Économie & Gestion",    heures: 6 },
      { matiere: "Comptabilité",          heures: 5 },
      { matiere: "Droit",                 heures: 2 },
      { matiere: "Philosophie",           heures: 2 },
      { matiere: "Histoire & Géographie", heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
  {
    id: "sec-3-technique",
    label: "3ème Année Secondaire (Terminale) – Technique Mathématique",
    filiere: "secondaire",
    cours: [
      { matiere: "Langue Arabe",          heures: 3 },
      { matiere: "Français",              heures: 3 },
      { matiere: "Anglais",               heures: 3 },
      { matiere: "Mathématiques",         heures: 6 },
      { matiere: "Sciences Physiques",    heures: 5 },
      { matiere: "Technologie",           heures: 4 },
      { matiere: "Dessin Technique",      heures: 2 },
      { matiere: "Philosophie",           heures: 2 },
      { matiere: "Éducation Physique",    heures: 2 },
    ],
  },
];

/**
 * Normalise une chaîne pour comparaison : minuscules, sans accents, espaces unifiés.
 */
export const normaliser = (str) =>
  str
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

/**
 * Tente de faire correspondre le nom d'une matière du template
 * avec une matière de la BDD. Retourne l'id ou null.
 */
export const trouverMatiereId = (nomTemplate, matieresBDD) => {
  const normTemplate = normaliser(nomTemplate);
  // 1. Correspondance exacte
  const exact = matieresBDD.find((m) => normaliser(m.nom) === normTemplate);
  if (exact) return exact.id;
  // 2. La matière BDD contient le premier mot significatif du template
  const motsCles = normTemplate.split(" ").filter((w) => w.length > 3);
  if (motsCles.length > 0) {
    const partiel = matieresBDD.find((m) =>
      motsCles.some((mot) => normaliser(m.nom).includes(mot))
    );
    if (partiel) return partiel.id;
  }
  return null;
};
