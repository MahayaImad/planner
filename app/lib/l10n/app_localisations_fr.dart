// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localisations.dart';

// ignore_for_file: type=lint

/// The translations for French (`fr`).
class LFr extends L {
  LFr([String locale = 'fr']) : super(locale);

  @override
  String get appNom => 'Planner';

  @override
  String get appSousTitre => 'Emplois du temps des CEM et lycées';

  @override
  String get langue => 'Langue';

  @override
  String get francais => 'Français';

  @override
  String get arabe => 'العربية';

  @override
  String get connexion => 'Connexion';

  @override
  String get connexionTitre => 'Connectez-vous';

  @override
  String get connexionSousTitre =>
      'Accédez à l\'espace de votre établissement.';

  @override
  String get email => 'Adresse e-mail';

  @override
  String get motDePasse => 'Mot de passe';

  @override
  String get seConnecter => 'Se connecter';

  @override
  String get creerUnCompte => 'Créer un établissement';

  @override
  String get inscriptionTitre => 'Créer un établissement';

  @override
  String get inscriptionSousTitre =>
      'Quelques informations suffisent pour démarrer.';

  @override
  String get nomEtablissement => 'Nom de l\'établissement';

  @override
  String get emailEtablissement => 'E-mail de l\'établissement';

  @override
  String get nom => 'Nom';

  @override
  String get prenom => 'Prénom';

  @override
  String get sInscrire => 'Créer l\'établissement';

  @override
  String get dejaUnCompte => 'Vous avez déjà un compte ?';

  @override
  String get seDeconnecter => 'Se déconnecter';

  @override
  String get champObligatoire => 'Ce champ est obligatoire';

  @override
  String get emailInvalide => 'Adresse e-mail invalide';

  @override
  String get motDePasseCourt => 'Au moins 12 caractères';

  @override
  String get identifiantsInvalides => 'E-mail ou mot de passe incorrect';

  @override
  String get erreurReseau => 'Serveur injoignable. Vérifiez votre connexion.';

  @override
  String get tableauDeBord => 'Tableau de bord';

  @override
  String get enseignants => 'Enseignants';

  @override
  String get matieres => 'Matières';

  @override
  String get salles => 'Salles';

  @override
  String get divisions => 'Divisions';

  @override
  String get programme => 'Programme';

  @override
  String get emploisDuTemps => 'Emplois du temps';

  @override
  String get statistiques => 'Statistiques';

  @override
  String get reglages => 'Réglages';

  @override
  String get donnees => 'Données';

  @override
  String get chargement => 'Chargement…';

  @override
  String get reessayer => 'Réessayer';

  @override
  String get aucuneDonnee => 'Aucune donnée pour le moment';

  @override
  String get enregistrer => 'Enregistrer';

  @override
  String get annuler => 'Annuler';

  @override
  String get supprimer => 'Supprimer';

  @override
  String get modifier => 'Modifier';

  @override
  String get ajouter => 'Ajouter';

  @override
  String get rechercher => 'Rechercher';

  @override
  String get fermer => 'Fermer';

  @override
  String get resumeEtablissement => 'Votre établissement';

  @override
  String nbEnseignants(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n enseignants',
      one: '1 enseignant',
      zero: 'Aucun enseignant',
    );
    return '$_temp0';
  }

  @override
  String nbDivisions(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n divisions',
      one: '1 division',
      zero: 'Aucune division',
    );
    return '$_temp0';
  }

  @override
  String nbMatieres(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n matières',
      one: '1 matière',
      zero: 'Aucune matière',
    );
    return '$_temp0';
  }

  @override
  String nbSalles(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n salles',
      one: '1 salle',
      zero: 'Aucune salle',
    );
    return '$_temp0';
  }

  @override
  String nbLignesProgramme(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n lignes',
      one: '1 ligne',
      zero: 'Programme vide',
    );
    return '$_temp0';
  }

  @override
  String get commencerIci => 'Par où commencer';

  @override
  String get etapeDonnees => 'Chargez vos données';

  @override
  String get etapeDonneesAide =>
      'Téléchargez le classeur Excel, remplissez-le, téléversez-le.';

  @override
  String get etapeProgramme => 'Vérifiez le programme';

  @override
  String get etapeProgrammeAide =>
      'Qui enseigne quoi, à quelle division, combien d\'heures.';

  @override
  String get etapeGenerer => 'Générez l\'emploi du temps';

  @override
  String get etapeGenererAide => 'Puis ajustez à la main ce qui doit l\'être.';

  @override
  String get classeurTitre => 'Classeur Excel';

  @override
  String get classeurAide =>
      'Remplissez un tableur plutôt que des dizaines d\'écrans.';

  @override
  String get telechargerModele => 'Télécharger le modèle';

  @override
  String get exporterDonnees => 'Exporter mes données';

  @override
  String get importerClasseur => 'Téléverser un classeur';

  @override
  String get verifierSansEcrire => 'Vérifier sans rien écrire';

  @override
  String importReussi(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n lignes importées',
      one: '1 ligne importée',
    );
    return '$_temp0';
  }

  @override
  String get importRefuse => 'Import refusé : rien n\'a été écrit.';

  @override
  String get plus => 'Plus';

  @override
  String get ecranAVenir => 'Cet écran arrive bientôt.';

  @override
  String get fichierEnregistre => 'Fichier enregistré.';

  @override
  String get importApplique => 'Import appliqué.';

  @override
  String get importValide => 'Fichier valide. Rien n\'a été écrit.';

  @override
  String get feuille => 'Feuille';

  @override
  String get creees => 'Créées';

  @override
  String get misesAJour => 'Mises à jour';

  @override
  String absentsDuFichier(String feuille, String noms) {
    return '$feuille : présents en base mais absents du fichier — $noms';
  }

  @override
  String get nombreAttendu => 'Entrez un nombre';

  @override
  String horsBornes(String min, String max) {
    return 'Entre $min et $max';
  }

  @override
  String get aucun => 'Aucun';

  @override
  String confirmerSuppression(String nom) {
    return 'Supprimer « $nom » ?';
  }

  @override
  String get suppressionEnCascade =>
      'Les leçons et lignes de programme qui s\'y rattachent seront supprimées.';

  @override
  String get nouvel => 'Nouveau';

  @override
  String get modifierTitre => 'Modifier';

  @override
  String get telephone => 'Téléphone';

  @override
  String get heuresConsecutivesMax => 'Heures consécutives max';

  @override
  String get heuresParJourMax => 'Heures par jour max';

  @override
  String get heuresParSemaineMax => 'Heures par semaine max';

  @override
  String get assurePermanences => 'Assure les permanences';

  @override
  String get aidePermanences =>
      'Peut encadrer une heure d\'accueil pour combler un trou.';

  @override
  String get aidePlafondHebdo => 'Laissez vide s\'il n\'y a pas de plafond.';

  @override
  String get aideMatieresEnseignant =>
      'Ce que cet enseignant peut prendre en charge.';

  @override
  String get aideEnseignantsVide =>
      'Ajoutez vos enseignants, ou chargez-les d\'un coup par classeur Excel.';

  @override
  String get aideMatieresVide =>
      'Les disciplines enseignées dans l\'établissement.';

  @override
  String get aideSallesVide =>
      'Salles de classe, laboratoires, terrain de sport.';

  @override
  String get aideDivisionsVide =>
      'Les classes de l\'établissement : 1AM1, 4AM A…';

  @override
  String get aideProgrammeVide =>
      'Qui enseigne quoi, à quelle division, combien d\'heures.';

  @override
  String get coefficient => 'Coefficient';

  @override
  String coefficientValeur(String valeur) {
    return 'Coefficient $valeur';
  }

  @override
  String get typeSalleRequis => 'Type de salle exigé';

  @override
  String get aideTypeSalle => 'Laissez vide pour une salle ordinaire.';

  @override
  String get typeSalle => 'Type';

  @override
  String get capacite => 'Capacité';

  @override
  String places(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n places',
      one: '1 place',
    );
    return '$_temp0';
  }

  @override
  String get niveau => 'Niveau';

  @override
  String get effectif => 'Effectif';

  @override
  String eleves(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n élèves',
      one: '1 élève',
    );
    return '$_temp0';
  }

  @override
  String get salleAttitree => 'Salle attitrée';

  @override
  String get aideSalleAttitree =>
      'Là où la division passe ses heures ordinaires.';

  @override
  String heuresParSemaine(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n h/semaine',
      one: '1 h/semaine',
    );
    return '$_temp0';
  }

  @override
  String heuresParJour(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n h/jour',
      one: '1 h/jour',
    );
    return '$_temp0';
  }

  @override
  String get heuresParSemaineLibelle => 'Heures par semaine';

  @override
  String get blocsDeuxHeures => 'Blocs de 2 h';

  @override
  String blocsDeDeuxHeures(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n blocs de 2 h',
      one: '1 bloc de 2 h',
    );
    return '$_temp0';
  }

  @override
  String get aideBlocs => 'Séances doubles à réserver dans ce volume.';

  @override
  String get maxParJour => 'Max par jour';

  @override
  String get fouj => 'Fouj (couplage)';

  @override
  String get aideFouj => 'Même libellé sur les deux lignes d\'un dédoublement.';

  @override
  String get demiGroupe => 'Demi-groupe';

  @override
  String get division => 'Division';

  @override
  String get matiere => 'Matière';

  @override
  String get enseignant => 'Enseignant';

  @override
  String get parDivision => 'Par division';

  @override
  String get parEnseignant => 'Par enseignant';

  @override
  String get parSalle => 'Par salle';

  @override
  String get aucunEmploiDuTemps => 'Aucun emploi du temps';

  @override
  String get aideAucunEmploiDuTemps =>
      'Créez-en un, puis lancez une génération.';

  @override
  String get aucuneLecon => 'Cet emploi du temps est vide';

  @override
  String get aideAucuneLecon =>
      'Lancez une génération pour obtenir une proposition.';

  @override
  String get motifSeanceFermee => 'Séance fermée dans la grille horaire';

  @override
  String get motifProfesseurOccupe =>
      'L\'enseignant a déjà cours à cette heure';

  @override
  String get motifProfesseurIndisponible =>
      'L\'enseignant est indisponible à cette heure';

  @override
  String get motifDivisionOccupee => 'La division a déjà cours à cette heure';

  @override
  String get motifAucuneSalle => 'Aucune salle du bon type n\'est libre';

  @override
  String get motifFenetre => 'Cette matière est interdite sur cette plage';

  @override
  String get motifPlafondProfesseur =>
      'L\'enseignant atteindrait son plafond du jour';

  @override
  String get motifPlafondDivision =>
      'La division atteindrait son plafond du jour';

  @override
  String get motifPlafondMatiere =>
      'Cette matière atteindrait son plafond du jour';

  @override
  String get motifConsecutives =>
      'L\'enseignant dépasserait ses heures consécutives';

  @override
  String get genererTitre => 'Générer l\'emploi du temps';

  @override
  String get genererAide =>
      'Le solveur propose une grille complète. Vous pourrez ensuite la retoucher à la main.';

  @override
  String get tempsDeCalcul => 'Temps de calcul';

  @override
  String get aideTempsDeCalcul =>
      'Plus long ne veut pas dire beaucoup mieux : l\'essentiel se joue dans les premières minutes.';

  @override
  String minutes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n minutes',
      one: '1 minute',
    );
    return '$_temp0';
  }

  @override
  String get lancer => 'Lancer';

  @override
  String get interrompre => 'Interrompre';

  @override
  String get laisserTourner => 'Laisser tourner';

  @override
  String secondesEcoulees(int ecoule, int limite) {
    return '$ecoule s sur $limite s';
  }

  @override
  String solutionsTrouvees(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n solutions',
      one: '1 solution',
    );
    return '$_temp0';
  }

  @override
  String coutCourant(String valeur) {
    return 'Coût $valeur';
  }

  @override
  String leconsPlacees(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n leçons placées',
      one: '1 leçon placée',
    );
    return '$_temp0';
  }

  @override
  String get qualiteObtenue => 'Qualité obtenue';

  @override
  String trousEleves(String n) {
    return 'Trous élèves : $n';
  }

  @override
  String trousProfesseurs(String n) {
    return 'Trous professeurs : $n';
  }

  @override
  String get generer => 'Générer';

  @override
  String get heuresPlacees => 'heures placées';

  @override
  String get trousElevesCourt => 'trous élèves';

  @override
  String get trousProfesseursCourt => 'trous professeurs';

  @override
  String get demiJourneesIsolees => 'demi-journées à 1 h';

  @override
  String get journeesSixHeures => 'journées à 6 h ou plus';

  @override
  String get matieresTroisHeures => 'matières à 3 h le même jour';

  @override
  String get occupationSeances => 'Occupation des séances';

  @override
  String get serviceDesProfesseurs => 'Service des professeurs';

  @override
  String get chargeDesDivisions => 'Charge des divisions';

  @override
  String get heures => 'Heures';

  @override
  String get jours => 'Jours';

  @override
  String get trous => 'Trous';

  @override
  String get maxJour => 'Max/jour';

  @override
  String get journeeLaPlusChargee => 'Journée la plus chargée';

  @override
  String get ongletGrille => 'Grille horaire';

  @override
  String get ongletCriteres => 'Critères';

  @override
  String get ongletFenetres => 'Fenêtres';

  @override
  String get reglagesEnregistres => 'Réglages enregistrés.';

  @override
  String get fermeturesTitre => 'Séances ouvertes';

  @override
  String get fermeturesAide =>
      'Décochez une case pour fermer la séance ce jour-là. Le mardi après-midi, par exemple.';

  @override
  String get horairesTitre => 'Horaires des séances';

  @override
  String get debut => 'Début';

  @override
  String get fin => 'Fin';

  @override
  String get tempsDeCalculDefaut => 'Temps de calcul par défaut (s)';

  @override
  String get aideTempsDefaut =>
      'Utilisé quand une génération n\'en précise pas.';

  @override
  String get typeSalleOrdinaire => 'Type de salle ordinaire';

  @override
  String get aideTypeSalleOrdinaire =>
      'Nom du type utilisé pour les cours sans exigence particulière.';

  @override
  String get criteresAide =>
      'Ces poids arbitrent entre des souhaits contradictoires. Zéro désactive un critère ; aucun n\'empêche une génération d\'aboutir.';

  @override
  String get critereTrousProfesseurs => 'Heure creuse d\'un professeur';

  @override
  String get aideTrousProfesseurs =>
      'Une heure sans cours au milieu de sa demi-journée.';

  @override
  String get critereVideDeuxHeures => 'Vide de deux heures';

  @override
  String get aideVideDeuxHeures =>
      'Deux heures creuses d\'affilée : bien pire qu\'une seule.';

  @override
  String get critereJourneeHachee => 'Journée hachée';

  @override
  String get aideJourneeHachee =>
      'Plus d\'une heure creuse dans la même journée, pause déjeuner comprise dans l\'amplitude.';

  @override
  String get critereHeureIsolee => 'Déplacement pour une seule heure';

  @override
  String get aideHeureIsolee =>
      'Le professeur ne vient qu\'une heure sur la demi-journée.';

  @override
  String get critereJourPresence => 'Jour de présence';

  @override
  String get aideJourPresence => 'Chaque jour en moins est un jour libéré.';

  @override
  String get criterePermanence => 'Permanence (récompense)';

  @override
  String get aidePermanenceCritere =>
      'Bonus quand une heure creuse est comblée par de l\'accueil.';

  @override
  String get critereBlocsHorsPolitique => 'Bloc hors politique du programme';

  @override
  String get aideBlocsHorsPolitique =>
      'Le programme dit comment répartir une matière entre les journées : un bloc de 2 h autorise une seule journée doublée.';

  @override
  String get critereMatieresRepetees => 'Matières doublées empilées';

  @override
  String get aideMatieresRepetees =>
      'Plusieurs matières à 2 h ou plus le même jour pour une division.';

  @override
  String get critereEquiteFins => 'Équité des fins tardives';

  @override
  String get aideEquiteFins =>
      'Répartit les dernières séances entre les divisions.';

  @override
  String get critereEquilibreJournees => 'Équilibre des journées';

  @override
  String get aideEquilibreJournees =>
      'Évite d\'alterner journées très chargées et très légères.';

  @override
  String get critereDemiJournees => 'Demi-journée travaillée';

  @override
  String get aideDemiJournees =>
      'Regroupe les cours sur moins de demi-journées.';

  @override
  String get critereMatieresLourdes => 'Matière lourde l\'après-midi';

  @override
  String get aideMatieresLourdes =>
      'Pousse les matières à fort coefficient vers le matin.';

  @override
  String get seuilsSeanceTitre => 'Heure de sortie des élèves';

  @override
  String get seuilsSeanceAide =>
      'Coût d\'occupation de chaque séance. Laissez à zéro celles que vous jugez idéales.';

  @override
  String get seuilsChargeTitre => 'Charge quotidienne des professeurs';

  @override
  String get seuilsChargeAide =>
      'Coût d\'atteindre ce nombre d\'heures dans la journée. Les seuils se cumulent.';

  @override
  String get fenetresAide =>
      'Une fenêtre interdit une matière sur une plage dans tout l\'établissement — journée d\'inspection, réunion de coordination.';

  @override
  String get aucuneFenetre => 'Aucune fenêtre déclarée.';

  @override
  String fenetreDetail(String jour, String seances) {
    return 'Jour $jour · séances $seances';
  }

  @override
  String get ajouterFenetre => 'Déclarer une fenêtre';

  @override
  String get jour => 'Jour';

  @override
  String get seancesBloquees => 'Séances bloquées';

  @override
  String get libelle => 'Libellé';

  @override
  String get aideLibelleFenetre =>
      'Facultatif : « inspection arabe », « réunion de coordination ».';

  @override
  String get declarezDabordUneMatiere => 'Déclarez d\'abord une matière.';

  @override
  String get adresseDejaUtilisee =>
      'Cette adresse est déjà associée à un compte. Connectez-vous, ou utilisez-en une autre.';

  @override
  String get creerEmploiDuTemps => 'Créer un emploi du temps';

  @override
  String get creer => 'Créer';

  @override
  String get semaineType => 'Semaine type';
}
