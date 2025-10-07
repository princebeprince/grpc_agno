import zipfile
import pickle
import os

def zip_to_pkl(zip_path, pkl_path):
    """
    Convert a .zip file to a .pkl file by reading all files inside
    and saving their contents in a serialized (pickled) dictionary.
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"File not found: {zip_path}")

    data_dict = {}

    # Open and extract contents of the zip
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            with zip_ref.open(file_name) as file:
                data_dict[file_name] = file.read()  # store as bytes

    # Save as pickle
    with open(pkl_path, 'wb') as pkl_file:
        pickle.dump(data_dict, pkl_file)

    print(f"✅ Successfully created {pkl_path} from {zip_path}")


if __name__ == "__main__":
    zip_file = "Archive.zip"   # input zip file path
    pkl_file = "output.pkl"    # output pkl file path
    zip_to_pkl(zip_file, pkl_file)
