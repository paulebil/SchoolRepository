from app.repository.school import SchoolRepository, School

class SchoolService:
    def __init__(self,school_repository: SchoolRepository ):
        self.school_repository = school_repository

    async def create_school(self, data):
        pass