import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api.dart';
import 'session.dart';

/// Une collection de l'API : lecture, création, modification,
/// suppression. Les cinq écrans de saisie n'en diffèrent que par le
/// chemin et la forme des champs, pas par la mécanique.
class Ressource {
  const Ressource(this.chemin, {this.methodeModification = 'patch'});

  final String chemin;

  /// Les réglages et le programme s'écrivent en PUT ou en POST selon
  /// les routes déjà en place ; le reste en PATCH.
  final String methodeModification;

  Future<List<Map<String, dynamic>>> lire(Api api) async {
    final reponse = await api.get(chemin) as List;
    return reponse.cast<Map<String, dynamic>>();
  }

  Future<void> creer(Api api, Map<String, dynamic> donnees) =>
      api.post(chemin, corps: donnees);

  Future<void> modifier(Api api, int id, Map<String, dynamic> donnees) =>
      methodeModification == 'put'
          ? api.put('$chemin$id', corps: donnees)
          : api.patch('$chemin$id', corps: donnees);

  Future<void> supprimer(Api api, int id) => api.delete('$chemin$id');
}

const ressourceEnseignants = Ressource('/professeurs/');
const ressourceMatieres = Ressource('/matieres/');
const ressourceSalles = Ressource('/salles/');
const ressourceDivisions = Ressource('/classes/');
const ressourceProgramme = Ressource('/programme/', methodeModification: 'put');

/// Contenu d'une collection. `autoDispose` libère la mémoire dès qu'on
/// quitte l'écran, `keepAlive` étant inutile pour des listes relues en
/// quelques dizaines de millisecondes.
final collectionProvider = FutureProvider.autoDispose
    .family<List<Map<String, dynamic>>, Ressource>((ref, ressource) async {
  return ressource.lire(ref.watch(apiProvider));
});
