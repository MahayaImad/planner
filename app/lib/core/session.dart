import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api.dart';

final apiProvider = Provider<Api>((ref) {
  final api = Api();
  ref.onDispose(api.fermer);
  return api;
});

/// Ce que l'application sait de l'utilisateur connecté.
@immutable
class Session {
  const Session({this.jeton, this.profil, this.pretePourDemarrer = false});

  final String? jeton;
  final Map<String, dynamic>? profil;

  /// Faux tant que les préférences n'ont pas été relues : sans ce
  /// drapeau, l'écran de connexion s'afficherait une fraction de
  /// seconde à chaque lancement, même pour un utilisateur déjà connecté.
  final bool pretePourDemarrer;

  bool get connectee => jeton != null;
  String get nomEcole => '${profil?['ecole_nom'] ?? ''}';

  Session copie({
    String? jeton,
    Map<String, dynamic>? profil,
    bool? pretePourDemarrer,
    bool vider = false,
  }) =>
      Session(
        jeton: vider ? null : (jeton ?? this.jeton),
        profil: vider ? null : (profil ?? this.profil),
        pretePourDemarrer: pretePourDemarrer ?? this.pretePourDemarrer,
      );
}

const _cleJeton = 'jeton';
const _cleLangue = 'langue';

class SessionNotifier extends StateNotifier<Session> {
  SessionNotifier(this._api) : super(const Session()) {
    _restaurer();
  }

  final Api _api;

  Future<void> _restaurer() async {
    final prefs = await SharedPreferences.getInstance();
    final jeton = prefs.getString(_cleJeton);
    if (jeton == null) {
      state = state.copie(pretePourDemarrer: true);
      return;
    }
    _api.jeton = jeton;
    try {
      final profil = await _api.get('/auth/moi') as Map<String, dynamic>;
      state = Session(
          jeton: jeton, profil: profil, pretePourDemarrer: true);
    } on ErreurApi catch (erreur) {
      // Un jeton périmé se jette ; une panne réseau ne doit pas
      // déconnecter quelqu'un qui a simplement perdu le wifi.
      if (erreur.authentification) {
        await prefs.remove(_cleJeton);
        _api.jeton = null;
        state = const Session(pretePourDemarrer: true);
      } else {
        state = Session(jeton: jeton, pretePourDemarrer: true);
      }
    }
  }

  Future<void> _adopter(Map<String, dynamic> reponse) async {
    final jeton = '${reponse['access_token']}';
    _api.jeton = jeton;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_cleJeton, jeton);
    Map<String, dynamic>? profil;
    try {
      profil = await _api.get('/auth/moi') as Map<String, dynamic>;
    } on ErreurApi {
      profil = null;
    }
    state = Session(jeton: jeton, profil: profil, pretePourDemarrer: true);
  }

  Future<void> connecter(String email, String motDePasse) async {
    final reponse = await _api.post('/auth/connexion',
        corps: {'email': email, 'mot_de_passe': motDePasse});
    await _adopter(reponse as Map<String, dynamic>);
  }

  Future<void> inscrire({
    required String nomEcole,
    required String emailEcole,
    required String nom,
    required String prenom,
    required String email,
    required String motDePasse,
  }) async {
    final reponse = await _api.post('/auth/inscrire', corps: {
      'ecole': {'nom': nomEcole, 'email': emailEcole},
      'admin': {
        'nom': nom,
        'prenom': prenom,
        'email': email,
        'mot_de_passe': motDePasse,
      },
    });
    await _adopter(reponse as Map<String, dynamic>);
  }

  Future<void> deconnecter() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_cleJeton);
    _api.jeton = null;
    state = const Session(pretePourDemarrer: true);
  }
}

final sessionProvider =
    StateNotifierProvider<SessionNotifier, Session>((ref) {
  return SessionNotifier(ref.watch(apiProvider));
});

/// Langue choisie. Null tant que rien n'est enregistré : l'application
/// suit alors la langue du téléphone, ce qui donne l'arabe d'emblée à
/// un utilisateur dont l'appareil est en arabe.
class LangueNotifier extends StateNotifier<Locale?> {
  LangueNotifier() : super(null) {
    _restaurer();
  }

  Future<void> _restaurer() async {
    final prefs = await SharedPreferences.getInstance();
    final code = prefs.getString(_cleLangue);
    if (code != null) state = Locale(code);
  }

  Future<void> choisir(Locale? locale) async {
    final prefs = await SharedPreferences.getInstance();
    if (locale == null) {
      await prefs.remove(_cleLangue);
    } else {
      await prefs.setString(_cleLangue, locale.languageCode);
    }
    state = locale;
  }
}

final langueProvider =
    StateNotifierProvider<LangueNotifier, Locale?>((ref) => LangueNotifier());
