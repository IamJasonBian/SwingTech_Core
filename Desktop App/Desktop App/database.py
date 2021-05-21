import datetime


class DataBase:
    def __init__(self, repo):
        pass

    def validate(self):
        return True

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]


