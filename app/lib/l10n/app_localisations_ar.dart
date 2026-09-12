// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localisations.dart';

// ignore_for_file: type=lint

/// The translations for Arabic (`ar`).
class LAr extends L {
  LAr([String locale = 'ar']) : super(locale);

  @override
  String get appNom => 'بلانر';

  @override
  String get appSousTitre => 'جداول التوقيت لمتوسطات وثانويات الجزائر';

  @override
  String get langue => 'اللغة';

  @override
  String get francais => 'Français';

  @override
  String get arabe => 'العربية';

  @override
  String get connexion => 'تسجيل الدخول';

  @override
  String get connexionTitre => 'سجّل دخولك';

  @override
  String get connexionSousTitre => 'ادخل إلى فضاء مؤسستك.';

  @override
  String get email => 'البريد الإلكتروني';

  @override
  String get motDePasse => 'كلمة المرور';

  @override
  String get seConnecter => 'تسجيل الدخول';

  @override
  String get creerUnCompte => 'إنشاء مؤسسة';

  @override
  String get inscriptionTitre => 'إنشاء مؤسسة';

  @override
  String get inscriptionSousTitre => 'معلومات قليلة تكفي للانطلاق.';

  @override
  String get nomEtablissement => 'اسم المؤسسة';

  @override
  String get emailEtablissement => 'البريد الإلكتروني للمؤسسة';

  @override
  String get nom => 'اللقب';

  @override
  String get prenom => 'الاسم';

  @override
  String get sInscrire => 'إنشاء المؤسسة';

  @override
  String get dejaUnCompte => 'لديك حساب بالفعل؟';

  @override
  String get seDeconnecter => 'تسجيل الخروج';

  @override
  String get champObligatoire => 'هذا الحقل إجباري';

  @override
  String get emailInvalide => 'بريد إلكتروني غير صالح';

  @override
  String get motDePasseCourt => '12 حرفًا على الأقل';

  @override
  String get identifiantsInvalides =>
      'البريد الإلكتروني أو كلمة المرور غير صحيحة';

  @override
  String get erreurReseau => 'تعذّر الوصول إلى الخادم. تحقّق من اتصالك.';

  @override
  String get tableauDeBord => 'لوحة القيادة';

  @override
  String get enseignants => 'الأساتذة';

  @override
  String get matieres => 'المواد';

  @override
  String get salles => 'القاعات';

  @override
  String get divisions => 'الأفواج';

  @override
  String get programme => 'البرنامج';

  @override
  String get emploisDuTemps => 'جداول التوقيت';

  @override
  String get statistiques => 'الإحصائيات';

  @override
  String get reglages => 'الإعدادات';

  @override
  String get donnees => 'البيانات';

  @override
  String get chargement => 'جارٍ التحميل…';

  @override
  String get reessayer => 'إعادة المحاولة';

  @override
  String get aucuneDonnee => 'لا توجد بيانات بعد';

  @override
  String get enregistrer => 'حفظ';

  @override
  String get annuler => 'إلغاء';

  @override
  String get supprimer => 'حذف';

  @override
  String get modifier => 'تعديل';

  @override
  String get ajouter => 'إضافة';

  @override
  String get rechercher => 'بحث';

  @override
  String get fermer => 'إغلاق';

  @override
  String get resumeEtablissement => 'مؤسستك';

  @override
  String nbEnseignants(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n أستاذ',
      many: '$n أستاذًا',
      few: '$n أساتذة',
      two: 'أستاذان',
      one: 'أستاذ واحد',
      zero: 'لا يوجد أستاذ',
    );
    return '$_temp0';
  }

  @override
  String nbDivisions(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n فوج',
      many: '$n فوجًا',
      few: '$n أفواج',
      two: 'فوجان',
      one: 'فوج واحد',
      zero: 'لا يوجد فوج',
    );
    return '$_temp0';
  }

  @override
  String nbMatieres(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n مادة',
      many: '$n مادة',
      few: '$n مواد',
      two: 'مادتان',
      one: 'مادة واحدة',
      zero: 'لا توجد مادة',
    );
    return '$_temp0';
  }

  @override
  String nbSalles(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n قاعة',
      many: '$n قاعة',
      few: '$n قاعات',
      two: 'قاعتان',
      one: 'قاعة واحدة',
      zero: 'لا توجد قاعة',
    );
    return '$_temp0';
  }

  @override
  String nbLignesProgramme(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n سطر',
      many: '$n سطرًا',
      few: '$n أسطر',
      two: 'سطران',
      one: 'سطر واحد',
      zero: 'البرنامج فارغ',
    );
    return '$_temp0';
  }

  @override
  String get commencerIci => 'من أين تبدأ';

  @override
  String get etapeDonnees => 'حمّل بياناتك';

  @override
  String get etapeDonneesAide => 'نزّل ملف Excel، املأه، ثم ارفعه.';

  @override
  String get etapeProgramme => 'تحقّق من البرنامج';

  @override
  String get etapeProgrammeAide => 'من يدرّس ماذا، لأي فوج، وكم ساعة.';

  @override
  String get etapeGenerer => 'أنشئ جدول التوقيت';

  @override
  String get etapeGenererAide => 'ثم عدّل يدويًا ما يحتاج إلى تعديل.';

  @override
  String get classeurTitre => 'ملف Excel';

  @override
  String get classeurAide => 'املأ جدولًا بدل عشرات الشاشات.';

  @override
  String get telechargerModele => 'تنزيل النموذج';

  @override
  String get exporterDonnees => 'تصدير بياناتي';

  @override
  String get importerClasseur => 'رفع ملف';

  @override
  String get verifierSansEcrire => 'التحقّق دون الحفظ';

  @override
  String importReussi(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: 'تم استيراد $n سطر',
      many: 'تم استيراد $n سطرًا',
      few: 'تم استيراد $n أسطر',
      two: 'تم استيراد سطرين',
      one: 'تم استيراد سطر واحد',
    );
    return '$_temp0';
  }

  @override
  String get importRefuse => 'تم رفض الاستيراد: لم يُكتب أي شيء.';

  @override
  String get plus => 'المزيد';

  @override
  String get ecranAVenir => 'هذه الشاشة قيد الإنجاز.';

  @override
  String get fichierEnregistre => 'تم حفظ الملف.';

  @override
  String get importApplique => 'تم تطبيق الاستيراد.';

  @override
  String get importValide => 'الملف صالح. لم يُكتب أي شيء.';

  @override
  String get feuille => 'الورقة';

  @override
  String get creees => 'المُنشأة';

  @override
  String get misesAJour => 'المُحدّثة';

  @override
  String absentsDuFichier(String feuille, String noms) {
    return '$feuille: موجودة في قاعدة البيانات وغير موجودة في الملف — $noms';
  }

  @override
  String get nombreAttendu => 'أدخل رقمًا';

  @override
  String horsBornes(String min, String max) {
    return 'بين $min و $max';
  }

  @override
  String get aucun => 'لا شيء';

  @override
  String confirmerSuppression(String nom) {
    return 'حذف «$nom»؟';
  }

  @override
  String get suppressionEnCascade =>
      'ستُحذف معها الحصص وأسطر البرنامج المرتبطة بها.';

  @override
  String get nouvel => 'جديد';

  @override
  String get modifierTitre => 'تعديل';

  @override
  String get telephone => 'الهاتف';

  @override
  String get heuresConsecutivesMax => 'أقصى ساعات متتالية';

  @override
  String get heuresParJourMax => 'أقصى ساعات في اليوم';

  @override
  String get heuresParSemaineMax => 'أقصى ساعات في الأسبوع';

  @override
  String get assurePermanences => 'يؤمّن حصص الاستقبال';

  @override
  String get aidePermanences => 'يمكنه تأطير ساعة استقبال لسدّ فراغ.';

  @override
  String get aidePlafondHebdo => 'اتركه فارغًا إذا لم يكن هناك حدّ أقصى.';

  @override
  String get aideMatieresEnseignant => 'ما يمكن لهذا الأستاذ تدريسه.';

  @override
  String get aideEnseignantsVide =>
      'أضف أساتذتك، أو حمّلهم دفعة واحدة عبر ملف Excel.';

  @override
  String get aideMatieresVide => 'المواد المدرّسة في المؤسسة.';

  @override
  String get aideSallesVide => 'قاعات الدراسة والمخابر والملعب.';

  @override
  String get aideDivisionsVide => 'أفواج المؤسسة: 1م1، 4م أ…';

  @override
  String get aideProgrammeVide => 'من يدرّس ماذا، لأي فوج، وكم ساعة.';

  @override
  String get coefficient => 'المعامل';

  @override
  String coefficientValeur(String valeur) {
    return 'المعامل $valeur';
  }

  @override
  String get typeSalleRequis => 'نوع القاعة المطلوب';

  @override
  String get aideTypeSalle => 'اتركه فارغًا لقاعة عادية.';

  @override
  String get typeSalle => 'النوع';

  @override
  String get capacite => 'السعة';

  @override
  String places(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n مقعد',
      many: '$n مقعدًا',
      few: '$n مقاعد',
      two: 'مقعدان',
      one: 'مقعد واحد',
    );
    return '$_temp0';
  }

  @override
  String get niveau => 'المستوى';

  @override
  String get effectif => 'عدد التلاميذ';

  @override
  String eleves(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n تلميذ',
      many: '$n تلميذًا',
      few: '$n تلاميذ',
      two: 'تلميذان',
      one: 'تلميذ واحد',
    );
    return '$_temp0';
  }

  @override
  String get salleAttitree => 'القاعة المخصّصة';

  @override
  String get aideSalleAttitree => 'حيث يقضي الفوج ساعاته العادية.';

  @override
  String heuresParSemaine(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n ساعة/أسبوع',
      many: '$n ساعة/أسبوع',
      few: '$n ساعات/أسبوع',
      two: 'ساعتان/أسبوع',
      one: 'ساعة/أسبوع',
    );
    return '$_temp0';
  }

  @override
  String heuresParJour(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n ساعة/يوم',
      many: '$n ساعة/يوم',
      few: '$n ساعات/يوم',
      two: 'ساعتان/يوم',
      one: 'ساعة/يوم',
    );
    return '$_temp0';
  }

  @override
  String get heuresParSemaineLibelle => 'ساعات في الأسبوع';

  @override
  String get blocsDeuxHeures => 'حصص مزدوجة';

  @override
  String blocsDeDeuxHeures(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n حصة مزدوجة',
      many: '$n حصة مزدوجة',
      few: '$n حصص مزدوجة',
      two: 'حصتان مزدوجتان',
      one: 'حصة مزدوجة واحدة',
    );
    return '$_temp0';
  }

  @override
  String get aideBlocs => 'الحصص المزدوجة المطلوب حجزها ضمن هذا الحجم.';

  @override
  String get maxParJour => 'الحدّ الأقصى في اليوم';

  @override
  String get fouj => 'الفوج (الازدواج)';

  @override
  String get aideFouj => 'نفس التسمية على سطري الازدواج.';

  @override
  String get demiGroupe => 'نصف الفوج';

  @override
  String get division => 'الفوج';

  @override
  String get matiere => 'المادة';

  @override
  String get enseignant => 'الأستاذ';

  @override
  String get parDivision => 'حسب الفوج';

  @override
  String get parEnseignant => 'حسب الأستاذ';

  @override
  String get parSalle => 'حسب القاعة';

  @override
  String get aucunEmploiDuTemps => 'لا يوجد جدول توقيت';

  @override
  String get aideAucunEmploiDuTemps => 'أنشئ واحدًا ثم ابدأ التوليد.';

  @override
  String get aucuneLecon => 'هذا الجدول فارغ';

  @override
  String get aideAucuneLecon => 'ابدأ التوليد للحصول على اقتراح.';

  @override
  String get motifSeanceFermee => 'الحصة مغلقة في الشبكة الزمنية';

  @override
  String get motifProfesseurOccupe => 'الأستاذ لديه حصة في هذا الوقت';

  @override
  String get motifProfesseurIndisponible => 'الأستاذ غير متاح في هذا الوقت';

  @override
  String get motifDivisionOccupee => 'الفوج لديه حصة في هذا الوقت';

  @override
  String get motifAucuneSalle => 'لا توجد قاعة مناسبة شاغرة';

  @override
  String get motifFenetre => 'هذه المادة ممنوعة في هذه الفترة';

  @override
  String get motifPlafondProfesseur => 'سيبلغ الأستاذ حدّه اليومي';

  @override
  String get motifPlafondDivision => 'سيبلغ الفوج حدّه اليومي';

  @override
  String get motifPlafondMatiere => 'ستبلغ هذه المادة حدّها اليومي';

  @override
  String get motifConsecutives => 'سيتجاوز الأستاذ ساعاته المتتالية';

  @override
  String get genererTitre => 'توليد جدول التوقيت';

  @override
  String get genererAide =>
      'يقترح المحرّك جدولًا كاملًا. يمكنك بعد ذلك تعديله يدويًا.';

  @override
  String get tempsDeCalcul => 'مدة الحساب';

  @override
  String get aideTempsDeCalcul =>
      'المدة الأطول لا تعني نتيجة أفضل بكثير: الأساس يُحسم في الدقائق الأولى.';

  @override
  String minutes(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n دقيقة',
      many: '$n دقيقة',
      few: '$n دقائق',
      two: 'دقيقتان',
      one: 'دقيقة واحدة',
    );
    return '$_temp0';
  }

  @override
  String get lancer => 'ابدأ';

  @override
  String get interrompre => 'إيقاف';

  @override
  String get laisserTourner => 'اتركه يعمل';

  @override
  String secondesEcoulees(int ecoule, int limite) {
    return '$ecoule ث من $limite ث';
  }

  @override
  String solutionsTrouvees(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n حل',
      many: '$n حلًا',
      few: '$n حلول',
      two: 'حلّان',
      one: 'حل واحد',
    );
    return '$_temp0';
  }

  @override
  String coutCourant(String valeur) {
    return 'التكلفة $valeur';
  }

  @override
  String leconsPlacees(int n) {
    String _temp0 = intl.Intl.pluralLogic(
      n,
      locale: localeName,
      other: '$n حصة موضوعة',
      many: '$n حصة موضوعة',
      few: '$n حصص موضوعة',
      two: 'حصتان موضوعتان',
      one: 'حصة واحدة موضوعة',
    );
    return '$_temp0';
  }

  @override
  String get qualiteObtenue => 'الجودة المحصّلة';

  @override
  String trousEleves(String n) {
    return 'فراغات التلاميذ: $n';
  }

  @override
  String trousProfesseurs(String n) {
    return 'فراغات الأساتذة: $n';
  }

  @override
  String get generer => 'توليد';

  @override
  String get heuresPlacees => 'حصص موضوعة';

  @override
  String get trousElevesCourt => 'فراغات التلاميذ';

  @override
  String get trousProfesseursCourt => 'فراغات الأساتذة';

  @override
  String get demiJourneesIsolees => 'أنصاف أيام بساعة واحدة';

  @override
  String get journeesSixHeures => 'أيام بست ساعات أو أكثر';

  @override
  String get matieresTroisHeures => 'مواد بثلاث ساعات في اليوم';

  @override
  String get occupationSeances => 'إشغال الحصص';

  @override
  String get serviceDesProfesseurs => 'خدمة الأساتذة';

  @override
  String get chargeDesDivisions => 'عبء الأفواج';

  @override
  String get heures => 'الساعات';

  @override
  String get jours => 'الأيام';

  @override
  String get trous => 'الفراغات';

  @override
  String get maxJour => 'الأقصى/اليوم';

  @override
  String get journeeLaPlusChargee => 'أثقل يوم';

  @override
  String get ongletGrille => 'الشبكة الزمنية';

  @override
  String get ongletCriteres => 'المعايير';

  @override
  String get ongletFenetres => 'النوافذ';

  @override
  String get reglagesEnregistres => 'تم حفظ الإعدادات.';

  @override
  String get fermeturesTitre => 'الحصص المفتوحة';

  @override
  String get fermeturesAide =>
      'أزل العلامة لإغلاق الحصة في ذلك اليوم — بعد ظهر الثلاثاء مثلًا.';

  @override
  String get horairesTitre => 'توقيت الحصص';

  @override
  String get debut => 'البداية';

  @override
  String get fin => 'النهاية';

  @override
  String get tempsDeCalculDefaut => 'مدة الحساب الافتراضية (ث)';

  @override
  String get aideTempsDefaut => 'تُستعمل عندما لا يحدّدها التوليد.';

  @override
  String get typeSalleOrdinaire => 'نوع القاعة العادية';

  @override
  String get aideTypeSalleOrdinaire =>
      'اسم النوع المستعمل للحصص دون متطلبات خاصة.';

  @override
  String get criteresAide =>
      'توازن هذه الأوزان بين رغبات متعارضة. الصفر يعطّل معيارًا، ولا يمنع أيٌّ منها التوليد من النجاح.';

  @override
  String get critereTrousProfesseurs => 'ساعة فارغة لأستاذ';

  @override
  String get aideTrousProfesseurs => 'ساعة بلا حصة في وسط نصف يومه.';

  @override
  String get critereVideDeuxHeures => 'فراغ من ساعتين';

  @override
  String get aideVideDeuxHeures =>
      'ساعتان فارغتان متتاليتان: أسوأ بكثير من واحدة.';

  @override
  String get critereJourneeHachee => 'يوم مقطّع';

  @override
  String get aideJourneeHachee =>
      'أكثر من ساعة فارغة في اليوم نفسه، بما في ذلك فترة الغداء.';

  @override
  String get critereHeureIsolee => 'تنقّل من أجل ساعة واحدة';

  @override
  String get aideHeureIsolee => 'الأستاذ يحضر ساعة واحدة فقط في نصف اليوم.';

  @override
  String get critereJourPresence => 'يوم حضور';

  @override
  String get aideJourPresence => 'كل يوم أقلّ هو يوم محرّر.';

  @override
  String get criterePermanence => 'حصة استقبال (مكافأة)';

  @override
  String get aidePermanenceCritere =>
      'مكافأة عندما تُملأ ساعة فارغة بحصة استقبال.';

  @override
  String get critereBlocsHorsPolitique => 'حصة مزدوجة خارج سياسة البرنامج';

  @override
  String get aideBlocsHorsPolitique =>
      'يحدّد البرنامج كيفية توزيع المادة على الأيام: حصة مزدوجة تسمح بيوم مضاعف واحد.';

  @override
  String get critereMatieresRepetees => 'تراكم المواد المضاعفة';

  @override
  String get aideMatieresRepetees =>
      'عدة مواد بساعتين أو أكثر في اليوم نفسه لفوج واحد.';

  @override
  String get critereEquiteFins => 'عدالة الخروج المتأخّر';

  @override
  String get aideEquiteFins => 'يوزّع الحصص الأخيرة بين الأفواج.';

  @override
  String get critereEquilibreJournees => 'توازن الأيام';

  @override
  String get aideEquilibreJournees =>
      'يتجنّب التناوب بين أيام مثقلة وأيام خفيفة.';

  @override
  String get critereDemiJournees => 'نصف يوم مشتغل';

  @override
  String get aideDemiJournees => 'يجمع الحصص في أنصاف أيام أقل.';

  @override
  String get critereMatieresLourdes => 'مادة ثقيلة بعد الظهر';

  @override
  String get aideMatieresLourdes =>
      'يدفع المواد ذات المعامل العالي نحو الصباح.';

  @override
  String get seuilsSeanceTitre => 'وقت خروج التلاميذ';

  @override
  String get seuilsSeanceAide =>
      'تكلفة إشغال كل حصة. اترك صفرًا للحصص التي تراها مثالية.';

  @override
  String get seuilsChargeTitre => 'العبء اليومي للأساتذة';

  @override
  String get seuilsChargeAide =>
      'تكلفة بلوغ هذا العدد من الساعات في اليوم. العتبات تتراكم.';

  @override
  String get fenetresAide =>
      'تمنع النافذة مادةً في فترة معيّنة عبر المؤسسة كلها — يوم تفتيش، اجتماع تنسيق.';

  @override
  String get aucuneFenetre => 'لا توجد نافذة مصرّح بها.';

  @override
  String fenetreDetail(String jour, String seances) {
    return 'اليوم $jour · الحصص $seances';
  }

  @override
  String get ajouterFenetre => 'التصريح بنافذة';

  @override
  String get jour => 'اليوم';

  @override
  String get seancesBloquees => 'الحصص الممنوعة';

  @override
  String get libelle => 'التسمية';

  @override
  String get aideLibelleFenetre => 'اختياري: «تفتيش العربية»، «اجتماع تنسيق».';

  @override
  String get declarezDabordUneMatiere => 'صرّح أولًا بمادة.';
}
