import faiss
import numpy as np
import app
from app.service.helper.generate_feature_vectors import FeatureExtraction
from app.constant import SAVED_INDEX_FOLDER
from app.database.helper import DatabaseHelper
from app.constant import NO_OF_NEIGHBORS, DISTANCE_THRESHOLD
from app.service.image_similarity.indexer import Indexer


class Searcher:
    def __init__(self):
        self.vector_generator = FeatureExtraction()
        self.db_helper = DatabaseHelper()
        self.indexer = Indexer()

        # read index if available else give error message
        try:
            self.faiss_index = faiss.read_index(SAVED_INDEX_FOLDER + '/file.index')
        except Exception as e:
            app.logger.warning("Error in loading index", e)
            return

    def searching(self, file_path):
        vector = self.vector_generator.getvectors(file_path)  # generating vector
        numpy_vector = np.array(vector, dtype='float32')
        faiss.normalize_L2(numpy_vector)  # normalizing vectors

        _, distances, indexes = self.faiss_index.range_search(numpy_vector, DISTANCE_THRESHOLD)

        # sorting indexes by distance
        similar_indexes = [indexes[list(distances).index(i)] for i in sorted(distances, reverse=True)]

        self.indexer.indexing(file_path)  # adding search image to faiss index

        return self.db_helper.get_imagename_by_id(similar_indexes)  # returning imagenames by using indexes
