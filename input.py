from os import listdir

CSV_DIR = "csv/"

def get_data():
    files = [f for f in listdir(CSV_DIR) if f[-4:] == ".csv"]

    data = []

    for f in files:
        


class Transaction():
    def __init__(self, date, desc, amt, label, ref_num):
        self.date = date
        self.desc = desc
        self.amt = amt
        self.label = label
        self.ref_num = ref_num
    def __repl__(self):
        return f"{{ {self.date}, {self.desc}, {self.amt}, {self.label}, {self.ref_num},  }}"
    def __str__(self):
        return self.__repl__()



if __name__ == "__main__":
    get_data()

