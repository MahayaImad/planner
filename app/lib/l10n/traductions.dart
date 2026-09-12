library;

// Point d'entrée unique des traductions. La classe générée s'appelle
// `L` (voir l10n.yaml) ; l'extension `contexte.l10n` évite d'écrire
// `L.of(context)` à chaque ligne.
export 'app_localisations.dart' show L;

import 'package:flutter/widgets.dart';

import 'app_localisations.dart';

extension Traductions on BuildContext {
  L get l10n => L.of(this);

  /// Vrai quand la langue s'écrit de droite à gauche. Ne sert qu'aux
  /// rares cas où le sens de lecture change autre chose que la mise en
  /// page — une flèche de retour, un chevron.
  bool get estRtl => Directionality.of(this) == TextDirection.rtl;
}
