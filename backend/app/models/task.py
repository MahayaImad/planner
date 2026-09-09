from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from ..database import Base


class TacheGeneration(Base):
    """
    Une exécution du solveur, suivie en base.

    La génération d'un emploi du temps dure plusieurs minutes : la faire
    dans le cycle requête/réponse monopolise un worker et dépasse le
    délai d'attente du navigateur. La requête est donc enregistrée ici,
    exécutée en arrière-plan, et le client interroge l'avancement.

    La requête d'origine est conservée : une génération est ainsi
    reproductible et auditable.
    """
    __tablename__ = "taches_generation"

    # en_attente → en_cours → terminee | echouee | annulee
    EN_ATTENTE, EN_COURS, TERMINEE, ECHOUEE, ANNULEE = (
        "en_attente", "en_cours", "terminee", "echouee", "annulee")
    STATUTS_FINAUX = (TERMINEE, ECHOUEE, ANNULEE)

    id = Column(Integer, primary_key=True, index=True)
    ecole_id = Column(Integer, ForeignKey("ecoles.id"), nullable=False)
    emploi_du_temps_id = Column(
        Integer, ForeignKey("emplois_du_temps.id", ondelete="CASCADE"), nullable=False)

    statut = Column(String(20), default=EN_ATTENTE, nullable=False, index=True)
    message = Column(String(500))

    requete = Column(Text, nullable=False)      # JSON de la demande
    resultat = Column(Text)                     # JSON du compte rendu
    erreurs = Column(Text)                      # JSON des erreurs de diagnostic

    # Avancement : coût de la meilleure solution trouvée jusqu'ici.
    cout_courant = Column(Integer)
    nb_solutions = Column(Integer, default=0)
    lecons_planifiees = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    emploi_du_temps = relationship("EmploiDuTemps")
