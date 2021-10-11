from difflib import SequenceMatcher
import sys
import datainput
import classify
import s3datasource

def convert_transaction_to_string(transaction):
    prop_list = [
        transaction.classification,
        # transaction.classification_debug,
        transaction.desc,
        transaction.amt,
        transaction.date,
        transaction.source,
    ]
    first = True
    line = ""
    for prop in prop_list:
        newline = '' if first else '\t'
        line += f"{newline}{prop}"
        first = False
    return line

def create_transaction_csv_blob(transactions):
    transaction_lines = map(convert_transaction_to_string, transactions)
    transaction_blob = "\n".join(transaction_lines)
    return transaction_blob


def group_by_similarity(data):
    # group data up by the length of their description
    print("Creating length map")
    length_map = {}
    for index, tran in enumerate(data):
        length = len(tran.desc)
        if not length in length_map:
            length_map[length] = []
        length_map[length].append(index)
    print(f"Length map created with {len(length_map.keys())} groups")

    # now group up groups by length proximity, e.g., transactions 
    # with description length of 5 get grouped up with transactions of
    # description length 6 and 4
    print("Gathering local length groups")
    length_groups = []
    max_length_in_map = max(length_map.keys())
    length_variability = 0
    for length in range(max_length_in_map + 1):
        local_length_group = []
        # get current length
        if length in length_map:
            local_length_group += length_map[length]

        # get the lengths around this length
        start = length - length_variability
        stop = length_variability + length
        for local_length in range(start, stop + 1):
            if local_length < 0 or local_length > max_length_in_map:
                continue
            if local_length in length_map:
                local_length_group += length_map[local_length]
        # add this group to the list of groups
        length_groups.append(local_length_group)
    print(f"{len(length_groups)} length groups gathered")

    print(f"Filling in edges with length groups")
    edges = {}
    # iterate through each length group and establish edges for transactions
    # with similar descriptions
    for length_group_index, length_group in enumerate(length_groups):
        print(f"On length group {length_group_index + 1}", end="\r")
        for index1 in length_group:
            trans1 = data[index1]
            for index2 in range(index1 + 1, len(length_group)):
                trans2 = data[index2]
                if trans_are_similar(trans1,trans2):
                    if not index1 in edges:
                        edges[index1] = []
                    edges[index1].append(index2)
                    if not index2 in edges:
                        edges[index2] = []
                    edges[index2].append(index1)
    print("Finished all groups!")
    print("Grouping islands")
    # need to go through the graph and convert the islands into lists
    queue = list(range(len(data)))
    islands = []
    visited_global = {}
    while len(queue) > 0:
        start = queue.pop(0)
        if start in visited_global:
            continue
        visited = {}
        traverse_similarity_node(edges, visited, start)

        island = list(visited.keys())
        for node in island:
            visited_global[node] = True
        islands.append(island)
    print(f"Finished grouping {len(islands)} islands")
    islands = sorted(islands, key=lambda i: len(i), reverse=True)
    flattened_indices = []
    for island in islands:
        flattened_indices += island
    return list(map(lambda i: data[i], flattened_indices))

def traverse_similarity_node(edges, visited, node):
    if node in visited:
        return
    visited[node] = True
    if node in edges:
        for child in edges[node]:
            traverse_similarity_node(edges, visited, child)

def trans_are_similar(t1, t2):
    ratio = SequenceMatcher(None, t1.desc, t2.desc).ratio()
    return ratio >= 0.8

if len(sys.argv) != 2:
    raise Exception("must have one argument which is the rules file")


c = s3datasource.get_context()
LOCAL_DATA_DIR = c.get_var("LOCAL_DATA_DIR")

datasource = datainput.get_local_data_source(LOCAL_DATA_DIR)
data = list(datainput.parse_data_source(datasource))
# data = list(datainput.parse_data_source_last_month(datasource))
rules_contents = None
with open(sys.argv[1],'r') as fin:
    rules_contents = fin.read()
rules = classify.process_rules(rules_contents)
classify.classify(data, rules)

classified_data = list(filter(lambda t: t.classification != 'none', data))
print(f"{len(classified_data)} of {len(data)} classified")

# sorted_data = sorted(data, key=lambda t: t.date)
sorted_data = data
sorted_data = sorted(sorted_data, key=lambda t: t.desc.lower(), reverse=False)
sorted_data = sorted(sorted_data, key=lambda t: t.classification, reverse=False)
sorted_data = sorted(sorted_data, key=lambda t: abs(float(t.amt)), reverse=True)
# sorted_data = group_by_similarity(sorted_data)
sorted_data = sorted(sorted_data, key=lambda t: True if t.classification == 'none' else False, reverse=True)

classified_total = sum(map(lambda t: abs(t.amt), filter(lambda t: t.classification != 'none', sorted_data)))
unclassified_total = sum(map(lambda t: abs(t.amt), filter(lambda t: t.classification == 'none', sorted_data)))

print(f'classified = {classified_total} unclassified = {unclassified_total}')

# output_path = f"classification_test_{c.get_run_id()}.xlsx"
# output_spreadsheet(data, output_path)
transaction_blob = create_transaction_csv_blob(sorted_data)
with open('classified_transactions.csv','w') as fout:
    fout.write(transaction_blob)

