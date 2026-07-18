"""
GetAllWithAssociationUseCase — retorna todos los estudiantes con flag de asociación.

Si user_id es None, is_associated=False para todos.
"""

from app.domain.student.repositories import StudentRepository
from app.domain.student.student import StudentWithAssociation


class GetAllWithAssociationUseCase:
    def __init__(self, repo: StudentRepository):
        self.repo = repo

    def execute(self, user_id: int | None) -> list[StudentWithAssociation]:
        students = self.repo.list_active_with_school()

        if user_id is None:
            return [StudentWithAssociation(student=s, associated=False) for s in students]

        associated_ids = set(self.repo.get_associations_for_user(user_id))
        return [StudentWithAssociation(student=s, associated=s.id in associated_ids) for s in students]
