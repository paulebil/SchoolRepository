from  app.repository.user import UserRepository

class StudentService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository