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
}
