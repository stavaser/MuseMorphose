import glob
import pickle

def pickle_load(f):
  return pickle.load(open(f, 'rb'))

def pickle_dump(obj, f):
  pickle.dump(obj, open(f, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

test_pieces = []

for orig_file in glob.glob("./ailab17k_from-scratch_remi/events/*.pkl"):
    out_file = orig_file.replace("/events/", "/")
    events = pickle_load(orig_file)
    for event in events:
        if event["name"] == "Note_Velocity":
            event["value"] = min(max(40, event["value"]), 80)
    bar_idx = []
    for idx, event in enumerate(events):
        if event["name"] == "Bar":
            bar_idx.append(idx)

    result = (bar_idx, events)
    test_pieces.append(out_file.split("/")[-1])
    pickle_dump(result, out_file)

pickle_dump(test_pieces, "../pickles/custom_test_pieces.pkl")