import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/api.dart';
import '../core/session.dart';
import '../core/theme.dart';
import '../l10n/traductions.dart';

/// Connexion et création d'établissement sur le même écran.
///
/// Deux pages séparées obligeraient un nouveau directeur à comprendre
/// laquelle le concerne avant d'avoir rien vu du produit.
class PageConnexion extends ConsumerStatefulWidget {
  const PageConnexion({super.key});

  @override
  ConsumerState<PageConnexion> createState() => _PageConnexionState();
}

class _PageConnexionState extends ConsumerState<PageConnexion> {
  final _formulaire = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _motDePasse = TextEditingController();
  final _nomEcole = TextEditingController();
  final _emailEcole = TextEditingController();
  final _nom = TextEditingController();
  final _prenom = TextEditingController();

  bool _inscription = false;
  bool _enCours = false;
  bool _motDePasseVisible = false;
  String? _erreur;

  @override
  void dispose() {
    for (final controleur in [
      _email, _motDePasse, _nomEcole, _emailEcole, _nom, _prenom,
    ]) {
      controleur.dispose();
    }
    super.dispose();
  }

  Future<void> _valider() async {
    if (!_formulaire.currentState!.validate()) return;
    setState(() {
      _enCours = true;
      _erreur = null;
    });
    final l = context.l10n;
    try {
      final session = ref.read(sessionProvider.notifier);
      if (_inscription) {
        await session.inscrire(
          nomEcole: _nomEcole.text.trim(),
          emailEcole: _emailEcole.text.trim(),
          nom: _nom.text.trim(),
          prenom: _prenom.text.trim(),
          email: _email.text.trim(),
          motDePasse: _motDePasse.text,
        );
      } else {
        await session.connecter(_email.text.trim(), _motDePasse.text);
      }
      if (mounted) context.go('/tableau-de-bord');
    } on ErreurApi catch (erreur) {
      setState(() {
        _erreur = erreur.reseau
            ? l.erreurReseau
            : (erreur.authentification || erreur.code == 400)
                ? (erreur.message.isEmpty
                    ? l.identifiantsInvalides
                    : erreur.message)
                : (erreur.message.isEmpty
                    ? l.identifiantsInvalides
                    : erreur.message);
      });
    } finally {
      if (mounted) setState(() => _enCours = false);
    }
  }

  String? _obligatoire(String? valeur) =>
      (valeur == null || valeur.trim().isEmpty)
          ? context.l10n.champObligatoire
          : null;

  String? _validerEmail(String? valeur) {
    final vide = _obligatoire(valeur);
    if (vide != null) return vide;
    final texte = valeur!.trim();
    if (!texte.contains('@') || !texte.contains('.')) {
      return context.l10n.emailInvalide;
    }
    return null;
  }

  String? _validerMotDePasse(String? valeur) {
    final vide = _obligatoire(valeur);
    if (vide != null) return vide;
    if (_inscription && valeur!.length < 12) {
      return context.l10n.motDePasseCourt;
    }
    return null;
  }

  @override
  Widget build(BuildContext contexte) {
    final l = contexte.l10n;
    final theme = Theme.of(contexte);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(Jetons.l),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 460),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(Jetons.s),
                        decoration: BoxDecoration(
                          color: Jetons.primaire,
                          borderRadius:
                              BorderRadius.circular(Jetons.rayonPetit),
                        ),
                        child: const Icon(Icons.schedule,
                            color: Colors.white, size: 22),
                      ),
                      const SizedBox(width: Jetons.s),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(l.appNom,
                                style: theme.textTheme.titleLarge
                                    ?.copyWith(fontWeight: FontWeight.w800)),
                            Text(l.appSousTitre,
                                style: theme.textTheme.bodySmall
                                    ?.copyWith(color: Jetons.encreAttenuee)),
                          ],
                        ),
                      ),
                      const _BasculeLangue(),
                    ],
                  ),
                  const SizedBox(height: Jetons.xl),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(Jetons.l),
                      child: Form(
                        key: _formulaire,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              _inscription
                                  ? l.inscriptionTitre
                                  : l.connexionTitre,
                              style: theme.textTheme.headlineSmall
                                  ?.copyWith(fontWeight: FontWeight.w700),
                            ),
                            const SizedBox(height: Jetons.xs),
                            Text(
                              _inscription
                                  ? l.inscriptionSousTitre
                                  : l.connexionSousTitre,
                              style: theme.textTheme.bodyMedium
                                  ?.copyWith(color: Jetons.encreAttenuee),
                            ),
                            const SizedBox(height: Jetons.l),
                            if (_inscription) ...[
                              TextFormField(
                                controller: _nomEcole,
                                decoration:
                                    InputDecoration(labelText: l.nomEtablissement),
                                validator: _obligatoire,
                                textInputAction: TextInputAction.next,
                              ),
                              const SizedBox(height: Jetons.m),
                              TextFormField(
                                controller: _emailEcole,
                                decoration: InputDecoration(
                                    labelText: l.emailEtablissement),
                                keyboardType: TextInputType.emailAddress,
                                validator: _validerEmail,
                                textInputAction: TextInputAction.next,
                              ),
                              const SizedBox(height: Jetons.m),
                              Row(
                                children: [
                                  Expanded(
                                    child: TextFormField(
                                      controller: _prenom,
                                      decoration:
                                          InputDecoration(labelText: l.prenom),
                                      validator: _obligatoire,
                                      textInputAction: TextInputAction.next,
                                    ),
                                  ),
                                  const SizedBox(width: Jetons.m),
                                  Expanded(
                                    child: TextFormField(
                                      controller: _nom,
                                      decoration:
                                          InputDecoration(labelText: l.nom),
                                      validator: _obligatoire,
                                      textInputAction: TextInputAction.next,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: Jetons.m),
                            ],
                            TextFormField(
                              controller: _email,
                              decoration: InputDecoration(labelText: l.email),
                              keyboardType: TextInputType.emailAddress,
                              autofillHints: const [AutofillHints.email],
                              validator: _validerEmail,
                              textInputAction: TextInputAction.next,
                            ),
                            const SizedBox(height: Jetons.m),
                            TextFormField(
                              controller: _motDePasse,
                              decoration: InputDecoration(
                                labelText: l.motDePasse,
                                suffixIcon: IconButton(
                                  onPressed: () => setState(() =>
                                      _motDePasseVisible = !_motDePasseVisible),
                                  icon: Icon(_motDePasseVisible
                                      ? Icons.visibility_off_outlined
                                      : Icons.visibility_outlined),
                                  tooltip: l.motDePasse,
                                ),
                              ),
                              obscureText: !_motDePasseVisible,
                              autofillHints: const [AutofillHints.password],
                              validator: _validerMotDePasse,
                              onFieldSubmitted: (_) => _valider(),
                            ),
                            if (_erreur != null) ...[
                              const SizedBox(height: Jetons.m),
                              // L'erreur se place au niveau du
                              // formulaire, pas en haut de page : on la
                              // lit sans quitter des yeux le champ que
                              // l'on vient de remplir.
                              Container(
                                padding: const EdgeInsets.all(Jetons.s),
                                decoration: BoxDecoration(
                                  color: Jetons.danger.withValues(alpha: 0.08),
                                  borderRadius: BorderRadius.circular(
                                      Jetons.rayonPetit),
                                  border: Border.all(
                                      color: Jetons.danger
                                          .withValues(alpha: 0.4)),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.error_outline,
                                        color: Jetons.danger, size: 20),
                                    const SizedBox(width: Jetons.s),
                                    Expanded(
                                      child: Text(_erreur!,
                                          style: theme.textTheme.bodySmall
                                              ?.copyWith(
                                                  color: Jetons.danger)),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                            const SizedBox(height: Jetons.l),
                            FilledButton(
                              onPressed: _enCours ? null : _valider,
                              child: _enCours
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          color: Colors.white),
                                    )
                                  : Text(_inscription
                                      ? l.sInscrire
                                      : l.seConnecter),
                            ),
                            const SizedBox(height: Jetons.s),
                            TextButton(
                              onPressed: _enCours
                                  ? null
                                  : () => setState(() {
                                        _inscription = !_inscription;
                                        _erreur = null;
                                      }),
                              child: Text(_inscription
                                  ? l.dejaUnCompte
                                  : l.creerUnCompte),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _BasculeLangue extends ConsumerWidget {
  const _BasculeLangue();

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final courante = Localizations.localeOf(contexte).languageCode;
    return TextButton.icon(
      onPressed: () => ref
          .read(langueProvider.notifier)
          .choisir(Locale(courante == 'ar' ? 'fr' : 'ar')),
      icon: const Icon(Icons.translate, size: 18),
      label: Text(courante == 'ar' ? 'Français' : 'العربية'),
    );
  }
}
