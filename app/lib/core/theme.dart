import 'package:flutter/material.dart';

/// Jetons de couleur issus de la direction artistique retenue :
/// minimalisme suisse, indigo sobre, accent orange réservé aux appels à
/// l'action. Aucune couleur brute n'est écrite ailleurs dans l'appli —
/// tout passe par le thème, sans quoi une retouche de charte
/// demanderait de fouiller cinquante fichiers.
abstract final class Jetons {
  static const primaire = Color(0xFF4F46E5);
  static const surPrimaire = Color(0xFFFFFFFF);
  static const secondaire = Color(0xFF818CF8);
  static const accent = Color(0xFFEA580C);
  static const fond = Color(0xFFEEF2FF);
  static const encre = Color(0xFF1E1B4B);
  static const carte = Color(0xFFFFFFFF);
  static const attenue = Color(0xFFEBEEF8);
  static const encreAttenuee = Color(0xFF475569);
  static const bordure = Color(0xFFC7D2FE);
  static const danger = Color(0xFFDC2626);
  static const succes = Color(0xFF15803D);
  static const alerte = Color(0xFFB45309);

  /// Échelle d'espacement dense, adaptée à un outil d'administration
  /// où l'on veut voir beaucoup de lignes sans faire défiler.
  static const double xs = 4;
  static const double s = 8;
  static const double m = 16;
  static const double l = 24;
  static const double xl = 32;

  static const rayon = 12.0;
  static const rayonPetit = 8.0;

  /// Une seule famille couvre le latin ET l'arabe : l'interface garde
  /// exactement la même allure dans les deux langues, et il n'y a
  /// qu'une police à charger.
  static const famille = 'Cairo';
}

/// Ombres discrètes : le style suisse s'appuie sur la grille et le
/// contraste, pas sur le relief.
const _ombreCarte = [
  BoxShadow(color: Color(0x0F1E1B4B), blurRadius: 2, offset: Offset(0, 1)),
  BoxShadow(color: Color(0x0A1E1B4B), blurRadius: 8, offset: Offset(0, 4)),
];

List<BoxShadow> get ombreCarte => _ombreCarte;

ThemeData construireTheme() {
  final schema = ColorScheme.fromSeed(
    seedColor: Jetons.primaire,
    primary: Jetons.primaire,
    onPrimary: Jetons.surPrimaire,
    secondary: Jetons.secondaire,
    onSecondary: Jetons.encre,
    tertiary: Jetons.accent,
    onTertiary: Colors.white,
    error: Jetons.danger,
    onError: Colors.white,
    surface: Jetons.carte,
    onSurface: Jetons.encre,
    outline: Jetons.bordure,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: schema,
    scaffoldBackgroundColor: Jetons.fond,
    fontFamily: Jetons.famille,
    appBarTheme: const AppBarTheme(
      backgroundColor: Jetons.carte,
      foregroundColor: Jetons.encre,
      elevation: 0,
      scrolledUnderElevation: 1,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: Jetons.carte,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(Jetons.rayon),
        side: const BorderSide(color: Jetons.bordure),
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: Jetons.bordure,
      thickness: 1,
      space: 1,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Jetons.carte,
      // Libellé toujours visible : un simple texte d'exemple disparaît
      // dès la première frappe et l'utilisateur ne sait plus ce qu'il
      // remplit.
      floatingLabelBehavior: FloatingLabelBehavior.always,
      contentPadding: const EdgeInsets.symmetric(
          horizontal: Jetons.m, vertical: Jetons.m),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Jetons.rayonPetit),
        borderSide: const BorderSide(color: Jetons.bordure),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Jetons.rayonPetit),
        borderSide: const BorderSide(color: Jetons.bordure),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Jetons.rayonPetit),
        borderSide: const BorderSide(color: Jetons.primaire, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(Jetons.rayonPetit),
        borderSide: const BorderSide(color: Jetons.danger),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        // 48 dp de haut : au-dessus du minimum tactile de 44, pouce
        // compris.
        minimumSize: const Size(64, 48),
        padding: const EdgeInsets.symmetric(horizontal: Jetons.l),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(Jetons.rayonPetit),
        ),
        // styleFrom remplace le style du thème au lieu de le compléter :
        // omettre la famille ici faisait tomber l'arabe sur une police
        // dépourvue de ses glyphes, et le libellé s'affichait en carrés.
        textStyle: const TextStyle(
            fontFamily: Jetons.famille, fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(64, 48),
        padding: const EdgeInsets.symmetric(horizontal: Jetons.l),
        side: const BorderSide(color: Jetons.bordure),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(Jetons.rayonPetit),
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(minimumSize: const Size(48, 44)),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: Jetons.attenue,
      side: const BorderSide(color: Jetons.bordure),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(Jetons.rayonPetit),
      ),
    ),
    navigationRailTheme: const NavigationRailThemeData(
      backgroundColor: Jetons.carte,
      indicatorColor: Jetons.attenue,
      labelType: NavigationRailLabelType.all,
    ),
    navigationBarTheme: const NavigationBarThemeData(
      backgroundColor: Jetons.carte,
      indicatorColor: Jetons.attenue,
      height: 68,
    ),
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(Jetons.rayonPetit),
      ),
    ),
  );
}
