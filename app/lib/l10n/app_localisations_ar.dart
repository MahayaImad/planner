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
}
