import 'package:flutter/material.dart';

import '../core/api.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';

/// Attente. Un texte accompagne toujours l'indicateur : un rond qui
/// tourne seul ne dit pas si l'application travaille ou si elle est
/// bloquée.
class EtatChargement extends StatelessWidget {
  const EtatChargement({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext contexte) => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: Jetons.m),
            Text(message,
                style: Theme.of(contexte)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(color: Jetons.encreAttenuee)),
          ],
        ),
      );
}

/// Panne. On dit ce qui s'est passé et on propose la seule action utile.
class EtatErreur extends StatelessWidget {
  const EtatErreur({super.key, required this.erreur, this.onReessayer});

  final Object erreur;
  final VoidCallback? onReessayer;

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final message = erreur is ErreurApi
        ? ((erreur as ErreurApi).reseau
            ? l.erreurReseau
            : ((erreur as ErreurApi).message.isEmpty
                ? l.erreurReseau
                : (erreur as ErreurApi).message))
        : '$erreur';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(Jetons.l),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cloud_off, size: 40, color: Jetons.encreAttenuee),
            const SizedBox(height: Jetons.m),
            Text(message, textAlign: TextAlign.center),
            if (onReessayer != null) ...[
              const SizedBox(height: Jetons.m),
              FilledButton.icon(
                onPressed: onReessayer,
                icon: const Icon(Icons.refresh),
                label: Text(l.reessayer),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Rien à montrer — mais l'écran doit dire quoi faire, pas rester nu.
class EtatVide extends StatelessWidget {
  const EtatVide({
    super.key,
    required this.icone,
    required this.titre,
    this.aide,
    this.action,
  });

  final IconData icone;
  final String titre;
  final String? aide;
  final Widget? action;

  @override
  Widget build(BuildContext contexte) => Center(
        child: Padding(
          padding: const EdgeInsets.all(Jetons.l),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icone, size: 44, color: Jetons.encreAttenuee),
              const SizedBox(height: Jetons.m),
              Text(titre,
                  textAlign: TextAlign.center,
                  style: Theme.of(contexte).textTheme.titleMedium),
              if (aide != null) ...[
                const SizedBox(height: Jetons.xs),
                Text(aide!,
                    textAlign: TextAlign.center,
                    style: Theme.of(contexte)
                        .textTheme
                        .bodySmall
                        ?.copyWith(color: Jetons.encreAttenuee)),
              ],
              if (action != null) ...[
                const SizedBox(height: Jetons.l),
                action!,
              ],
            ],
          ),
        ),
      );
}
