import time
import os
import pdb
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def load_data(file_name):
    file_ptr = open(file_name, 'r').read()
    lines = file_ptr.split('\n')
    number_of_lines = lines.__len__() - 1
    row_values = lines[0].split()
    number_of_values = row_values.__len__()

    number_of_rows = 0
    for i in range(number_of_lines):
        row_values = lines[i].split()
        number_of_values = row_values.__len__()
        if (number_of_values > 0):
            number_of_rows += 1
            num_of_columns = number_of_values

    map_of_rew = np.zeros([number_of_rows, num_of_columns], dtype=float)
    print("examples shape = " + str(map_of_rew.shape))
    
    index = 0
    for i in range(number_of_lines):
        row_values = lines[i].split()
        number_of_values = row_values.__len__()
        if (number_of_values > 0):
            for j in range(number_of_values):
                map_of_rew[index][j] = float(row_values[j])
            index = index + 1

    return map_of_rew

# environment function:  DO NOT CHANGE ANYTHING !
def environment(state, action, reward_map):
    num_of_rows, num_of_columns = reward_map.shape
    prob_side = 0.15
    prob_back = 0.01
    wall_colid_reward = -1.5

    state_new = np.copy(state)
    reward = 0

    los = np.random.random()    # random number from uniform distr. from range (0,1)

    # Action identifiers (1 - right, 2 - up, 3 - left, 4 - bottom): 
    action_exe = -1
    if action == 1:
        if los < prob_back:
            action_exe = 3
        elif los < prob_back + prob_side:
            action_exe = 2
        elif  los < prob_back + 2*prob_side:
            action_exe = 4
        else:
            action_exe = 1
    elif action == 2:
        if los < prob_back:
            action_exe = 4
        elif los < prob_back + prob_side:
            action_exe = 1
        elif  los < prob_back + 2*prob_side:
            action_exe = 3
        else:
            action_exe = 2
    elif action == 3:
        if los < prob_back:
            action_exe = 1
        elif los < prob_back + prob_side:
            action_exe = 2
        elif  los < prob_back + 2*prob_side:
            action_exe = 4
        else:
            action_exe = 3
    elif action == 4:
        if los < prob_back:
            action_exe = 2
        elif los < prob_back + prob_side:
            action_exe = 1
        elif  los < prob_back + 2*prob_side:
            action_exe = 3
        else:
            action_exe = 4

    # Action identifiers (1 - right, 2 - up, 3 - left, 4 - bottom): 
    if action_exe == 1:
        if state[1] < num_of_columns - 1:
            state_new[1] += 1
            reward += reward_map[state_new[0],state_new[1]]
        else:
            reward += wall_colid_reward
    elif  action_exe == 2:
        if state[0] > 0:
            state_new[0] -= 1
            reward += reward_map[state_new[0],state_new[1]]
        else:
            reward += wall_colid_reward
    if action_exe == 3:
        if state[1] > 0:
            state_new[1] -= 1
            reward += reward_map[state_new[0],state_new[1]]
        else:
            reward += wall_colid_reward
    elif  action_exe == 4:
        if state[0] < num_of_rows - 1:
            state_new[0] += 1
            reward += reward_map[state_new[0],state_new[1]]
        else:
            reward += wall_colid_reward

    return state_new, reward

# test for given number of episodes - pure exploitation
def sailor_test(reward_map, strategy, num_of_episodes, gamma):
    num_of_rows, num_of_columns = reward_map.shape
    num_of_steps_max = int(2.5*(num_of_rows + num_of_columns))    # maximum number of steps in an episode
    sum_of_rewards = np.zeros([num_of_episodes], dtype=float)

    for episode in range(num_of_episodes):
        state = np.zeros([2],dtype=int)                            # initial state here [1 1] but rather random due to exploration
        state[0] = np.random.randint(0,num_of_rows)
        the_end = False
        nr_pos = 0
        while the_end == False:
            nr_pos = nr_pos + 1;                            # move number
        
            # Action choosing (1 - right, 2 - up, 3 - left, 4 - bottom): 
            action = strategy[state[0],state[1]]
            state_next, reward  = environment(state, action, reward_map);    
            state = state_next;      # going to the next state
        
            # end of episode if maximum number of steps is reached or last column
            # is reached
            if (nr_pos == num_of_steps_max) | (state[1] >= num_of_columns-1):
                the_end = True;                                  
        
            sum_of_rewards[episode] += reward*(gamma**(nr_pos-1))
    #print('test-'+str(num_of_episodes)+' average sum of rewards = ' + str(np.mean(sum_of_rewards)))
    return np.mean(sum_of_rewards)

# drawing map of rewards and strategy using arrows
def draw(reward_map, strategy):
    num_of_rows, num_of_columns = reward_map.shape
    w = 40
    image_map = np.zeros([num_of_rows*w, num_of_columns*w, 3], dtype=int)
    for i in range(num_of_rows):
        for j in range(num_of_columns):
            for n in range(w):
                for m in range(w):
                    if reward_map[i,j] > 0:
                        image_map[i*w+n,j*w+m,0] = 200
                        image_map[i*w+n,j*w+m,1] = 200
                        image_map[i*w+n,j*w+m,2] = 100
                    elif reward_map[i,j] == 0:
                        image_map[i*w+n,j*w+m,0] = 90
                        image_map[i*w+n,j*w+m,1] = 90
                        image_map[i*w+n,j*w+m,2] = 200
                    elif reward_map[i,j] >= -1:
                        image_map[i*w+n,j*w+m,0] = 40
                        image_map[i*w+n,j*w+m,1] = 40
                        image_map[i*w+n,j*w+m,2] = 110
                    elif reward_map[i,j] >= -5:
                        image_map[i*w+n,j*w+m,0] = 20
                        image_map[i*w+n,j*w+m,1] = 20
                        image_map[i*w+n,j*w+m,2] = 50
                    elif reward_map[i,j] >= -10:
                        image_map[i*w+n,j*w+m,2] = 30
    for i in range(num_of_rows):
        for j in range((num_of_columns)*w):
            for k in range(3):
                image_map[i * w , j, k] = 0
                image_map[i * w + 1, j, k] = 0
    for j in range(num_of_columns):
        for i in range(num_of_rows*w):
            for k in range(3):
                image_map[i, j * w, k] = 0
                image_map[i, j * w + 1, k] = 0
    f = plt.figure()

    # Action identifiers (1 - right, 2 - up, 3 - left, 4 - bottom):
    for i in range(num_of_rows):
        for j in range(num_of_columns-1):
            action = strategy[i,j]
            if action == 1:
                # xytext - starting point, xy - end point
                plt.annotate('', xytext=((j-0.4)*w+w/2, i*w+w/2), xy=((j+0.4)*w+w/2, i*w+w/2),
                    arrowprops=dict(facecolor='red', shrink=0.09),
                    )
            elif action == 2:
                plt.annotate('', xytext=(j*w+w/2, (i+0.4)*w+w/2), xy=(j*w+w/2, (i-0.4)*w+w/2),
                    arrowprops=dict(facecolor='red', shrink=0.09),
                    )
            elif action == 3:
                plt.annotate('',  xytext=((j+0.4)*w+w/2, i*w+w/2),xy=((j-0.4)*w+w/2, i*w+w/2),
                    arrowprops=dict(facecolor='red', shrink=0.09),
                    )
            elif action == 4:
                plt.annotate('',  xytext=(j*w+w/2, (i-0.4)*w+w/2),xy=(j*w+w/2, (i+0.4)*w+w/2),
                    arrowprops=dict(facecolor='red', shrink=0.09),
                    )


    im = plt.imshow(image_map, cmap=plt.get_cmap('plasma'))
    plt.show()
    f.savefig('image.svg')


