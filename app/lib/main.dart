import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/routeur.dart';
import 'core/session.dart';
import 'core/theme.dart';
import 'l10n/app_localisations.dart';

void main() {
  runApp(const ProviderScope(child: Application()));
}

class Application extends ConsumerWidget {
  const Application({super.key});

  @override
  Widget build(BuildContext contexte, WidgetRef ref) {
    final routeur = ref.watch(routeurProvider);
    final langue = ref.watch(langueProvider);

    return MaterialApp.router(
      title: 'Planner',
      debugShowCheckedModeBanner: false,
      theme: construireTheme(),
      routerConfig: routeur,
      // Langue nulle = celle de l'appareil. Un téléphone réglé en arabe
      // ouvre donc l'application en arabe, de droite à gauche, sans que
      // personne n'ait rien à régler.
      locale: langue,
      supportedLocales: L.supportedLocales,
      // Sans cette résolution, un appareil réglé dans une langue que
      // nous ne traduisons pas reçoit la PREMIÈRE locale déclarée —
      // l'arabe, par ordre alphabétique. Le français est le repli.
      localeResolutionCallback: (demandee, supportees) {
        if (demandee != null) {
          for (final supportee in supportees) {
            if (supportee.languageCode == demandee.languageCode) {
              return supportee;
            }
          }
        }
        return const Locale('fr');
      },
      localizationsDelegates: const [
        L.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
    );
  }
}
