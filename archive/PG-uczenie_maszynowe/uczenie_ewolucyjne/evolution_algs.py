import numpy as np
import random

def get_random_vector_indices( vec, count=2 ):
    idx = range( len( vec ) )
    return random.sample( idx, count )

def get_random_vector_items( vec, count=2 ):
    return [ vec[ i ] for i in get_random_vector_indices( vec, count ) ]

def randomize_2_vectors( vec1, vec2 ):
    if np.random.random() < 0.5:
        return (vec1, vec2)
    else:
        return (vec2, vec1)


# #
# Simple vectors crossover

def crossover_vectors( vec1, vec2, pivot ):
    cross_variant = np.random.random()

    if cross_variant < 0.5:
        slice_a = slice( None, pivot )
        slice_b = slice( pivot, None )
    else:
        slice_a = slice( pivot, None )
        slice_b = slice( None, pivot )

    return (
        np.concatenate( (vec1[ slice_a ], vec2[ slice_b ]) ),
        np.concatenate( (vec2[ slice_a ], vec1[ slice_b ]) ),
    )

def rand_crossover_vectors( vec1, vec2 ):
    pivot = np.random.randint( 0, len( vec1 ) - 1 )
    child_a, child_b = randomize_2_vectors( vec1, vec2 )
    return crossover_vectors( child_a, child_b, pivot )


# #
# Crossover vectors slice

def crossover_vectors_slice( vec1, vec2, pivot_from, pivot_to ):
    return (
        np.concatenate( (vec1[ :pivot_from ], vec2[ pivot_from:pivot_to ], vec1[ pivot_to: ]) ),
        np.concatenate( (vec2[ :pivot_from ], vec1[ pivot_from:pivot_to ], vec2[ pivot_to: ]) ),
    )

def rand_crossover_vectors_slice( vec1, vec2 ):
    pivot_from = np.random.randint( 0, len( vec1 ) - 2 )
    pivot_to = np.random.randint( pivot_from, len( vec1 ) -1 )
    child_a, child_b = randomize_2_vectors( vec1, vec2 )

    return crossover_vectors_slice( child_a, child_b, pivot_from, pivot_to )


# #
# Swap items

def swap_vector_items( vec, index_a, index_b ):
    vec[index_a], vec[index_b] = vec[index_b], vec[index_a]
    return vec

def rand_swap_vector_items( vec ):
    idx = range( len( vec ) )
    i1, i2 = random.sample(idx, 2)
    return swap_vector_items( vec, i1, i2 )


# #
# Mutations

def mutate_vector( vec, min, max ):
    i = np.random.randint( 0, len( vec ) - 1 )
    # print( f"Before {vec} {i=}" )
    vec[ i ] = np.random.randint( min, max )
    # print( f" After {vec}" )
    return vec

def shuffle_vector( vec ):
    np.random.shuffle( vec )
    return vec