import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api.dart';
import '../core/ressources.dart';
import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';
import 'etats.dart';
import 'formulaire.dart';

/// Ce qu'un écran de saisie doit dire de sa collection.
@immutable
class Definition {
  const Definition({
    required this.ressource,
    required this.titre,
    required this.icone,
    required this.champs,
    required this.libelle,
    required this.sousTitre,
    this.aideVide,
  });

  final Ressource ressource;
  final String titre;
  final IconData icone;

  /// Les champs peuvent dépendre d'autres collections (les matières
  /// d'un enseignant, la salle d'une division) : la fonction les reçoit
  /// au moment d'ouvrir le formulaire.
  final List<Champ> Function(BuildContext, Map<String, List<Map<String, dynamic>>>) champs;

  final String Function(Map<String, dynamic>) libelle;
  final String Function(BuildContext, Map<String, dynamic>) sousTitre;
  final String? aideVide;
}

/// Écran de saisie générique : liste, recherche, création, modification,
/// suppression.
///
/// Les cinq collections partagent cette page ; seuls leurs champs
/// changent. Cinq écrans écrits à la main auraient divergé dès le
/// premier ajout de colonne.
class ListeRessource extends ConsumerStatefulWidget {
  const ListeRessource({
    super.key,
    required this.definition,
    this.dependances = const [],
  });

  final Definition definition;

  /// Collections dont les champs ont besoin (matières, salles…).
  final List<({String cle, Ressource ressource})> dependances;

  @override
  ConsumerState<ListeRessource> createState() => _ListeRessourceState();
}

class _ListeRessourceState extends ConsumerState<ListeRessource> {
  String _recherche = '';
  bool _enCours = false;

  Map<String, List<Map<String, dynamic>>> _dependances() {
    final resultat = <String, List<Map<String, dynamic>>>{};
    for (final dependance in widget.dependances) {
      resultat[dependance.cle] =
          ref.watch(collectionProvider(dependance.ressource)).valueOrNull ??
              const [];
    }
    return resultat;
  }

  Future<void> _agir(Future<void> Function() operation) async {
    setState(() => _enCours = true);
    try {
      await operation();
      ref.invalidate(collectionProvider(widget.definition.ressource));
    } on ErreurApi catch (erreur) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          backgroundColor: Jetons.danger,
          content: Text(erreur.reseau
              ? context.l10n.erreurReseau
              : (erreur.message.isEmpty ? '${erreur.code}' : erreur.message)),
        ));
      }
    } finally {
      if (mounted) setState(() => _enCours = false);
    }
  }

  Future<void> _ouvrir([Map<String, dynamic>? existant]) async {
    final l = context.l10n;
    final valeurs = await ouvrirFormulaire(
      contexte: context,
      titre: existant == null
          ? '${l.nouvel} — ${widget.definition.titre}'
          : '${l.modifierTitre} — ${widget.definition.libelle(existant)}',
      champs: widget.definition.champs(context, _dependances()),
      valeurs: existant,
    );
    if (valeurs == null) return;
    final api = ref.read(apiProvider);
    await _agir(() => existant == null
        ? widget.definition.ressource.creer(api, valeurs)
        : widget.definition.ressource
            .modifier(api, existant['id'] as int, valeurs));
  }

  Future<void> _supprimer(Map<String, dynamic> element) async {
    final l = context.l10n;
    final confirme = await showDialog<bool>(
      context: context,
      builder: (dialogue) => AlertDialog(
        title: Text(l.confirmerSuppression(widget.definition.libelle(element))),
        content: Text(l.suppressionEnCascade),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogue).pop(false),
            child: Text(l.annuler),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Jetons.danger),
            onPressed: () => Navigator.of(dialogue).pop(true),
            child: Text(l.supprimer),
          ),
        ],
      ),
    );
    if (confirme != true) return;
    await _agir(() => widget.definition.ressource
        .supprimer(ref.read(apiProvider), element['id'] as int));
  }

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final definition = widget.definition;
    final collection = ref.watch(collectionProvider(definition.ressource));
    // Les dépendances doivent être chargées avant d'ouvrir un
    // formulaire qui les propose en liste.
    for (final dependance in widget.dependances) {
      ref.watch(collectionProvider(dependance.ressource));
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(definition.titre),
        actions: [
          IconButton(
            tooltip: l.reessayer,
            onPressed: () =>
                ref.invalidate(collectionProvider(definition.ressource)),
            icon: const Icon(Icons.refresh),
          ),
        ],
        bottom: _enCours
            ? const PreferredSize(
                preferredSize: Size.fromHeight(2),
                child: LinearProgressIndicator(minHeight: 2),
              )
            : null,
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _enCours ? null : () => _ouvrir(),
        icon: const Icon(Icons.add),
        label: Text(l.ajouter),
      ),
      body: collection.when(
        loading: () => EtatChargement(message: l.chargement),
        error: (erreur, _) => EtatErreur(
          erreur: erreur,
          onReessayer: () =>
              ref.invalidate(collectionProvider(definition.ressource)),
        ),
        data: (elements) {
          final filtres = _recherche.isEmpty
              ? elements
              : elements
                  .where((e) => definition
                      .libelle(e)
                      .toLowerCase()
                      .contains(_recherche.toLowerCase()))
                  .toList();

          if (elements.isEmpty) {
            return EtatVide(
              icone: definition.icone,
              titre: l.aucuneDonnee,
              aide: definition.aideVide,
              action: FilledButton.icon(
                onPressed: () => _ouvrir(),
                icon: const Icon(Icons.add),
                label: Text(l.ajouter),
              ),
            );
          }

          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(
                    Jetons.l, Jetons.m, Jetons.l, Jetons.s),
                child: TextField(
                  decoration: InputDecoration(
                    labelText: l.rechercher,
                    prefixIcon: const Icon(Icons.search),
                    isDense: true,
                  ),
                  onChanged: (valeur) => setState(() => _recherche = valeur),
                ),
              ),
              Expanded(
                child: ListView.separated(
                  padding: const EdgeInsets.fromLTRB(
                      Jetons.l, 0, Jetons.l, 96),
                  itemCount: filtres.length,
                  separatorBuilder: (_, __) => const SizedBox(height: Jetons.s),
                  itemBuilder: (contexte, index) {
                    final element = filtres[index];
                    return Card(
                      clipBehavior: Clip.antiAlias,
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Jetons.attenue,
                          child: Icon(definition.icone,
                              size: 20, color: Jetons.primaire),
                        ),
                        title: Text(definition.libelle(element),
                            style: const TextStyle(
                                fontWeight: FontWeight.w600)),
                        subtitle: Text(definition.sousTitre(contexte, element)),
                        onTap: () => _ouvrir(element),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              tooltip: l.modifier,
                              onPressed: () => _ouvrir(element),
                              icon: const Icon(Icons.edit_outlined),
                            ),
                            IconButton(
                              tooltip: l.supprimer,
                              onPressed: () => _supprimer(element),
                              icon: const Icon(Icons.delete_outline,
                                  color: Jetons.danger),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
