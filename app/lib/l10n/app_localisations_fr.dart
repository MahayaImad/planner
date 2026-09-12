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
}
