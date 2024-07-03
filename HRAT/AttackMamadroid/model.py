import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class Net(nn.Module):
    def __init__(self, states_dim, actions_num):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(states_dim, 50)
        self.fc1.weight.data.normal_(0, 0.1)  # initialization
        self.out = nn.Linear(50, actions_num)
        self.out.weight.data.normal_(0, 0.1)  # initialization

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        actions_value = self.out(x)
        return actions_value


class DQN(object):
    """
    Description:

    Source:
        Self designed. This environments is designed to modify function call graph in programming.

    Observations:
        Type: vector:
            the centrality of sensitive apis (attention nodes)

    Actions:
        Type: list(4)
        Num     Action
        0       add an edge between two nodes
        1       rewiring
        2       add an nodes, and connect it to another nodes
        3       delete an nodes


    Reward:
        Reward is


    Episode Termination:
        The observation is classified as target class.
        Episode length is greater than 200.

    """

    def __init__(self, states_dim, actions_num, memory_capacity, learning_rate, ):

        self.eval_net, self.target_net = Net(states_dim, actions_num), Net(states_dim, actions_num)
        self.learn_step_counter = 0
        self.action_space = ['add_edge', 'rewiring', 'add_nodes', 'delete_nodes']
        self.memory_counter = 0  # for storing memory
        self.memory = np.zeros((memory_capacity, states_dim * 2 + 5))  # initialize memory
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=learning_rate)
        self.loss_func = nn.MSELoss()

    def choose_action(self, x, actions_num, EPSILON=0.9):
        # x = torch.unsqueeze(torch.FloatTensor(x), 0)
        x = torch.unsqueeze(x.float(), 0).to(device)
        # input only one sample
        if np.random.uniform() < EPSILON:
            action_type = self.eval_net.forward(x)
            action_type = torch.max(action_type, 1)[1].data.numpy()
        else:  # random
            action = np.random.randint(actions_num)
            action_type = action

        return action_type

    def store_transition(self, s, a, r, s_, memory_capacity):
        r = np.array(r)
        transition = np.hstack((s.cpu(), a, r, s_.cpu()))
        # replace the old memory with new memory
        index = self.memory_counter % memory_capacity
        self.memory[index, :] = transition
        self.memory_counter += 1

    def learn(self, MEMORY_CAPACITY, BATCH_SIZE, N_STATES, TARGET_REPLACE_ITER=100, GAMMA=0.9):
        # target parameter update
        if self.learn_step_counter % TARGET_REPLACE_ITER == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
        self.learn_step_counter += 1

        # sample batch transitions
        sample_index = np.random.choice(MEMORY_CAPACITY, BATCH_SIZE)
        b_memory = self.memory[sample_index, :]
        b_state = torch.FloatTensor(b_memory[:, :N_STATES])  # N_States : state dimension = degree dimension
        b_action = torch.LongTensor(b_memory[:, N_STATES:N_STATES + 1].astype(int))  # action dimension: 4 []
        b_reward = torch.FloatTensor(b_memory[:, N_STATES + 4:N_STATES + 5])
        b_state_new = torch.FloatTensor(b_memory[:, -N_STATES:])

        # q_eval w.r.t the action in experience
        q_eval = self.eval_net(b_state).gather(1, b_action)  # shape (batch, 1)
        q_next = self.target_net(b_state_new).detach()  # detach from graph, don't backpropagate
        q_target = b_reward + GAMMA * q_next.max(1)[0].view(BATCH_SIZE, 1)  # shape (batch, 1)
        loss = self.loss_func(q_eval, q_target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
