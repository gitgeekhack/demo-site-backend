from .connection_manager import DatabaseConnection
import json


class DatabaseHelper:
    def __init__(self):
        self.db_connector = DatabaseConnection()

    def vector_already_present(self, vectors):
        """
        Checking vector already present or not
        Parameters:
            vectors <list>: list of all vectors to search
        Returns:
            not_present <list>: list of vectors which are not present in database
            ids <list>: id of all vectors which are not present in database
        """
        es = self.db_connector.connect()

        # list to store not present vectors and its respective ids
        not_present, ids = [], []

        for index, vector in enumerate(vectors):
            str1 = '{"query": {"bool": {"must": ['
            for i in vector:
                str1 += '{{"match": {{"vector": {id} }}}},'.format(id=i)
            str2 = ']}}}'

            final_str = str1[:-1] + str2  # final query string

            query_string = json.loads(final_str)
            response = es.search(index="vector_mapping", body=query_string)

            if response['hits']['max_score']:
                if int(response['hits']['max_score']) != 1792:
                    not_present.append(vector)
                    ids.append(index)
            else:
                not_present.append(vector)
                ids.append(index)

        self.db_connector.close(es)

        return not_present, ids

    def get_imagename_by_id(self, ids):
        """
        get image names using ids
        Parameters:
            ids <list>: list of ids
        Returns:
            imagenames <list>: list of imagenames respective to ids
        """
        es = self.db_connector.connect()

        imagenames = []
        for i in ids:
            if i != -1:
                response = es.get(index="vector_mapping", id=i)
                imagenames.append(response['_source']['imagename'])

        self.db_connector.close(es)

        return imagenames

    def store_vectors(self, files, vectors, ids):
        """
        store vectors to database
        Parameters:
            files <list>: list of all filenames
            vectors <list>: list of all vectors
            ids <list>: list of ids
        """
        es = self.db_connector.connect()

        total_indexed = es.count(index="vector_mapping")['count']

        for id in ids:
            doc = {
                "imagename": files[id],
                "vector": vectors[id]
            }
            es.index(index="vector_mapping", document=doc, id=total_indexed+ids.index(id))

        self.db_connector.close(es)


