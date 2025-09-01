import face_recognition 
import os
import pickle

def accept_register_new_user(name , image , db_dir):

    embeddings = face_recognition.face_encodings(image)[0]
    print(embeddings)
    os.makedirs(os.path.dirname(db_dir), exist_ok=True)
    file =os.path.join(db_dir, '{}.pickle'.format(name))
    print(file)
    # حفظ الملف على القرص
    with open(file, 'wb') as f:
        print(f)
        pickle.dump(embeddings, f)

def recognize(img, db_path):
    # it is assumed there will be at most 1 match in the db

    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted(os.listdir(db_path))

    match = False
    j = 0
    while not match and j < len(db_dir):
        path_ = os.path.join(db_path, db_dir[j])

        file = open(path_, 'rb')
        embeddings = pickle.load(file)

        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        j += 1

    if match:
        return db_dir[j - 1][:-7]
    else:
        return 'unknown_person'

