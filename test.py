class test:
    def __init__(self):
        self.info = {}
        self.test()
        
    def test(self):
        aa = {'a':1}

        self.info[aa['a']] = 2
        print(self.info)


t =test()      
    
        
