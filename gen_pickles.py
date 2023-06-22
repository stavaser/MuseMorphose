from utils import pickle_load, pickle_dump

if __name__ == "__main__":
    pickle_dump(["1.pkl", "2.pkl", "3.pkl"], "./pickles/custom_test_pieces.pkl")
    # print(pickle_load("./pickles/custom_vocab.pkl"))