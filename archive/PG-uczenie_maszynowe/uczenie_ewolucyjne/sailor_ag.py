"""
    Genetic algoritm for sailor problem.
    Sailor sails from left to right side of the map bypassing dangerous places (with negative rewards).
    The environment is nondeterministic due to the wind and waves which means that the boat moves to chosen
    places only with constant probabilities. If you want to evaluate sailor's strategy in the reliable way,
    you need to use many episodes for strategy evaluation.

    In this task you need to invent crossover and mutation operations, invent the evaluation method, choose
    the best parameters values of the evolution, maybe add more parameters and operations. Your solutions
    should work for different maps and different gamma values.
"""
import time
import random
import math
import os
import pdb
import numpy as np
import matplotlib.pyplot as plt
import evolution_algs as ealgs
import sailor_funct as sf


# Evolution parameters ..... (find the best values)
# number_of_epochs = 20                      # number fo epochs of evolution
# number_of_individuals = 10                 # number of individuals in population (each individual conatains sailor strategy)
# number_of_episodes_for_eval = 5            # number of epizodes for strategy evaluation
number_of_epochs = 75                      # number fo epochs of evolution
number_of_individuals = 40                 # number of individuals in population (each individual conatains sailor strategy)
number_of_episodes_for_eval = 75          # number of epizodes for strategy evaluation
p_cross = 0.4                              # crossover probability
p_mut = 0.2                                # mutation probability
selection_pressure = 3                   # if higher -> more copies of the best individuals in new population expense of worst individuals
best_to_next_gen = 5

# Task definition parameters ............ (begin from small one, and try big one later)
# file_name = 'map_small.txt'
# file_name = 'map_easy.txt'
file_name = 'map_middle.txt'
# file_name = 'map_big.txt'
# file_name = 'map_spiral.txt'
gamma = 0.9999                                 # discount factor (part of a task). If gamma < 1, rewards with longer time distance are less important
                                            # (it pays an agent to get positive rewards as soon as possible and penalties as long as possible)


stored_means = []

reward_map = sf.load_data(file_name)                 # load map of rewards from file
num_of_rows, num_of_columns = reward_map.shape
used_p_cross = p_cross
used_p_mut = p_mut

num_of_steps_max = int(2.5*(num_of_rows + num_of_columns))    # maximum number of steps in an episode
Popul = np.random.randint(1,5,(number_of_individuals, num_of_rows, num_of_columns))  # population of strategies

print('Initial population = ' + str(Popul))


def reproduction(Popul,fitnesses):      # new population based on fittness values
#    print( f"{fitnesses=}" )

    fit_cum = np.copy(fitnesses)
    for i in range(fitnesses.size-1):    # cumulative sum
        fit_cum[i+1] += fit_cum[i]

    max_cum_value = fit_cum[fitnesses.size-1]
    Popul_new = np.copy(Popul)

    for i in range(fitnesses.size):
        rand_value = np.random.random() * max_cum_value

        for j in range(fit_cum.size):
            prev_val = 0
            if j>0:
                prev_val = fit_cum[j-1]
            if (rand_value > prev_val) & (rand_value <= fit_cum[j]):
                parent_index = j
                break
        Popul_new[i,...] = np.copy(Popul[j,...])

    sorted_fitness_indices = np.argsort( fitnesses )[::-1]
    best_popul = Popul[sorted_fitness_indices[ :best_to_next_gen ]]
    Popul_new[ :best_to_next_gen ] = best_popul

    # print( f"{best_popul}" )

    return Popul_new
# end of reproduction

maximum_mean_sum_of_rewards = -1000000000


for epoch in range(number_of_epochs):
    # evaluation of individuals:
    mean_sums_of_rewards = np.zeros([number_of_individuals])
    minimum_mean_sum_of_rewords = 1000000000
    fitnesses = np.zeros([number_of_individuals])
    for individual in range(number_of_individuals):
        mean_sums_of_rewards[individual] = sf.sailor_test(reward_map, Popul[individual,...],number_of_episodes_for_eval,gamma)
        if minimum_mean_sum_of_rewords > mean_sums_of_rewards[individual]:
            minimum_mean_sum_of_rewords = mean_sums_of_rewards[individual]
        if maximum_mean_sum_of_rewards < mean_sums_of_rewards[individual]:
            maximum_mean_sum_of_rewards = mean_sums_of_rewards[individual]
            best_strategy = Popul[individual,...]
            print('new record = ' + str(maximum_mean_sum_of_rewards) + ' in epoch ' + str(epoch))

    # Fittness values must be >= 0 and higher as individual better. You can use selection_factor as an exponent of
    # mean_sums_of_rewards to adjust selection pressure - expected number of copies of the best individuals against the
    # existence of the worst.
    for individual in range(number_of_individuals):
        fitnesses[individual] = sf.sailor_test(reward_map, Popul[individual,...],number_of_episodes_for_eval,gamma)

    fitness_len = len( fitnesses )
    min_fitness = np.min( fitnesses )
    max_fitness = np.max( fitnesses )
    # normalized_fitnesses = np.exp( selection_pressure * (fitnesses - max_fitness) / (max_fitness - min_fitness) )
    normalized_fitnesses = np.zeros( fitness_len )

    for i in range( fitness_len ):
        normalized_fitnesses[ i ] = np.exp( (fitnesses[ i ] - min_fitness) * selection_pressure )

    # print( f"{normalized_fitnesses}")
    stored_means.append( np.mean(mean_sums_of_rewards) )
    print('epoch = ' + str(epoch) + ' mean sum of rewards over population = ' + str(stored_means[ -1 ]))
    if len( stored_means ) > 10: stored_means = stored_means[ -10: ]

    diff = np.diff( stored_means[ -3: ] )
    change_p = max( 0, 0.3 - sum( diff ) ) if len( stored_means ) > 3 else 0
    help_cross = False
    help_mutation = False

    if change_p < 0.05:
        used_p_cross = p_cross * 3
        used_p_mut = p_mut * 3
    if change_p < 0.1:
        used_p_cross = p_cross * 2
        used_p_mut = p_mut * 2
    else:
        used_p_cross = p_cross
        used_p_mut = p_mut

    # Reproduction ...... can be rank or roulette version
    Popul = reproduction(Popul,normalized_fitnesses)    # roulette version

    # Crossover .......
    for i, individual in enumerate( Popul ):
        if random.random() < used_p_cross:
            another_individual = random.choice( Popul )

            fet1 = random.choice( individual )
            fet2 = random.choice( another_individual )

            if random.random() < change_p:
                help_cross = True
                # print(f" - Helping individual cross; {mutation_p=}")

                if change_p < 0.05:
                    ealgs.rand_crossover_vectors_slice( fet1, fet2 )
                    ealgs.rand_crossover_vectors_slice( fet1, fet2 )
                elif random.random() < 0.5: ealgs.rand_crossover_vectors( fet1, fet2 )
                else: ealgs.rand_crossover_vectors_slice( fet1, fet2 )

            if random.random() < 0.25:
                ealgs.rand_crossover_vectors_slice( fet1, fet2 )
                ealgs.rand_crossover_vectors_slice( fet1, fet2 )
            elif random.random() < 0.25: ealgs.rand_crossover_vectors_slice( fet1, fet2 )
            elif random.random() < 0.5: ealgs.rand_swap_vector_items( fet1 )
            else: ealgs.rand_crossover_vectors( fet1, fet2 )



    # Mutation .......
    for i, individual in enumerate( Popul ):
        if random.random() < used_p_mut:
            feature = random.choice( individual )

            if random.random() < change_p:
                help_mutation = True
                # print(f" - Helping individual mutation; {mutation_p=}")

                if change_p < 0.05:
                    ealgs.mutate_vector( feature, 1, 4 )
                    ealgs.mutate_vector( feature, 1, 4 )
                elif random.random() < 0.5: ealgs.mutate_vector( feature, 1, 4 )
                else: ealgs.shuffle_vector( feature )

            if random.random() < 0.5:
                ealgs.mutate_vector( feature, 1, 4 )
                ealgs.mutate_vector( feature, 1, 4 )
            elif random.random() < 0.5: ealgs.rand_swap_vector_items( feature )
            elif random.random() < 0.5: ealgs.rand_swap_vector_items( individual )
            elif random.random() < 0.1: ealgs.shuffle_vector( feature )
            elif random.random() < 0.1: ealgs.shuffle_vector( individual )
            else: ealgs.mutate_vector( feature, 1, 4 )

    # Other operations (elitism, niches, parameter changing functions etc.) ...


    if help_cross: print(f" - Helping individual cross; {change_p=}")
    if help_mutation: print(f" - Helping individual mutation; {change_p=}")

# end of evolution loop

mean_sum_of_rewards = sf.sailor_test(reward_map, best_strategy, 1000, gamma)
print('average sum of rewards for best strategy = ' + str(mean_sum_of_rewards))
sf.draw(reward_map,best_strategy)
print('Final population = ' + str(Popul))
