import s3datasource

loaded = False
filter_list = None

def load_filter_list(c):
    global loaded
    if not loaded:
        contents = s3datasource.get_object(c, c.get_var("FILTER_FILEPATH"))
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

def filter_data(c, data):
    load_filter_list(c)
    new_data = list(filter(lambda i: not filter_list_checker(i.desc), data))
    return new_data
