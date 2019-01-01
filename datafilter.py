from datainput import get_data

FILTER_FILE = "filter_list.txt"
loaded = False
filter_list = None

def load_filter_list():
    global loaded
    if not loaded:
        with open(FILTER_FILE, "r") as fin:
            contents = fin.read()
            lines = contents.split("\n")
            lines = [l.replace("\n", "").strip() for l in lines]
            lines = [l for l in lines if l != ""]
            global filter_list
            filter_list = lines
        loaded = True

def filter_list_checker(s):
    for l in filter_list:
        if l in s:
            return True
    return False

def filter_data(data):
    load_filter_list()
    new_data = list(filter(lambda i: not filter_list_checker(i.desc), data))
    return new_data

if __name__ == "__main__":
    data = get_data()
    filtered_data = filter_data(data)
    leftover_data = set(data) - set(filtered_data)
    print (f"Data: {len(data)}")
    print (f"Filtered: {len(filtered_data)}")
    print (f"Leftover: {len(leftover_data)}")
    # print("\n".join(map(lambda i: i.desc, leftover_data)))


