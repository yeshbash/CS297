import pickle


def load_object(path):
    with open(path,"rb") as f:
        _object = pickle.load(f)
        print("object loaded from "+path)
    return _object


def save_object(object, path):
    with open(path, "wb") as f:
        pickle.dump(object, f)
        print("object saved to " + path)



