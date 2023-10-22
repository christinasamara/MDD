import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer

def lsh(df):
    tfidf = TfidfVectorizer(
        analyzer='char_wb',
        ngram_range=(1, 3),
        min_df=0,
        stop_words='english')
    X_tfidf = tfidf.fit_transform(df['EDUCATION'])
    #print(tfidf.get_feature_names_out())

    def get_similarity_items(X_tfidf, item_id, topn=5):
        query = X_tfidf[item_id]
        scores = X_tfidf.dot(query.T).toarray().ravel()
        best = np.argpartition(scores, -topn)[-topn:]
        return sorted(zip(best, scores[best]), key=lambda x: -x[1])


    def generate_random_vectors(dim, n_vectors):
        return np.random.randn(dim, n_vectors)

    vocab_size = len(tfidf.get_feature_names_out())


    np.random.seed(0)
    n_vectors = 16
    random_vectors = generate_random_vectors(vocab_size, n_vectors)

    powers_of_two = 1 << np.arange(n_vectors - 1, -1, step=-1)
    bin_indices_bits = X_tfidf.dot(random_vectors) >= 0
    bin_indices = bin_indices_bits.dot(powers_of_two)

    from collections import defaultdict


    def train_lsh(X_tfidf, n_vectors, seed=None):    
        if seed is not None:
            np.random.seed(seed)

        dim = X_tfidf.shape[1]
        random_vectors = generate_random_vectors(dim, n_vectors)  

        # partition data points into bins,
        # and encode bin index bits into integers
        bin_indices_bits = X_tfidf.dot(random_vectors) >= 0
        powers_of_two = 1 << np.arange(n_vectors - 1, -1, step=-1)
        bin_indices = bin_indices_bits.dot(powers_of_two)

        # update `table` so that `table[i]` is the list of document ids with bin index equal to i
        table = defaultdict(list)
        for idx, bin_index in enumerate(bin_indices):
            table[bin_index].append(idx)
        
        # note that we're storing the bin_indices here
        # so we can do some ad-hoc checking with it,
        # this isn't actually required
        model = {'table': table,
                'random_vectors': random_vectors,
                'bin_indices': bin_indices,
                'bin_indices_bits': bin_indices_bits}
        return model


    # train the model
    n_vectors = 16
    model = train_lsh(X_tfidf, n_vectors, seed=143)


    from itertools import combinations


    def search_nearby_bins(query_bin_bits, table, search_radius=3, candidate_set=None):
      
        if candidate_set is None:
            candidate_set = set()

        n_vectors = query_bin_bits.shape[0]
        powers_of_two = 1 << np.arange(n_vectors - 1, -1, step=-1)

        for different_bits in combinations(range(n_vectors), search_radius):
            # flip the bits (n_1, n_2, ..., n_r) of the query bin to produce a new bit vector
            index = list(different_bits)
            alternate_bits = query_bin_bits.copy()
            alternate_bits[index] = np.logical_not(alternate_bits[index])

            # convert the new bit vector to an integer index
            nearby_bin = alternate_bits.dot(powers_of_two)

            # fetch the list of documents belonging to
            # the bin indexed by the new bit vector,
            # then add those documents to candidate_set;
            # make sure that the bin exists in the table
            if nearby_bin in table:
                candidate_set.update(table[nearby_bin])

        return candidate_set
    from sklearn.metrics.pairwise import pairwise_distances


    def get_nearest_neighbors(X_tfidf, query_vector, model, max_search_radius=3):
        table = model['table']
        random_vectors = model['random_vectors']

        # compute bin index for the query vector, in bit representation.
        bin_index_bits = np.ravel(query_vector.dot(random_vectors) >= 0)

        # search nearby bins and collect candidates
        candidate_set = set()
        for search_radius in range(max_search_radius + 1):
            candidate_set = search_nearby_bins(bin_index_bits, table, search_radius, candidate_set)

        # sort candidates by their true distances from the query
        candidate_list = list(candidate_set)
        candidates = X_tfidf[candidate_list]
        distance = pairwise_distances(candidates, query_vector, metric='cosine').flatten()
        
        distance_col = 'distance'
        nearest_neighbors = pd.DataFrame({
            'id': candidate_list, distance_col: distance
        }).sort_values(distance_col).reset_index(drop=True)
        test = nearest_neighbors.loc[nearest_neighbors['distance'] <0.6]
        return test

    #print('original similar items:\n' + str(similar_items))
    def stringQuery(question):
        query = tfidf.transform(([question]))
        return query
    item_id = 2

    print('Enter your query:')
    query = input()
    query_vector = stringQuery(query)
    #query_vector = X_tfidf[item_id]
    nearest_neighbors = get_nearest_neighbors(X_tfidf, query_vector, model, max_search_radius=5)

    print(pd.merge(nearest_neighbors,df,left_on="id",right_index=True))
