class enemy:
    def __init__(self):
        self.HP = 10

class enemyName:
    def __init__(self):
        self.par = enemy()
    def update(self):
        print(self.par.HP)

eN = enemyName()
eN.update()