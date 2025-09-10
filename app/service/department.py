from app.repository.department import DepartmentRepository

class DepartmentService:
    def __init__(self, department_repository: DepartmentRepository):
        self.department_repository = department_repository

    async def create_department(self, data):
        pass
