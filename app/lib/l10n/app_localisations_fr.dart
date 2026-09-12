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
}
