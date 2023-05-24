from env import myEnv

env = myEnv()
state_number = env.observation_space.shape[0]
action_number = env.action_space.shape[0]
max_action = env.action_space.high[0]
min_action = env.action_space.low[0]
max_action_1 = env.action_space.high[1]
min_action_1 = env.action_space.low[1]

Switch = 0
GAMMA = 0.9
BATCH = 2

EP_MAX = 1000
EP_LEN = 8

A_LR = 0.0001
C_LR = 0.0003

A_UPDATE_STEPS = 3
C_UPDATE_STEPS = 3

METHOD = [
    dict(name='kl_pen', kl_target=0.01, lam=0.5),  # KL penalty
    dict(name='clip', epsilon=0.2),  # Clipped surrogate objective, find this is better
][1]  # choose the method for optimization
