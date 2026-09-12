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

  /// No description provided for @nombreAttendu.
  ///
  /// In fr, this message translates to:
  /// **'Entrez un nombre'**
  String get nombreAttendu;

  /// No description provided for @horsBornes.
  ///
  /// In fr, this message translates to:
  /// **'Entre {min} et {max}'**
  String horsBornes(String min, String max);

  /// No description provided for @aucun.
  ///
  /// In fr, this message translates to:
  /// **'Aucun'**
  String get aucun;

  /// No description provided for @confirmerSuppression.
  ///
  /// In fr, this message translates to:
  /// **'Supprimer « {nom} » ?'**
  String confirmerSuppression(String nom);

  /// No description provided for @suppressionEnCascade.
  ///
  /// In fr, this message translates to:
  /// **'Les leçons et lignes de programme qui s\'y rattachent seront supprimées.'**
  String get suppressionEnCascade;

  /// No description provided for @nouvel.
  ///
  /// In fr, this message translates to:
  /// **'Nouveau'**
  String get nouvel;

  /// No description provided for @modifierTitre.
  ///
  /// In fr, this message translates to:
  /// **'Modifier'**
  String get modifierTitre;

  /// No description provided for @telephone.
  ///
  /// In fr, this message translates to:
  /// **'Téléphone'**
  String get telephone;

  /// No description provided for @heuresConsecutivesMax.
  ///
  /// In fr, this message translates to:
  /// **'Heures consécutives max'**
  String get heuresConsecutivesMax;

  /// No description provided for @heuresParJourMax.
  ///
  /// In fr, this message translates to:
  /// **'Heures par jour max'**
  String get heuresParJourMax;

  /// No description provided for @heuresParSemaineMax.
  ///
  /// In fr, this message translates to:
  /// **'Heures par semaine max'**
  String get heuresParSemaineMax;

  /// No description provided for @assurePermanences.
  ///
  /// In fr, this message translates to:
  /// **'Assure les permanences'**
  String get assurePermanences;

  /// No description provided for @aidePermanences.
  ///
  /// In fr, this message translates to:
  /// **'Peut encadrer une heure d\'accueil pour combler un trou.'**
  String get aidePermanences;

  /// No description provided for @aidePlafondHebdo.
  ///
  /// In fr, this message translates to:
  /// **'Laissez vide s\'il n\'y a pas de plafond.'**
  String get aidePlafondHebdo;

  /// No description provided for @aideMatieresEnseignant.
  ///
  /// In fr, this message translates to:
  /// **'Ce que cet enseignant peut prendre en charge.'**
  String get aideMatieresEnseignant;

  /// No description provided for @aideEnseignantsVide.
  ///
  /// In fr, this message translates to:
  /// **'Ajoutez vos enseignants, ou chargez-les d\'un coup par classeur Excel.'**
  String get aideEnseignantsVide;

  /// No description provided for @aideMatieresVide.
  ///
  /// In fr, this message translates to:
  /// **'Les disciplines enseignées dans l\'établissement.'**
  String get aideMatieresVide;

  /// No description provided for @aideSallesVide.
  ///
  /// In fr, this message translates to:
  /// **'Salles de classe, laboratoires, terrain de sport.'**
  String get aideSallesVide;

  /// No description provided for @aideDivisionsVide.
  ///
  /// In fr, this message translates to:
  /// **'Les classes de l\'établissement : 1AM1, 4AM A…'**
  String get aideDivisionsVide;

  /// No description provided for @aideProgrammeVide.
  ///
  /// In fr, this message translates to:
  /// **'Qui enseigne quoi, à quelle division, combien d\'heures.'**
  String get aideProgrammeVide;

  /// No description provided for @coefficient.
  ///
  /// In fr, this message translates to:
  /// **'Coefficient'**
  String get coefficient;

  /// No description provided for @coefficientValeur.
  ///
  /// In fr, this message translates to:
  /// **'Coefficient {valeur}'**
  String coefficientValeur(String valeur);

  /// No description provided for @typeSalleRequis.
  ///
  /// In fr, this message translates to:
  /// **'Type de salle exigé'**
  String get typeSalleRequis;

  /// No description provided for @aideTypeSalle.
  ///
  /// In fr, this message translates to:
  /// **'Laissez vide pour une salle ordinaire.'**
  String get aideTypeSalle;

  /// No description provided for @typeSalle.
  ///
  /// In fr, this message translates to:
  /// **'Type'**
  String get typeSalle;

  /// No description provided for @capacite.
  ///
  /// In fr, this message translates to:
  /// **'Capacité'**
  String get capacite;

  /// No description provided for @places.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 place} other{{n} places}}'**
  String places(int n);

  /// No description provided for @niveau.
  ///
  /// In fr, this message translates to:
  /// **'Niveau'**
  String get niveau;

  /// No description provided for @effectif.
  ///
  /// In fr, this message translates to:
  /// **'Effectif'**
  String get effectif;

  /// No description provided for @eleves.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 élève} other{{n} élèves}}'**
  String eleves(int n);

  /// No description provided for @salleAttitree.
  ///
  /// In fr, this message translates to:
  /// **'Salle attitrée'**
  String get salleAttitree;

  /// No description provided for @aideSalleAttitree.
  ///
  /// In fr, this message translates to:
  /// **'Là où la division passe ses heures ordinaires.'**
  String get aideSalleAttitree;

  /// No description provided for @heuresParSemaine.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 h/semaine} other{{n} h/semaine}}'**
  String heuresParSemaine(int n);

  /// No description provided for @heuresParJour.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 h/jour} other{{n} h/jour}}'**
  String heuresParJour(int n);

  /// No description provided for @heuresParSemaineLibelle.
  ///
  /// In fr, this message translates to:
  /// **'Heures par semaine'**
  String get heuresParSemaineLibelle;

  /// No description provided for @blocsDeuxHeures.
  ///
  /// In fr, this message translates to:
  /// **'Blocs de 2 h'**
  String get blocsDeuxHeures;

  /// No description provided for @blocsDeDeuxHeures.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 bloc de 2 h} other{{n} blocs de 2 h}}'**
  String blocsDeDeuxHeures(int n);

  /// No description provided for @aideBlocs.
  ///
  /// In fr, this message translates to:
  /// **'Séances doubles à réserver dans ce volume.'**
  String get aideBlocs;

  /// No description provided for @maxParJour.
  ///
  /// In fr, this message translates to:
  /// **'Max par jour'**
  String get maxParJour;

  /// No description provided for @fouj.
  ///
  /// In fr, this message translates to:
  /// **'Fouj (couplage)'**
  String get fouj;

  /// No description provided for @aideFouj.
  ///
  /// In fr, this message translates to:
  /// **'Même libellé sur les deux lignes d\'un dédoublement.'**
  String get aideFouj;

  /// No description provided for @demiGroupe.
  ///
  /// In fr, this message translates to:
  /// **'Demi-groupe'**
  String get demiGroupe;

  /// No description provided for @division.
  ///
  /// In fr, this message translates to:
  /// **'Division'**
  String get division;

  /// No description provided for @matiere.
  ///
  /// In fr, this message translates to:
  /// **'Matière'**
  String get matiere;

  /// No description provided for @enseignant.
  ///
  /// In fr, this message translates to:
  /// **'Enseignant'**
  String get enseignant;

  /// No description provided for @parDivision.
  ///
  /// In fr, this message translates to:
  /// **'Par division'**
  String get parDivision;

  /// No description provided for @parEnseignant.
  ///
  /// In fr, this message translates to:
  /// **'Par enseignant'**
  String get parEnseignant;

  /// No description provided for @parSalle.
  ///
  /// In fr, this message translates to:
  /// **'Par salle'**
  String get parSalle;

  /// No description provided for @aucunEmploiDuTemps.
  ///
  /// In fr, this message translates to:
  /// **'Aucun emploi du temps'**
  String get aucunEmploiDuTemps;

  /// No description provided for @aideAucunEmploiDuTemps.
  ///
  /// In fr, this message translates to:
  /// **'Créez-en un, puis lancez une génération.'**
  String get aideAucunEmploiDuTemps;

  /// No description provided for @aucuneLecon.
  ///
  /// In fr, this message translates to:
  /// **'Cet emploi du temps est vide'**
  String get aucuneLecon;

  /// No description provided for @aideAucuneLecon.
  ///
  /// In fr, this message translates to:
  /// **'Lancez une génération pour obtenir une proposition.'**
  String get aideAucuneLecon;

  /// No description provided for @motifSeanceFermee.
  ///
  /// In fr, this message translates to:
  /// **'Séance fermée dans la grille horaire'**
  String get motifSeanceFermee;

  /// No description provided for @motifProfesseurOccupe.
  ///
  /// In fr, this message translates to:
  /// **'L\'enseignant a déjà cours à cette heure'**
  String get motifProfesseurOccupe;

  /// No description provided for @motifProfesseurIndisponible.
  ///
  /// In fr, this message translates to:
  /// **'L\'enseignant est indisponible à cette heure'**
  String get motifProfesseurIndisponible;

  /// No description provided for @motifDivisionOccupee.
  ///
  /// In fr, this message translates to:
  /// **'La division a déjà cours à cette heure'**
  String get motifDivisionOccupee;

  /// No description provided for @motifAucuneSalle.
  ///
  /// In fr, this message translates to:
  /// **'Aucune salle du bon type n\'est libre'**
  String get motifAucuneSalle;

  /// No description provided for @motifFenetre.
  ///
  /// In fr, this message translates to:
  /// **'Cette matière est interdite sur cette plage'**
  String get motifFenetre;

  /// No description provided for @motifPlafondProfesseur.
  ///
  /// In fr, this message translates to:
  /// **'L\'enseignant atteindrait son plafond du jour'**
  String get motifPlafondProfesseur;

  /// No description provided for @motifPlafondDivision.
  ///
  /// In fr, this message translates to:
  /// **'La division atteindrait son plafond du jour'**
  String get motifPlafondDivision;

  /// No description provided for @motifPlafondMatiere.
  ///
  /// In fr, this message translates to:
  /// **'Cette matière atteindrait son plafond du jour'**
  String get motifPlafondMatiere;

  /// No description provided for @motifConsecutives.
  ///
  /// In fr, this message translates to:
  /// **'L\'enseignant dépasserait ses heures consécutives'**
  String get motifConsecutives;

  /// No description provided for @genererTitre.
  ///
  /// In fr, this message translates to:
  /// **'Générer l\'emploi du temps'**
  String get genererTitre;

  /// No description provided for @genererAide.
  ///
  /// In fr, this message translates to:
  /// **'Le solveur propose une grille complète. Vous pourrez ensuite la retoucher à la main.'**
  String get genererAide;

  /// No description provided for @tempsDeCalcul.
  ///
  /// In fr, this message translates to:
  /// **'Temps de calcul'**
  String get tempsDeCalcul;

  /// No description provided for @aideTempsDeCalcul.
  ///
  /// In fr, this message translates to:
  /// **'Plus long ne veut pas dire beaucoup mieux : l\'essentiel se joue dans les premières minutes.'**
  String get aideTempsDeCalcul;

  /// No description provided for @minutes.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 minute} other{{n} minutes}}'**
  String minutes(int n);

  /// No description provided for @lancer.
  ///
  /// In fr, this message translates to:
  /// **'Lancer'**
  String get lancer;

  /// No description provided for @interrompre.
  ///
  /// In fr, this message translates to:
  /// **'Interrompre'**
  String get interrompre;

  /// No description provided for @laisserTourner.
  ///
  /// In fr, this message translates to:
  /// **'Laisser tourner'**
  String get laisserTourner;

  /// No description provided for @secondesEcoulees.
  ///
  /// In fr, this message translates to:
  /// **'{ecoule} s sur {limite} s'**
  String secondesEcoulees(int ecoule, int limite);

  /// No description provided for @solutionsTrouvees.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 solution} other{{n} solutions}}'**
  String solutionsTrouvees(int n);

  /// No description provided for @coutCourant.
  ///
  /// In fr, this message translates to:
  /// **'Coût {valeur}'**
  String coutCourant(String valeur);

  /// No description provided for @leconsPlacees.
  ///
  /// In fr, this message translates to:
  /// **'{n, plural, =1{1 leçon placée} other{{n} leçons placées}}'**
  String leconsPlacees(int n);

  /// No description provided for @qualiteObtenue.
  ///
  /// In fr, this message translates to:
  /// **'Qualité obtenue'**
  String get qualiteObtenue;

  /// No description provided for @trousEleves.
  ///
  /// In fr, this message translates to:
  /// **'Trous élèves : {n}'**
  String trousEleves(String n);

  /// No description provided for @trousProfesseurs.
  ///
  /// In fr, this message translates to:
  /// **'Trous professeurs : {n}'**
  String trousProfesseurs(String n);

  /// No description provided for @generer.
  ///
  /// In fr, this message translates to:
  /// **'Générer'**
  String get generer;

  /// No description provided for @heuresPlacees.
  ///
  /// In fr, this message translates to:
  /// **'heures placées'**
  String get heuresPlacees;

  /// No description provided for @trousElevesCourt.
  ///
  /// In fr, this message translates to:
  /// **'trous élèves'**
  String get trousElevesCourt;

  /// No description provided for @trousProfesseursCourt.
  ///
  /// In fr, this message translates to:
  /// **'trous professeurs'**
  String get trousProfesseursCourt;

  /// No description provided for @demiJourneesIsolees.
  ///
  /// In fr, this message translates to:
  /// **'demi-journées à 1 h'**
  String get demiJourneesIsolees;

  /// No description provided for @journeesSixHeures.
  ///
  /// In fr, this message translates to:
  /// **'journées à 6 h ou plus'**
  String get journeesSixHeures;

  /// No description provided for @matieresTroisHeures.
  ///
  /// In fr, this message translates to:
  /// **'matières à 3 h le même jour'**
  String get matieresTroisHeures;

  /// No description provided for @occupationSeances.
  ///
  /// In fr, this message translates to:
  /// **'Occupation des séances'**
  String get occupationSeances;

  /// No description provided for @serviceDesProfesseurs.
  ///
  /// In fr, this message translates to:
  /// **'Service des professeurs'**
  String get serviceDesProfesseurs;

  /// No description provided for @chargeDesDivisions.
  ///
  /// In fr, this message translates to:
  /// **'Charge des divisions'**
  String get chargeDesDivisions;

  /// No description provided for @heures.
  ///
  /// In fr, this message translates to:
  /// **'Heures'**
  String get heures;

  /// No description provided for @jours.
  ///
  /// In fr, this message translates to:
  /// **'Jours'**
  String get jours;

  /// No description provided for @trous.
  ///
  /// In fr, this message translates to:
  /// **'Trous'**
  String get trous;

  /// No description provided for @maxJour.
  ///
  /// In fr, this message translates to:
  /// **'Max/jour'**
  String get maxJour;

  /// No description provided for @journeeLaPlusChargee.
  ///
  /// In fr, this message translates to:
  /// **'Journée la plus chargée'**
  String get journeeLaPlusChargee;

  /// No description provided for @ongletGrille.
  ///
  /// In fr, this message translates to:
  /// **'Grille horaire'**
  String get ongletGrille;

  /// No description provided for @ongletCriteres.
  ///
  /// In fr, this message translates to:
  /// **'Critères'**
  String get ongletCriteres;

  /// No description provided for @ongletFenetres.
  ///
  /// In fr, this message translates to:
  /// **'Fenêtres'**
  String get ongletFenetres;

  /// No description provided for @reglagesEnregistres.
  ///
  /// In fr, this message translates to:
  /// **'Réglages enregistrés.'**
  String get reglagesEnregistres;

  /// No description provided for @fermeturesTitre.
  ///
  /// In fr, this message translates to:
  /// **'Séances ouvertes'**
  String get fermeturesTitre;

  /// No description provided for @fermeturesAide.
  ///
  /// In fr, this message translates to:
  /// **'Décochez une case pour fermer la séance ce jour-là. Le mardi après-midi, par exemple.'**
  String get fermeturesAide;

  /// No description provided for @horairesTitre.
  ///
  /// In fr, this message translates to:
  /// **'Horaires des séances'**
  String get horairesTitre;

  /// No description provided for @debut.
  ///
  /// In fr, this message translates to:
  /// **'Début'**
  String get debut;

  /// No description provided for @fin.
  ///
  /// In fr, this message translates to:
  /// **'Fin'**
  String get fin;

  /// No description provided for @tempsDeCalculDefaut.
  ///
  /// In fr, this message translates to:
  /// **'Temps de calcul par défaut (s)'**
  String get tempsDeCalculDefaut;

  /// No description provided for @aideTempsDefaut.
  ///
  /// In fr, this message translates to:
  /// **'Utilisé quand une génération n\'en précise pas.'**
  String get aideTempsDefaut;

  /// No description provided for @typeSalleOrdinaire.
  ///
  /// In fr, this message translates to:
  /// **'Type de salle ordinaire'**
  String get typeSalleOrdinaire;

  /// No description provided for @aideTypeSalleOrdinaire.
  ///
  /// In fr, this message translates to:
  /// **'Nom du type utilisé pour les cours sans exigence particulière.'**
  String get aideTypeSalleOrdinaire;

  /// No description provided for @criteresAide.
  ///
  /// In fr, this message translates to:
  /// **'Ces poids arbitrent entre des souhaits contradictoires. Zéro désactive un critère ; aucun n\'empêche une génération d\'aboutir.'**
  String get criteresAide;

  /// No description provided for @critereTrousProfesseurs.
  ///
  /// In fr, this message translates to:
  /// **'Heure creuse d\'un professeur'**
  String get critereTrousProfesseurs;

  /// No description provided for @aideTrousProfesseurs.
  ///
  /// In fr, this message translates to:
  /// **'Une heure sans cours au milieu de sa demi-journée.'**
  String get aideTrousProfesseurs;

  /// No description provided for @critereVideDeuxHeures.
  ///
  /// In fr, this message translates to:
  /// **'Vide de deux heures'**
  String get critereVideDeuxHeures;

  /// No description provided for @aideVideDeuxHeures.
  ///
  /// In fr, this message translates to:
  /// **'Deux heures creuses d\'affilée : bien pire qu\'une seule.'**
  String get aideVideDeuxHeures;

  /// No description provided for @critereJourneeHachee.
  ///
  /// In fr, this message translates to:
  /// **'Journée hachée'**
  String get critereJourneeHachee;

  /// No description provided for @aideJourneeHachee.
  ///
  /// In fr, this message translates to:
  /// **'Plus d\'une heure creuse dans la même journée, pause déjeuner comprise dans l\'amplitude.'**
  String get aideJourneeHachee;

  /// No description provided for @critereHeureIsolee.
  ///
  /// In fr, this message translates to:
  /// **'Déplacement pour une seule heure'**
  String get critereHeureIsolee;

  /// No description provided for @aideHeureIsolee.
  ///
  /// In fr, this message translates to:
  /// **'Le professeur ne vient qu\'une heure sur la demi-journée.'**
  String get aideHeureIsolee;

  /// No description provided for @critereJourPresence.
  ///
  /// In fr, this message translates to:
  /// **'Jour de présence'**
  String get critereJourPresence;

  /// No description provided for @aideJourPresence.
  ///
  /// In fr, this message translates to:
  /// **'Chaque jour en moins est un jour libéré.'**
  String get aideJourPresence;

  /// No description provided for @criterePermanence.
  ///
  /// In fr, this message translates to:
  /// **'Permanence (récompense)'**
  String get criterePermanence;

  /// No description provided for @aidePermanenceCritere.
  ///
  /// In fr, this message translates to:
  /// **'Bonus quand une heure creuse est comblée par de l\'accueil.'**
  String get aidePermanenceCritere;

  /// No description provided for @critereBlocsHorsPolitique.
  ///
  /// In fr, this message translates to:
  /// **'Bloc hors politique du programme'**
  String get critereBlocsHorsPolitique;

  /// No description provided for @aideBlocsHorsPolitique.
  ///
  /// In fr, this message translates to:
  /// **'Le programme dit comment répartir une matière entre les journées : un bloc de 2 h autorise une seule journée doublée.'**
  String get aideBlocsHorsPolitique;

  /// No description provided for @critereMatieresRepetees.
  ///
  /// In fr, this message translates to:
  /// **'Matières doublées empilées'**
  String get critereMatieresRepetees;

  /// No description provided for @aideMatieresRepetees.
  ///
  /// In fr, this message translates to:
  /// **'Plusieurs matières à 2 h ou plus le même jour pour une division.'**
  String get aideMatieresRepetees;

  /// No description provided for @critereEquiteFins.
  ///
  /// In fr, this message translates to:
  /// **'Équité des fins tardives'**
  String get critereEquiteFins;

  /// No description provided for @aideEquiteFins.
  ///
  /// In fr, this message translates to:
  /// **'Répartit les dernières séances entre les divisions.'**
  String get aideEquiteFins;

  /// No description provided for @critereEquilibreJournees.
  ///
  /// In fr, this message translates to:
  /// **'Équilibre des journées'**
  String get critereEquilibreJournees;

  /// No description provided for @aideEquilibreJournees.
  ///
  /// In fr, this message translates to:
  /// **'Évite d\'alterner journées très chargées et très légères.'**
  String get aideEquilibreJournees;

  /// No description provided for @critereDemiJournees.
  ///
  /// In fr, this message translates to:
  /// **'Demi-journée travaillée'**
  String get critereDemiJournees;

  /// No description provided for @aideDemiJournees.
  ///
  /// In fr, this message translates to:
  /// **'Regroupe les cours sur moins de demi-journées.'**
  String get aideDemiJournees;

  /// No description provided for @critereMatieresLourdes.
  ///
  /// In fr, this message translates to:
  /// **'Matière lourde l\'après-midi'**
  String get critereMatieresLourdes;

  /// No description provided for @aideMatieresLourdes.
  ///
  /// In fr, this message translates to:
  /// **'Pousse les matières à fort coefficient vers le matin.'**
  String get aideMatieresLourdes;

  /// No description provided for @seuilsSeanceTitre.
  ///
  /// In fr, this message translates to:
  /// **'Heure de sortie des élèves'**
  String get seuilsSeanceTitre;

  /// No description provided for @seuilsSeanceAide.
  ///
  /// In fr, this message translates to:
  /// **'Coût d\'occupation de chaque séance. Laissez à zéro celles que vous jugez idéales.'**
  String get seuilsSeanceAide;

  /// No description provided for @seuilsChargeTitre.
  ///
  /// In fr, this message translates to:
  /// **'Charge quotidienne des professeurs'**
  String get seuilsChargeTitre;

  /// No description provided for @seuilsChargeAide.
  ///
  /// In fr, this message translates to:
  /// **'Coût d\'atteindre ce nombre d\'heures dans la journée. Les seuils se cumulent.'**
  String get seuilsChargeAide;

  /// No description provided for @fenetresAide.
  ///
  /// In fr, this message translates to:
  /// **'Une fenêtre interdit une matière sur une plage dans tout l\'établissement — journée d\'inspection, réunion de coordination.'**
  String get fenetresAide;

  /// No description provided for @aucuneFenetre.
  ///
  /// In fr, this message translates to:
  /// **'Aucune fenêtre déclarée.'**
  String get aucuneFenetre;

  /// No description provided for @fenetreDetail.
  ///
  /// In fr, this message translates to:
  /// **'Jour {jour} · séances {seances}'**
  String fenetreDetail(String jour, String seances);

  /// No description provided for @ajouterFenetre.
  ///
  /// In fr, this message translates to:
  /// **'Déclarer une fenêtre'**
  String get ajouterFenetre;

  /// No description provided for @jour.
  ///
  /// In fr, this message translates to:
  /// **'Jour'**
  String get jour;

  /// No description provided for @seancesBloquees.
  ///
  /// In fr, this message translates to:
  /// **'Séances bloquées'**
  String get seancesBloquees;

  /// No description provided for @libelle.
  ///
  /// In fr, this message translates to:
  /// **'Libellé'**
  String get libelle;

  /// No description provided for @aideLibelleFenetre.
  ///
  /// In fr, this message translates to:
  /// **'Facultatif : « inspection arabe », « réunion de coordination ».'**
  String get aideLibelleFenetre;

  /// No description provided for @declarezDabordUneMatiere.
  ///
  /// In fr, this message translates to:
  /// **'Déclarez d\'abord une matière.'**
  String get declarezDabordUneMatiere;

  /// No description provided for @adresseDejaUtilisee.
  ///
  /// In fr, this message translates to:
  /// **'Cette adresse est déjà associée à un compte. Connectez-vous, ou utilisez-en une autre.'**
  String get adresseDejaUtilisee;
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
