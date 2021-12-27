import localbase
class Login():
    def logOnDatabase(self, user_id, localbase):
        self.__user = localbase.getUser(user_id)
        return self
    
    def is_active(self):
        return True

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user[0])