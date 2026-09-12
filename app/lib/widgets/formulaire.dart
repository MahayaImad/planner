import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../core/theme.dart';
import '../l10n/traductions.dart';

/// Nature d'un champ de saisie.
enum TypeChamp { texte, entier, decimal, choix, multiChoix, booleen }

/// Description d'un champ. Les écrans déclarent leurs champs ; le
/// dialogue s'occupe de les afficher, de les valider et de les
/// convertir — écrire cinq formulaires à la main les aurait fait
/// diverger au premier ajout de colonne.
@immutable
class Champ {
  const Champ({
    required this.cle,
    required this.libelle,
    this.type = TypeChamp.texte,
    this.obligatoire = false,
    this.aide,
    this.options = const [],
    this.defaut,
    this.minimum,
    this.maximum,
  });

  final String cle;
  final String libelle;
  final TypeChamp type;
  final bool obligatoire;
  final String? aide;

  /// Pour `choix` et `multiChoix` : les valeurs proposées.
  final List<({Object valeur, String libelle})> options;

  final Object? defaut;
  final num? minimum;
  final num? maximum;
}

/// Dialogue de création ou de modification.
///
/// Retourne les valeurs saisies, ou null si l'utilisateur annule.
Future<Map<String, dynamic>?> ouvrirFormulaire({
  required BuildContext contexte,
  required String titre,
  required List<Champ> champs,
  Map<String, dynamic>? valeurs,
}) {
  return showDialog<Map<String, dynamic>>(
    context: contexte,
    builder: (_) => _Dialogue(titre: titre, champs: champs, valeurs: valeurs),
  );
}

class _Dialogue extends StatefulWidget {
  const _Dialogue({
    required this.titre,
    required this.champs,
    this.valeurs,
  });

  final String titre;
  final List<Champ> champs;
  final Map<String, dynamic>? valeurs;

  @override
  State<_Dialogue> createState() => _DialogueState();
}

class _DialogueState extends State<_Dialogue> {
  final _formulaire = GlobalKey<FormState>();
  late final Map<String, dynamic> _valeurs;
  final Map<String, TextEditingController> _controleurs = {};

  @override
  void initState() {
    super.initState();
    _valeurs = {
      for (final champ in widget.champs)
        champ.cle: widget.valeurs?[champ.cle] ?? champ.defaut,
    };
    for (final champ in widget.champs) {
      if (champ.type == TypeChamp.texte ||
          champ.type == TypeChamp.entier ||
          champ.type == TypeChamp.decimal) {
        _controleurs[champ.cle] = TextEditingController(
          text: _valeurs[champ.cle] == null ? '' : '${_valeurs[champ.cle]}',
        );
      }
    }
  }

  @override
  void dispose() {
    for (final controleur in _controleurs.values) {
      controleur.dispose();
    }
    super.dispose();
  }

  void _valider() {
    if (!_formulaire.currentState!.validate()) return;
    final resultat = <String, dynamic>{};
    for (final champ in widget.champs) {
      switch (champ.type) {
        case TypeChamp.texte:
          final texte = _controleurs[champ.cle]!.text.trim();
          resultat[champ.cle] = texte.isEmpty ? null : texte;
        case TypeChamp.entier:
          final texte = _controleurs[champ.cle]!.text.trim();
          resultat[champ.cle] = texte.isEmpty ? null : int.tryParse(texte);
        case TypeChamp.decimal:
          final texte = _controleurs[champ.cle]!.text.trim().replaceAll(',', '.');
          resultat[champ.cle] = texte.isEmpty ? null : double.tryParse(texte);
        case TypeChamp.choix:
        case TypeChamp.booleen:
        case TypeChamp.multiChoix:
          resultat[champ.cle] = _valeurs[champ.cle];
      }
    }
    Navigator.of(context).pop(resultat);
  }

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    return AlertDialog(
      title: Text(widget.titre),
      // Un dialogue qui déborde de l'écran sur un téléphone est
      // inutilisable : la largeur suit celle disponible.
      content: SizedBox(
        width: 460,
        child: SingleChildScrollView(
          child: Form(
            key: _formulaire,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                for (final champ in widget.champs) ...[
                  _construireChamp(champ),
                  const SizedBox(height: Jetons.m),
                ],
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(contexte).pop(),
          child: Text(l.annuler),
        ),
        FilledButton(onPressed: _valider, child: Text(l.enregistrer)),
      ],
    );
  }

  Widget _construireChamp(Champ champ) {
    final l = context.l10n;

    String? obligatoire(String? valeur) =>
        champ.obligatoire && (valeur == null || valeur.trim().isEmpty)
            ? l.champObligatoire
            : null;

    switch (champ.type) {
      case TypeChamp.texte:
        return TextFormField(
          controller: _controleurs[champ.cle],
          decoration: InputDecoration(
              labelText: champ.libelle, helperText: champ.aide),
          validator: obligatoire,
        );

      case TypeChamp.entier:
      case TypeChamp.decimal:
        return TextFormField(
          controller: _controleurs[champ.cle],
          decoration: InputDecoration(
              labelText: champ.libelle, helperText: champ.aide),
          keyboardType: TextInputType.numberWithOptions(
              decimal: champ.type == TypeChamp.decimal),
          inputFormatters: [
            FilteringTextInputFormatter.allow(
                champ.type == TypeChamp.decimal
                    ? RegExp(r'[0-9.,]')
                    : RegExp(r'[0-9]')),
          ],
          validator: (valeur) {
            final vide = obligatoire(valeur);
            if (vide != null) return vide;
            if (valeur == null || valeur.trim().isEmpty) return null;
            final nombre = num.tryParse(valeur.trim().replaceAll(',', '.'));
            if (nombre == null) return l.nombreAttendu;
            if (champ.minimum != null && nombre < champ.minimum!) {
              return l.horsBornes(
                  '${champ.minimum}', '${champ.maximum ?? ''}');
            }
            if (champ.maximum != null && nombre > champ.maximum!) {
              return l.horsBornes(
                  '${champ.minimum ?? ''}', '${champ.maximum}');
            }
            return null;
          },
        );

      case TypeChamp.choix:
        return DropdownButtonFormField<Object?>(
          initialValue: _valeurs[champ.cle],
          decoration: InputDecoration(
              labelText: champ.libelle, helperText: champ.aide),
          items: [
            if (!champ.obligatoire)
              DropdownMenuItem<Object?>(value: null, child: Text(l.aucun)),
            for (final option in champ.options)
              DropdownMenuItem<Object?>(
                  value: option.valeur, child: Text(option.libelle)),
          ],
          onChanged: (valeur) => setState(() => _valeurs[champ.cle] = valeur),
          validator: (valeur) => champ.obligatoire && valeur == null
              ? l.champObligatoire
              : null,
        );

      case TypeChamp.booleen:
        return SwitchListTile(
          value: _valeurs[champ.cle] == true,
          onChanged: (valeur) => setState(() => _valeurs[champ.cle] = valeur),
          title: Text(champ.libelle),
          subtitle: champ.aide == null ? null : Text(champ.aide!),
          contentPadding: EdgeInsets.zero,
        );

      case TypeChamp.multiChoix:
        final choisis = (_valeurs[champ.cle] as List?)?.toList() ?? [];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(champ.libelle,
                style: Theme.of(context).textTheme.labelLarge),
            if (champ.aide != null)
              Text(champ.aide!,
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(color: Jetons.encreAttenuee)),
            const SizedBox(height: Jetons.s),
            Wrap(
              spacing: Jetons.s,
              runSpacing: Jetons.s,
              children: [
                for (final option in champ.options)
                  FilterChip(
                    label: Text(option.libelle),
                    selected: choisis.contains(option.valeur),
                    onSelected: (actif) => setState(() {
                      final liste = List<Object>.from(choisis);
                      actif
                          ? liste.add(option.valeur)
                          : liste.remove(option.valeur);
                      _valeurs[champ.cle] = liste;
                    }),
                  ),
              ],
            ),
          ],
        );
    }
  }
}
