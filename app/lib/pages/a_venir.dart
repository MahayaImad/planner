import 'package:flutter/material.dart';

import '../core/navigation.dart';
import '../l10n/traductions.dart';
import '../widgets/etats.dart';

/// Écran encore à écrire.
///
/// Une page explicite vaut mieux qu'une page blanche : elle dit ce qui
/// manque au lieu de laisser croire à une panne.
class PageAVenir extends StatelessWidget {
  const PageAVenir({super.key, required this.destination});

  final Destination destination;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(destination.libelle(l))),
      body: EtatVide(
        icone: destination.icone,
        titre: destination.libelle(l),
        aide: l.ecranAVenir,
      ),
    );
  }
}
