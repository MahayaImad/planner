import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/api.dart';
import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';

/// Chargement en masse par classeur Excel.
///
/// Trois gestes : télécharger, remplir hors ligne, téléverser. Le
/// rapport d'import est montré tel quel — un import refusé doit dire
/// exactement quelle ligne pose problème, sinon l'utilisateur renvoie
/// le même fichier.
class PageDonnees extends ConsumerStatefulWidget {
  const PageDonnees({super.key});

  @override
  ConsumerState<PageDonnees> createState() => _PageDonneesState();
}

class _PageDonneesState extends ConsumerState<PageDonnees> {
  bool _enCours = false;
  Map<String, dynamic>? _rapport;
  String? _erreur;

  Future<void> _enregistrerClasseur(String chemin, String nom) async {
    setState(() {
      _enCours = true;
      _erreur = null;
    });
    try {
      final octets = await ref.read(apiProvider).telecharger(chemin);
      final emplacement = await getSaveLocation(
        suggestedName: nom,
        acceptedTypeGroups: const [
          XTypeGroup(label: 'Excel', extensions: ['xlsx']),
        ],
      );
      if (emplacement == null) return;
      await XFile.fromData(
        octets,
        name: nom,
        mimeType: 'application/vnd.openxmlformats-officedocument'
            '.spreadsheetml.sheet',
      ).saveTo(emplacement.path);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.l10n.fichierEnregistre)),
        );
      }
    } on ErreurApi catch (erreur) {
      setState(() => _erreur = erreur.reseau
          ? context.l10n.erreurReseau
          : erreur.message);
    } finally {
      if (mounted) setState(() => _enCours = false);
    }
  }

  Future<void> _televerser({required bool apercu}) async {
    final fichier = await openFile(
      acceptedTypeGroups: const [
        XTypeGroup(label: 'Excel', extensions: ['xlsx']),
      ],
    );
    if (fichier == null) return;
    setState(() {
      _enCours = true;
      _erreur = null;
      _rapport = null;
    });
    try {
      final octets = await fichier.readAsBytes();
      final reponse = await ref.read(apiProvider).televerser(
            '/donnees/importer',
            octets,
            fichier.name,
            requete: apercu ? {'apercu': 'true'} : null,
          );
      setState(() => _rapport = reponse as Map<String, dynamic>);
    } on ErreurApi catch (erreur) {
      setState(() => _erreur = erreur.reseau
          ? context.l10n.erreurReseau
          : erreur.message);
    } finally {
      if (mounted) setState(() => _enCours = false);
    }
  }

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final theme = Theme.of(contexte);

    return Scaffold(
      appBar: AppBar(title: Text(l.donnees)),
      body: ListView(
        padding: const EdgeInsets.all(Jetons.l),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(Jetons.l),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l.classeurTitre,
                      style: theme.textTheme.titleMedium
                          ?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: Jetons.xs),
                  Text(l.classeurAide,
                      style: theme.textTheme.bodyMedium
                          ?.copyWith(color: Jetons.encreAttenuee)),
                  const SizedBox(height: Jetons.l),
                  Wrap(
                    spacing: Jetons.s,
                    runSpacing: Jetons.s,
                    children: [
                      FilledButton.icon(
                        onPressed: _enCours
                            ? null
                            : () => _enregistrerClasseur(
                                '/donnees/modele.xlsx',
                                'modele-etablissement.xlsx'),
                        icon: const Icon(Icons.download_outlined),
                        label: Text(l.telechargerModele),
                      ),
                      OutlinedButton.icon(
                        onPressed: _enCours
                            ? null
                            : () => _enregistrerClasseur(
                                '/donnees/export.xlsx',
                                'donnees-etablissement.xlsx'),
                        icon: const Icon(Icons.file_download_outlined),
                        label: Text(l.exporterDonnees),
                      ),
                    ],
                  ),
                  const Divider(height: Jetons.xl),
                  Wrap(
                    spacing: Jetons.s,
                    runSpacing: Jetons.s,
                    children: [
                      FilledButton.icon(
                        onPressed:
                            _enCours ? null : () => _televerser(apercu: false),
                        icon: const Icon(Icons.upload_outlined),
                        label: Text(l.importerClasseur),
                      ),
                      OutlinedButton.icon(
                        onPressed:
                            _enCours ? null : () => _televerser(apercu: true),
                        icon: const Icon(Icons.fact_check_outlined),
                        label: Text(l.verifierSansEcrire),
                      ),
                    ],
                  ),
                  if (_enCours) ...[
                    const SizedBox(height: Jetons.m),
                    const LinearProgressIndicator(),
                  ],
                ],
              ),
            ),
          ),
          if (_erreur != null) ...[
            const SizedBox(height: Jetons.m),
            _Bandeau(
              couleur: Jetons.danger,
              icone: Icons.error_outline,
              titre: _erreur!,
            ),
          ],
          if (_rapport != null) ...[
            const SizedBox(height: Jetons.m),
            _RapportImport(rapport: _rapport!),
          ],
        ],
      ),
    );
  }
}

class _RapportImport extends StatelessWidget {
  const _RapportImport({required this.rapport});

  final Map<String, dynamic> rapport;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final theme = Theme.of(contexte);
    final valide = rapport['valide'] == true;
    final applique = rapport['applique'] == true;
    final erreurs = (rapport['erreurs'] as List?) ?? const [];
    final crees = (rapport['crees'] as Map?) ?? const {};
    final modifies = (rapport['modifies'] as Map?) ?? const {};
    final absents =
        (rapport['presents_en_base_absents_du_fichier'] as Map?) ?? const {};

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Jetons.l),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _Bandeau(
              couleur: valide ? Jetons.succes : Jetons.danger,
              icone: valide ? Icons.check_circle_outline : Icons.error_outline,
              titre: valide
                  ? (applique ? l.importApplique : l.importValide)
                  : l.importRefuse,
            ),
            if (!valide) ...[
              const SizedBox(height: Jetons.m),
              for (final erreur in erreurs)
                Padding(
                  padding: const EdgeInsets.only(bottom: Jetons.xs),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('•  '),
                      Expanded(
                        child: Text('$erreur',
                            style: theme.textTheme.bodySmall),
                      ),
                    ],
                  ),
                ),
            ],
            if (valide) ...[
              const SizedBox(height: Jetons.m),
              Table(
                columnWidths: const {
                  0: FlexColumnWidth(2),
                  1: FlexColumnWidth(1),
                  2: FlexColumnWidth(1),
                },
                children: [
                  TableRow(children: [
                    Text(l.feuille, style: theme.textTheme.labelMedium),
                    Text(l.creees, style: theme.textTheme.labelMedium),
                    Text(l.misesAJour, style: theme.textTheme.labelMedium),
                  ]),
                  for (final entree in crees.entries)
                    TableRow(children: [
                      Padding(
                        padding: const EdgeInsets.symmetric(
                            vertical: Jetons.xs),
                        child: Text('${entree.key}'),
                      ),
                      Text('${entree.value}'),
                      Text('${modifies[entree.key] ?? 0}'),
                    ]),
                ],
              ),
              for (final entree in absents.entries)
                if ((entree.value as List).isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: Jetons.s),
                    child: Text(
                      l.absentsDuFichier(
                          '${entree.key}', (entree.value as List).join(', ')),
                      style: theme.textTheme.bodySmall
                          ?.copyWith(color: Jetons.alerte),
                    ),
                  ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Bandeau extends StatelessWidget {
  const _Bandeau({
    required this.couleur,
    required this.icone,
    required this.titre,
  });

  final Color couleur;
  final IconData icone;
  final String titre;

  @override
  Widget build(BuildContext contexte) => Container(
        padding: const EdgeInsets.all(Jetons.m),
        decoration: BoxDecoration(
          color: couleur.withValues(alpha: 0.08),
          border: Border.all(color: couleur.withValues(alpha: 0.4)),
          borderRadius: BorderRadius.circular(Jetons.rayonPetit),
        ),
        child: Row(
          children: [
            Icon(icone, color: couleur, size: 20),
            const SizedBox(width: Jetons.s),
            Expanded(
              child: Text(titre,
                  style: Theme.of(contexte)
                      .textTheme
                      .bodyMedium
                      ?.copyWith(color: couleur, fontWeight: FontWeight.w600)),
            ),
          ],
        ),
      );
}
