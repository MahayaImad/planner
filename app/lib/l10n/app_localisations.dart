import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localisations_ar.dart';
import 'app_localisations_fr.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of L
/// returned by `L.of(context)`.
///
/// Applications need to include `L.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localisations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: L.localizationsDelegates,
///   supportedLocales: L.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the L.supportedLocales
/// property.
abstract class L {
  L(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static L of(BuildContext context) {
    return Localizations.of<L>(context, L)!;
  }

  static const LocalizationsDelegate<L> delegate = _LDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('fr')
  ];

  /// No description provided for @appNom.
  ///
  /// In fr, this message translates to:
  /// **'Planner'**
  String get appNom;

  /// No description provided for @appSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Emplois du temps des CEM et lycées'**
  String get appSousTitre;

  /// No description provided for @langue.
  ///
  /// In fr, this message translates to:
  /// **'Langue'**
  String get langue;

  /// No description provided for @francais.
  ///
  /// In fr, this message translates to:
  /// **'Français'**
  String get francais;

  /// No description provided for @arabe.
  ///
  /// In fr, this message translates to:
  /// **'العربية'**
  String get arabe;

  /// No description provided for @connexion.
  ///
  /// In fr, this message translates to:
  /// **'Connexion'**
  String get connexion;

  /// No description provided for @connexionTitre.
  ///
  /// In fr, this message translates to:
  /// **'Connectez-vous'**
  String get connexionTitre;

  /// No description provided for @connexionSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Accédez à l\'espace de votre établissement.'**
  String get connexionSousTitre;

  /// No description provided for @email.
  ///
  /// In fr, this message translates to:
  /// **'Adresse e-mail'**
  String get email;

  /// No description provided for @motDePasse.
  ///
  /// In fr, this message translates to:
  /// **'Mot de passe'**
  String get motDePasse;

  /// No description provided for @seConnecter.
  ///
  /// In fr, this message translates to:
  /// **'Se connecter'**
  String get seConnecter;

  /// No description provided for @creerUnCompte.
  ///
  /// In fr, this message translates to:
  /// **'Créer un établissement'**
  String get creerUnCompte;

  /// No description provided for @inscriptionTitre.
  ///
  /// In fr, this message translates to:
  /// **'Créer un établissement'**
  String get inscriptionTitre;

  /// No description provided for @inscriptionSousTitre.
  ///
  /// In fr, this message translates to:
  /// **'Quelques informations suffisent pour démarrer.'**
  String get inscriptionSousTitre;

  /// No description provided for @nomEtablissement.
  ///
  /// In fr, this message translates to:
  /// **'Nom de l\'établissement'**
  String get nomEtablissement;

  /// No description provided for @emailEtablissement.
  ///
  /// In fr, this message translates to:
  /// **'E-mail de l\'établissement'**
  String get emailEtablissement;

  /// No description provided for @nom.
  ///
  /// In fr, this message translates to:
  /// **'Nom'**
  String get nom;

  /// No description provided for @prenom.
  ///
  /// In fr, this message translates to:
  /// **'Prénom'**
  String get prenom;

  /// No description provided for @sInscrire.
  ///
  /// In fr, this message translates to:
  /// **'Créer l\'établissement'**
  String get sInscrire;

  /// No description provided for @dejaUnCompte.
  ///
  /// In fr, this message translates to:
  /// **'Vous avez déjà un compte ?'**
  String get dejaUnCompte;

  /// No description provided for @seDeconnecter.
  ///
  /// In fr, this message translates to:
  /// **'Se déconnecter'**
  String get seDeconnecter;

  /// No description provided for @champObligatoire.
  ///
  /// In fr, this message translates to:
  /// **'Ce champ est obligatoire'**
  String get champObligatoire;

  /// No description provided for @emailInvalide.
  ///
  /// In fr, this message translates to:
  /// **'Adresse e-mail invalide'**
  String get emailInvalide;

  /// No description provided for @motDePasseCourt.
  ///
  /// In fr, this message translates to:
  /// **'Au moins 12 caractères'**
  String get motDePasseCourt;

  /// No description provided for @identifiantsInvalides.
  ///
  /// In fr, this message translates to:
  /// **'E-mail ou mot de passe incorrect'**
  String get identifiantsInvalides;

  /// No description provided for @erreurReseau.
  ///
  /// In fr, this message translates to:
  /// **'Serveur injoignable. Vérifiez votre connexion.'**
  String get erreurReseau;

  /// No description provided for @tableauDeBord.
  ///
  /// In fr, this message translates to:
  /// **'Tableau de bord'**
  String get tableauDeBord;

  /// No description provided for @enseignants.
  ///
  /// In fr, this message translates to:
  /// **'Enseignants'**
  String get enseignants;

  /// No description provided for @matieres.
  ///
  /// In fr, this message translates to:
  /// **'Matières'**
  String get matieres;

  /// No description provided for @salles.
  ///
  /// In fr, this message translates to:
  /// **'Salles'**
  String get salles;

  /// No description provided for @divisions.
  ///
  /// In fr, this message translates to:
  /// **'Divisions'**
  String get divisions;

  /// No description provided for @programme.
  ///
  /// In fr, this message translates to:
  /// **'Programme'**
  String get programme;

  /// No description provided for @emploisDuTemps.
  ///
  /// In fr, this message translates to:
  /// **'Emplois du temps'**
  String get emploisDuTemps;

  /// No description provided for @statistiques.
  ///
  /// In fr, this message translates to:
  /// **'Statistiques'**
  String get statistiques;

  /// No description provided for @reglages.
  ///
  /// In fr, this message translates to:
  /// **'Réglages'**
  String get reglages;

  /// No description provided for @donnees.
  ///
  /// In fr, this message translates to:
  /// **'Données'**
  String get donnees;

  /// No description provided for @chargement.
  ///
  /// In fr, this message translates to:
  /// **'Chargement…'**
  String get chargement;

  /// No description provided for @reessayer.
  ///
  /// In fr, this message translates to:
  /// **'Réessayer'**
  String get reessayer;

  /// No description provided for @aucuneDonnee.
  ///
  /// In fr, this message translates to:
  /// **'Aucune donnée pour le moment'**
  String get aucuneDonnee;

  /// No description provided for @enregistrer.
  ///
  /// In fr, this message translates to:
  /// **'Enregistrer'**
  String get enregistrer;

  /// No description provided for @annuler.
  ///
  /// In fr, this message translates to:
  /// **'Annuler'**
  String get annuler;

  /// No description provided for @supprimer.
  ///
  /// In fr, this message translates to:
  /// **'Supprimer'**
  String get supprimer;

  /// No description provided for @modifier.
  ///
  /// In fr, this message translates to:
  /// **'Modifier'**
  String get modifier;

  /// No description provided for @ajouter.
  ///
  /// In fr, this message translates to:
  /// **'Ajouter'**
  String get ajouter;

  /// No description provided for @rechercher.
  ///
  /// In fr, this message translates to:
  /// **'Rechercher'**
  String get rechercher;

  /// No description provided for @fermer.
  ///
  /// In fr, this message translates to:
  /// **'Fermer'**
  String get fermer;

  /// No description provided for @resumeEtablissement.
  ///
  /// In fr, this message translates to:
  /// **'Votre établissement'**
  String get resumeEtablissement;

  /// No description provided for @nbEnseignants.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Aucun enseignant} =1{1 enseignant} other{{n} enseignants}}'**
  String nbEnseignants(int n);

  /// No description provided for @nbDivisions.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Aucune division} =1{1 division} other{{n} divisions}}'**
  String nbDivisions(int n);

  /// No description provided for @nbMatieres.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Aucune matière} =1{1 matière} other{{n} matières}}'**
  String nbMatieres(int n);

  /// No description provided for @nbSalles.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Aucune salle} =1{1 salle} other{{n} salles}}'**
  String nbSalles(int n);

  /// No description provided for @nbLignesProgramme.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =0{Programme vide} =1{1 ligne} other{{n} lignes}}'**
  String nbLignesProgramme(int n);

  /// No description provided for @commencerIci.
  ///
  /// In fr, this message translates to:
  /// **'Par où commencer'**
  String get commencerIci;

  /// No description provided for @etapeDonnees.
  ///
  /// In fr, this message translates to:
  /// **'Chargez vos données'**
  String get etapeDonnees;

  /// No description provided for @etapeDonneesAide.
  ///
  /// In fr, this message translates to:
  /// **'Téléchargez le classeur Excel, remplissez-le, téléversez-le.'**
  String get etapeDonneesAide;

  /// No description provided for @etapeProgramme.
  ///
  /// In fr, this message translates to:
  /// **'Vérifiez le programme'**
  String get etapeProgramme;

  /// No description provided for @etapeProgrammeAide.
  ///
  /// In fr, this message translates to:
  /// **'Qui enseigne quoi, à quelle division, combien d\'heures.'**
  String get etapeProgrammeAide;

  /// No description provided for @etapeGenerer.
  ///
  /// In fr, this message translates to:
  /// **'Générez l\'emploi du temps'**
  String get etapeGenerer;

  /// No description provided for @etapeGenererAide.
  ///
  /// In fr, this message translates to:
  /// **'Puis ajustez à la main ce qui doit l\'être.'**
  String get etapeGenererAide;

  /// No description provided for @classeurTitre.
  ///
  /// In fr, this message translates to:
  /// **'Classeur Excel'**
  String get classeurTitre;

  /// No description provided for @classeurAide.
  ///
  /// In fr, this message translates to:
  /// **'Remplissez un tableur plutôt que des dizaines d\'écrans.'**
  String get classeurAide;

  /// No description provided for @telechargerModele.
  ///
  /// In fr, this message translates to:
  /// **'Télécharger le modèle'**
  String get telechargerModele;

  /// No description provided for @exporterDonnees.
  ///
  /// In fr, this message translates to:
  /// **'Exporter mes données'**
  String get exporterDonnees;

  /// No description provided for @importerClasseur.
  ///
  /// In fr, this message translates to:
  /// **'Téléverser un classeur'**
  String get importerClasseur;

  /// No description provided for @verifierSansEcrire.
  ///
  /// In fr, this message translates to:
  /// **'Vérifier sans rien écrire'**
  String get verifierSansEcrire;

  /// No description provided for @importReussi.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 ligne importée} other{{n} lignes importées}}'**
  String importReussi(int n);

  /// No description provided for @importRefuse.
  ///
  /// In fr, this message translates to:
  /// **'Import refusé : rien n\'a été écrit.'**
  String get importRefuse;

  /// No description provided for @plus.
  ///
  /// In fr, this message translates to:
  /// **'Plus'**
  String get plus;

  /// No description provided for @ecranAVenir.
  ///
  /// In fr, this message translates to:
  /// **'Cet écran arrive bientôt.'**
  String get ecranAVenir;

  /// No description provided for @fichierEnregistre.
  ///
  /// In fr, this message translates to:
  /// **'Fichier enregistré.'**
  String get fichierEnregistre;

  /// No description provided for @importApplique.
  ///
  /// In fr, this message translates to:
  /// **'Import appliqué.'**
  String get importApplique;

  /// No description provided for @importValide.
  ///
  /// In fr, this message translates to:
  /// **'Fichier valide. Rien n\'a été écrit.'**
  String get importValide;

  /// No description provided for @feuille.
  ///
  /// In fr, this message translates to:
  /// **'Feuille'**
  String get feuille;

  /// No description provided for @creees.
  ///
  /// In fr, this message translates to:
  /// **'Créées'**
  String get creees;

  /// No description provided for @misesAJour.
  ///
  /// In fr, this message translates to:
  /// **'Mises à jour'**
  String get misesAJour;

  /// No description provided for @absentsDuFichier.
  ///
  /// In fr, this message translates to:
  /// **'{feuille} : présents en base mais absents du fichier — {noms}'**
  String absentsDuFichier(String feuille, String noms);
}

class _LDelegate extends LocalizationsDelegate<L> {
  const _LDelegate();

  @override
  Future<L> load(Locale locale) {
    return SynchronousFuture<L>(lookupL(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ar', 'fr'].contains(locale.languageCode);

  @override
  bool shouldReload(_LDelegate old) => false;
}

L lookupL(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return LAr();
    case 'fr':
      return LFr();
  }

  throw FlutterError(
      'L.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
