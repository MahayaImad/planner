import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api.dart';
import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';

/// Lancement du solveur et suivi de la recherche.
///
/// Une génération dure de quelques secondes à un quart d'heure. Le
/// dialogue montre donc ce qui avance — solutions trouvées, coût
/// courant — plutôt qu'un sablier muet, et laisse interrompre : au
/// bout de deux minutes, une proposition acceptable vaut souvent mieux
/// qu'une meilleure obtenue dix minutes plus tard.
class DialogueGeneration extends ConsumerStatefulWidget {
  const DialogueGeneration({super.key, required this.edtId});

  final int edtId;

  @override
  ConsumerState<DialogueGeneration> createState() => _DialogueGenerationState();
}

class _DialogueGenerationState extends ConsumerState<DialogueGeneration> {
  static const _limites = [60, 120, 300, 600, 900];

  int _limite = 300;
  int? _tacheId;
  Map<String, dynamic>? _tache;
  String? _erreur;
  Timer? _suivi;
  DateTime? _depart;

  @override
  void dispose() {
    _suivi?.cancel();
    super.dispose();
  }

  Future<void> _lancer() async {
    setState(() {
      _erreur = null;
      _tache = null;
    });
    try {
      final reponse = await ref.read(apiProvider).post(
          '/emplois-du-temps/${widget.edtId}/generer',
          corps: {'limite_secondes': _limite}) as Map<String, dynamic>;
      setState(() {
        _tacheId = reponse['id'] as int;
        _depart = DateTime.now();
      });
      // Une seconde entre deux relevés : assez pour voir le coût
      // descendre, assez peu pour ne pas marteler le serveur pendant un
      // quart d'heure.
      _suivi = Timer.periodic(const Duration(seconds: 1), (_) => _relever());
      _relever();
    } on ErreurApi catch (erreur) {
      setState(() => _erreur = _phrase(erreur));
    }
  }

  Future<void> _relever() async {
    if (_tacheId == null) return;
    try {
      final tache = await ref.read(apiProvider).get(
              '/emplois-du-temps/${widget.edtId}/taches/$_tacheId')
          as Map<String, dynamic>;
      if (!mounted) return;
      setState(() => _tache = tache);
      if (tache['terminee'] == true) {
        _suivi?.cancel();
        _suivi = null;
      }
    } on ErreurApi {
      // Un relevé manqué n'est pas grave : le suivant reprendra.
    }
  }

  Future<void> _annuler() async {
    if (_tacheId == null) return;
    try {
      await ref.read(apiProvider).delete(
          '/emplois-du-temps/${widget.edtId}/taches/$_tacheId');
    } on ErreurApi catch (erreur) {
      setState(() => _erreur = _phrase(erreur));
    }
  }

  String _phrase(ErreurApi erreur) => erreur.reseau
      ? context.l10n.erreurReseau
      : (erreur.message.isEmpty ? '${erreur.code}' : erreur.message);

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final theme = Theme.of(contexte);
    final tache = _tache;
    final terminee = tache?['terminee'] == true;
    final enCours = _tacheId != null && !terminee;
    final reussie = tache?['statut'] == 'terminee';

    return AlertDialog(
      title: Text(l.genererTitre),
      content: SizedBox(
        width: 460,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_tacheId == null) ...[
              Text(l.genererAide,
                  style: theme.textTheme.bodyMedium
                      ?.copyWith(color: Jetons.encreAttenuee)),
              const SizedBox(height: Jetons.l),
              DropdownButtonFormField<int>(
                initialValue: _limite,
                decoration: InputDecoration(
                    labelText: l.tempsDeCalcul, helperText: l.aideTempsDeCalcul),
                items: [
                  for (final limite in _limites)
                    DropdownMenuItem(
                        value: limite, child: Text(l.minutes(limite ~/ 60))),
                ],
                onChanged: (valeur) =>
                    setState(() => _limite = valeur ?? _limite),
              ),
            ] else ...[
              _Avancement(
                tache: tache,
                enCours: enCours,
                ecoule: _depart == null
                    ? Duration.zero
                    : DateTime.now().difference(_depart!),
                limite: _limite,
              ),
            ],
            if (_erreur != null) ...[
              const SizedBox(height: Jetons.m),
              Text(_erreur!,
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: Jetons.danger)),
            ],
          ],
        ),
      ),
      actions: [
        if (_tacheId == null) ...[
          TextButton(
            onPressed: () => Navigator.of(contexte).pop(false),
            child: Text(l.annuler),
          ),
          FilledButton.icon(
            onPressed: _lancer,
            icon: const Icon(Icons.auto_fix_high),
            label: Text(l.lancer),
          ),
        ] else if (enCours) ...[
          TextButton(
            onPressed: _annuler,
            child: Text(l.interrompre),
          ),
          FilledButton(
            // Fermer ne fait qu'arrêter de regarder : la recherche
            // continue côté serveur, et l'écran se rafraîchira.
            onPressed: () => Navigator.of(contexte).pop(true),
            child: Text(l.laisserTourner),
          ),
        ] else
          FilledButton(
            onPressed: () => Navigator.of(contexte).pop(reussie),
            child: Text(l.fermer),
          ),
      ],
    );
  }
}

class _Avancement extends StatelessWidget {
  const _Avancement({
    required this.tache,
    required this.enCours,
    required this.ecoule,
    required this.limite,
  });

  final Map<String, dynamic>? tache;
  final bool enCours;
  final Duration ecoule;
  final int limite;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final theme = Theme.of(contexte);
    final statut = '${tache?['statut'] ?? ''}';
    final echouee = statut == 'echouee';
    final annulee = statut == 'annulee';
    final erreurs = (tache?['erreurs'] as List?) ?? const [];
    final qualite = (tache?['resultat'] as Map?)?['qualite'] as Map?;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            if (enCours)
              const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2))
            else
              Icon(
                echouee || annulee
                    ? Icons.error_outline
                    : Icons.check_circle_outline,
                color: echouee || annulee ? Jetons.danger : Jetons.succes,
              ),
            const SizedBox(width: Jetons.s),
            Expanded(
              child: Text(
                '${tache?['message'] ?? l.chargement}',
                style: theme.textTheme.bodyMedium
                    ?.copyWith(fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
        if (enCours) ...[
          const SizedBox(height: Jetons.m),
          LinearProgressIndicator(
            value: limite == 0
                ? null
                : (ecoule.inSeconds / limite).clamp(0.0, 1.0),
          ),
          const SizedBox(height: Jetons.xs),
          Text(l.secondesEcoulees(ecoule.inSeconds, limite),
              style: theme.textTheme.bodySmall
                  ?.copyWith(color: Jetons.encreAttenuee)),
        ],
        const SizedBox(height: Jetons.m),
        // Le coût et le nombre de solutions descendent au fil de la
        // recherche : c'est ce qui montre qu'elle travaille encore.
        Wrap(
          spacing: Jetons.s,
          runSpacing: Jetons.s,
          children: [
            if ((tache?['nb_solutions'] as int? ?? 0) > 0)
              Chip(label: Text(l.solutionsTrouvees(tache!['nb_solutions'] as int))),
            if (tache?['cout_courant'] != null)
              Chip(label: Text(l.coutCourant('${tache!['cout_courant']}'))),
            if ((tache?['lecons_planifiees'] as int? ?? 0) > 0)
              Chip(label: Text(
                  l.leconsPlacees(tache!['lecons_planifiees'] as int))),
          ],
        ),
        if (qualite != null) ...[
          const SizedBox(height: Jetons.m),
          Text(l.qualiteObtenue, style: theme.textTheme.labelLarge),
          const SizedBox(height: Jetons.xs),
          Wrap(
            spacing: Jetons.s,
            runSpacing: Jetons.s,
            children: [
              Chip(label: Text(
                  l.trousEleves('${qualite['trous_classes'] ?? 0}'))),
              Chip(label: Text(
                  l.trousProfesseurs('${qualite['trous_professeurs'] ?? 0}'))),
            ],
          ),
        ],
        if (erreurs.isNotEmpty) ...[
          const SizedBox(height: Jetons.m),
          for (final erreur in erreurs)
            Padding(
              padding: const EdgeInsets.only(bottom: Jetons.xs),
              child: Text('• $erreur',
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: Jetons.danger)),
            ),
        ],
      ],
    );
  }
}
