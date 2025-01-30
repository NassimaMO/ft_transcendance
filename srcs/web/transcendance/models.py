from django.db import models

# Create your models here.

class Author :
    name: str
    nickname: str
    date: str
    img: str
    description: str

    def __init__(self, name) :
        self.name = name
        if (name == "Theo") :
            self.nickname = "The aux baies"
            self.date = "novembre 2022"
            self.img = "tea"
        if (name == "Nassima") :
            self.nickname = "Sheiilll"
            self.date = "mai 2022"
            self.img = "sheil"
        if (name == "Nily") :
            self.nickname = "Killjoy"
            self.date = "mai 2022"
            self.img = "valorant"