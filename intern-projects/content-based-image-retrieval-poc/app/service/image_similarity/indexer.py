import faiss
import app
from app.service.helper.generate_feature_vectors import FeatureExtraction
from app.database.helper import DatabaseHelper
from app.constant import SAVED_INDEX_FOLDER, DIMENSION
import numpy as np


class Indexer:
    def __init__(self):
        self.vector_generator = FeatureExtraction()
        self.db_helper = DatabaseHelper()

        try:
            self.faiss_index = faiss.read_index(SAVED_INDEX_FOLDER + '/file.index')
        except Exception:
            app.logger.info("Creating Faiss index")
            self.faiss_index = faiss.IndexFlatIP(DIMENSION)

    def indexing(self, files):
        vectors = self.vector_generator.getvectors(files)

        # find vectors which are not present in index
        not_present_vectors, ids = self.db_helper.vector_already_present(vectors)

        if not_present_vectors:
            numpy_vectors = np.array(not_present_vectors, dtype='float32')  # converting vector to 'float32' datatype

            faiss.normalize_L2(numpy_vectors)  # normalizing vectors
            if not self.faiss_index.is_trained:
                self.faiss_index.train(numpy_vectors)  # training faiss index
            self.faiss_index.add(numpy_vectors)  # adding vectors to faiss index
            faiss.write_index(self.faiss_index, SAVED_INDEX_FOLDER+'/file.index')  # saving faiss index to storage

            self.db_helper.store_vectors(files, vectors, ids)  # storing vectors to database



