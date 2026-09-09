from .school import EcoleCreate, EcoleRead
from .user import UtilisateurCreate, UtilisateurRead, Token, LoginRequest
from .teacher import ProfesseurCreate, ProfesseurRead, ProfesseurUpdate
from .subject import MatiereCreate, MatiereRead, MatiereUpdate
from .room import SalleCreate, SalleRead, SalleUpdate
from .class_ import ClasseCreate, ClasseRead, ClasseUpdate
from .schedule import (
    EmploiDuTempsCreate, EmploiDuTempsRead,
    LeconRead, GenererRequest, CoursRequisInput,
    GrilleInput, FenetreInput, PonderationsInput, DiagnosticResponse,
    TacheRead,
)
from .availability import DisponibiliteCreate, DisponibiliteRead
from .settings import (
    ParametresRead, ParametresUpdate, FenetreCreate, FenetreRead,
)
