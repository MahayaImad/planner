import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

/// Erreur remontée par l'API, avec de quoi l'afficher telle quelle.
class ErreurApi implements Exception {
  ErreurApi(this.code, this.message);

  /// 0 quand la requête n'a jamais atteint le serveur.
  final int code;
  final String message;

  bool get reseau => code == 0;
  bool get authentification => code == 401 || code == 403;

  @override
  String toString() => 'ErreurApi($code, $message)';
}

/// Client HTTP de la plateforme.
///
/// L'adresse du serveur se règle au lancement
/// (`--dart-define=API_BASE=https://…`) : la même compilation sert donc
/// le développement, la recette et la production, sans code conditionnel
/// disséminé dans l'application.
class Api {
  Api({http.Client? client}) : _client = client ?? http.Client();

  static const base = String.fromEnvironment(
    'API_BASE',
    defaultValue: kReleaseMode ? '/api' : 'http://localhost:8000',
  );

  final http.Client _client;
  String? jeton;

  Map<String, String> _entetes({bool corpsJson = false}) => {
        if (jeton != null) 'Authorization': 'Bearer $jeton',
        if (corpsJson) 'Content-Type': 'application/json',
      };

  Uri _uri(String chemin, [Map<String, dynamic>? requete]) {
    final adresse = Uri.parse('$base$chemin');
    if (requete == null || requete.isEmpty) return adresse;
    return adresse.replace(queryParameters: {
      ...adresse.queryParameters,
      for (final entree in requete.entries)
        entree.key: '${entree.value}',
    });
  }

  Future<dynamic> get(String chemin, {Map<String, dynamic>? requete}) =>
      _envoyer(() => _client.get(_uri(chemin, requete), headers: _entetes()));

  Future<dynamic> post(String chemin, {Object? corps}) => _envoyer(
        () => _client.post(_uri(chemin),
            headers: _entetes(corpsJson: true),
            body: corps == null ? null : jsonEncode(corps)),
      );

  Future<dynamic> put(String chemin, {Object? corps}) => _envoyer(
        () => _client.put(_uri(chemin),
            headers: _entetes(corpsJson: true),
            body: corps == null ? null : jsonEncode(corps)),
      );

  Future<dynamic> patch(String chemin, {Object? corps}) => _envoyer(
        () => _client.patch(_uri(chemin),
            headers: _entetes(corpsJson: true),
            body: corps == null ? null : jsonEncode(corps)),
      );

  Future<dynamic> delete(String chemin) =>
      _envoyer(() => _client.delete(_uri(chemin), headers: _entetes()));

  /// Télécharge un fichier binaire (classeur Excel).
  Future<Uint8List> telecharger(String chemin) async {
    final reponse = await _tenter(
        () => _client.get(_uri(chemin), headers: _entetes()));
    if (reponse.statusCode >= 400) {
      throw ErreurApi(reponse.statusCode, _message(reponse));
    }
    return reponse.bodyBytes;
  }

  /// Téléverse un fichier en multipart.
  Future<dynamic> televerser(
    String chemin,
    Uint8List contenu,
    String nomFichier, {
    Map<String, dynamic>? requete,
  }) async {
    final requeteHttp = http.MultipartRequest('POST', _uri(chemin, requete))
      ..headers.addAll(_entetes())
      ..files.add(http.MultipartFile.fromBytes('fichier', contenu,
          filename: nomFichier));
    try {
      final diffusee = await requeteHttp.send();
      final reponse = await http.Response.fromStream(diffusee);
      return _lire(reponse);
    } on ErreurApi {
      rethrow;
    } catch (_) {
      throw ErreurApi(0, 'reseau');
    }
  }

  Future<http.Response> _tenter(
      Future<http.Response> Function() operation) async {
    try {
      return await operation();
    } catch (_) {
      throw ErreurApi(0, 'reseau');
    }
  }

  Future<dynamic> _envoyer(Future<http.Response> Function() operation) async =>
      _lire(await _tenter(operation));

  dynamic _lire(http.Response reponse) {
    if (reponse.statusCode == 204 || reponse.bodyBytes.isEmpty) {
      if (reponse.statusCode >= 400) {
        throw ErreurApi(reponse.statusCode, '');
      }
      return null;
    }
    // Le serveur répond en UTF-8 ; s'en remettre à l'en-tête donnerait
    // du latin-1 sur les accents et l'arabe.
    final texte = utf8.decode(reponse.bodyBytes);
    dynamic contenu;
    try {
      contenu = jsonDecode(texte);
    } catch (_) {
      contenu = texte;
    }
    if (reponse.statusCode >= 400) {
      throw ErreurApi(reponse.statusCode, _extraireMessage(contenu));
    }
    return contenu;
  }

  String _message(http.Response reponse) {
    try {
      return _extraireMessage(jsonDecode(utf8.decode(reponse.bodyBytes)));
    } catch (_) {
      return '';
    }
  }

  /// FastAPI rend « detail » tantôt en texte, tantôt en liste d'erreurs
  /// de validation : les deux formes doivent devenir une phrase.
  String _extraireMessage(dynamic contenu) {
    if (contenu is Map && contenu['detail'] != null) {
      final detail = contenu['detail'];
      if (detail is String) return detail;
      if (detail is List) {
        return detail
            .map((e) => e is Map ? '${e['msg'] ?? e}' : '$e')
            .join(' · ');
      }
      return '$detail';
    }
    return contenu is String ? contenu : '';
  }

  void fermer() => _client.close();
}
