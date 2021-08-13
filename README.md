

# TUSBF: An UltralTool for data collecting via UDP/TCP/SerialPort/Bluetooth/TestFile



## Introduction

Hello every, this is DrWiki.

I developed a easy-used tool for collecting data via WIFI-UDP/WIFI-TCP/Serial Port/Bluetooth/Test File.

Actually, it's based on pyQt5 and is a improved Qwidget from QGroupBox class. And thanks a lot to XXXXX who has released an awsome UDP/TCP demo on github, which also is the most important material That I learned from. 

 Here is the relationships between all the Qt and custom class that is involved. It's edited using UML.  By the way, UML  is a good tool to show that  but it's not convenient enough and I am still looking for a better one.

<img src="C:\Users\SongZiwu\AppData\Roaming\Typora\typora-user-images\image-20210706132351290.png" alt="image-20210706132351290"  />





## 1. How to use

import numpy as np
import gym
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
# from torch.distributions import Normal

# import matplotlib

import matplotlib.pyplot as plt


# class State:
#     def __init__(self):
#         self.x = 0

class Env:
    def __init__(self):
        # # state参数范围设置
        # self.theta_high = 2 * np.pi
        # self.theta_low = 0
        # self.theta_dot_high = 8.0
        # self.theta_dot_low = -8.0
        #
        # # 参数预设省的下面有波浪线
        # self.theta = 0
        # self.theta_dot = 0
        # self.u = None
        # self.done = False
        #
        # # action范围设置
        # self.u_high = 2.0
        # self.u_low = -2.0
        #
        # # 仿真参数设置
        # self.g = 10.0
        # self.dt = 0.05  # 仿真步长
        # self.m = 1  # 质量
        # self.l = 1  # 长度
        #
        # # reward权重参数
        # self.w1 = 1
        # self.w2 = 0.1
        # self.w3 = 0.001
        #
        # # 初始化状态
        # self.reset()

        # 随机位置
        # def reset(self):
        #     self.theta = np.random.uniform(self.theta_low, self.theta_high)
        #     self.theta_dot = np.random.uniform(self.theta_dot_low, self.theta_dot_high)
        #     self.u = None
        #     return np.array([self.theta, self.theta_dot])
        # self.action=[(0:9:36) * pi / 18]
        # self.action=np.zeros(2)
        self.NextObs = np.zeros(3)
        self.reward = 0
        self.isout = 0
        self.state = np.zeros(5)

    def reset(self):
        self.state[0] = 0
        self.state[1] = 0
        self.state[2] = 0
        self.state[3] = 12
        self.state[4] = 0.02
        y = 0

        return self.state

    def Isout(self):

        x = self.state[0]
        y = self.state[1]

        isout = y < 0 or (abs(x) > 1.5) * ((y >= 0 and y <= 6) or (y > 44 and y <= 50)) or (x < -1.5 or x > 5.5) * (
                    (y > 6 and y <= 19.5) or y > 30.5 and y <= 44) or (x < 2.5 or x > 5.5) * (y > 19.5 and y <= 30.5)
        return isout

    def Reward(self):
        x = self.state[0]
        y = self.state[1]
        vx = self.state[2]
        vy = self.state[3]
        t = self.state[4]

        self.isout = self.Isout()
        if not self.isout:
            self.reward = y / t + 0.5 * y - x * x * ((y > 0 and y < 6) or (y > 30.5 and y < 50)) - 10 * (
                        (x - 4) * (x - 4)) * (y >= 6 and y <= 30.5)
        else:
            self.reward = -5000
            print("0ut，time=")
            print(t)

        if y >= 50:
            self.reward = 5000

            print("Finish！！！time=")
            print(t)
        return self.reward

    def step(self, Action, way_x, way_y):
        # 初始化运算参数
        self.done = False
        # 获取k时间状态
        x = self.state[0]
        y = self.state[1]
        vx = self.state[2]
        vy = self.state[3]
        t = self.state[4]
        ts = 0.02
        self.reward = self.Reward()
        way_x.append(x)
        way_y.append(y)
        # plt.scatter(x, y, color='blue', marker='o')
        # 计算reward
        # reward = self.Reward()
        theta = Action[0, 0]
        a = Action[0, 1]

        ax = a * np.cos(theta.cpu().detach().numpy())
        ax = ax.cpu().detach().numpy()
        ay = a * np.sin(theta.cpu().detach().numpy())
        ay = ay.cpu().detach().numpy()

        self.state = self.state + ts * np.array([vx, vy, ax, ay, 1])

        x = self.NextObs[0]
        y = self.NextObs[1]
        vx = self.NextObs[2]
        # f0 = self.m * self.g * np.cos(theta) / theta
        self.done = self.Isout()

        return self.state, self.reward, self.done, y


use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")


class ValueNetwork(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_size, init_w=3e-3):
        super(ValueNetwork, self).__init__()

        self.linear1 = nn.Linear(num_inputs + num_actions, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, 2)

        self.linear3.weight.data.uniform_(-init_w, init_w)
        self.linear3.bias.data.uniform_(-init_w, init_w)

    def forward(self, state, act):
        # print(state.shape)
        # print(act.shape)
        x = torch.cat((state, act), 1)
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x


class PolicyNetwork(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_size, init_w=3e-3):
        super(PolicyNetwork, self).__init__()

        self.linear1 = nn.Linear(num_inputs, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, num_actions)

        # uniform_将tensor用从均匀分布中抽样得到的值填充。参数初始化
        self.linear3.weight.data.uniform_(-init_w, init_w)
        # 也用用normal_(0, 0.1) 来初始化的，高斯分布中抽样填充，这两种都是比较有效的初始化方式
        self.linear3.bias.data.uniform_(-init_w, init_w)
        # 其意义在于我们尽可能保持 每个神经元的输入和输出的方差一致。
        # 使用 RELU（without BN） 激活函数时，最好选用 He 初始化方法，将参数初始化为服从高斯分布或者均匀分布的较小随机数
        # 使用 BN 时，减少了网络对参数初始值尺度的依赖，此时使用较小的标准差(eg：0.01)进行初始化即可

        # 但是注意DRL中不建议使用BN

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = F.tanh(self.linear3(x))
        return x

    def get_action(self, state):
        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        action = self.forward(state)
        return action



# class OUNoise(object):
#     def __init__(self, action_space, mu=0.0, theta = 0.15, max_sigma = 0.3, min_sigma = 0.3, decay_period = 100000):#decay_period要根据迭代次数合理设置
#         self.mu = mu
#         self.theta = theta
#         self.sigma = max_sigma
#         self.max_sigma = max_sigma
#         self.min_sigma = min_sigma
#         self.decay_period = decay_period
#         self.action_dim = action_space.shape[0]
#         self.low = action_space.low
#         self.high = action_space.high
#         self.reset()
#
#     def reset(self):
#         self.state = np.ones(self.action_dim) *self.mu
#
#     def evolve_state(self):
#         x = self.state
#         dx = self.theta* (self.mu - x) + self.sigma * np.random.randn(self.action_dim)
#         self.state = x + dx
#         return self.state
#
#     def get_action(self, action, t=0):
#         ou_state = self.evolve_state()
#         self.sigma = self.max_sigma - (self.max_sigma - self.min_sigma) * min(1.0, t / self.decay_period)
#         return np.clip(action + ou_state, self.low, self.high)


class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def push(self, state, action_, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action_.cpu().detach().numpy(), reward, next_state, done)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        temp = zip(*batch)
        state, action, reward, next_state, done = map(np.stack, temp)
        # print(action.shape)
        return state, action, reward, next_state, done

    def __len__(self):
        return len(self.buffer)


class NormalizedActions(gym.ActionWrapper):

    def action(self, action):
        low_bound = 0
        upper_bound = 1

        action = action * 2 * 3.14159
        # 将经过tanh输出的值重新映射回环境的真实值内
        action = np.clip(action, low_bound, upper_bound)

        return action

    def reverse_action(self, action):
        low_bound = self.action_space.low
        upper_bound = self.action_space.high

        # 因为激活函数使用的是tanh，这里将环境输出的动作正则化到（-1，1）

        action = 2 * (action - low_bound) / (upper_bound - low_bound) - 1
        action = np.clip(action, low_bound, upper_bound)

        return action


def plot(frame_idx, rewards):
    plt.figure(figsize=(20, 5))
    # plt.subplot(131)
    plt.title('episode %s. reward: %s' % (frame_idx, rewards[-1]))
    # print("rewards", rewards)
    plt.plot(rewards)
    plt.show()


class DDPG(object):
    def __init__(self, action_dim, state_dim, hidden_dim):
        super(DDPG, self).__init__()
        self.action_dim, self.state_dim, self.hidden_dim = action_dim, state_dim, hidden_dim
        self.batch_size = 128
        self.gamma = 0.99
        self.min_value = -np.inf
        self.max_value = np.inf
        self.soft_tau = 1e-2
        self.replay_buffer_size = 5000
        self.value_lr = 1e-3
        self.policy_lr = 1e-4

        self.value_net = ValueNetwork(state_dim, action_dim, hidden_dim).to(device)
        # value_net = torch.load(PATH)
        self.policy_net = PolicyNetwork(state_dim, action_dim, hidden_dim).to(device)

        self.target_value_net = ValueNetwork(state_dim, action_dim, hidden_dim).to(device)
        self.target_policy_net = PolicyNetwork(state_dim, action_dim, hidden_dim).to(device)

        for target_param, param in zip(self.target_value_net.parameters(), self.value_net.parameters()):
            target_param.data.copy_(param.data)

        for target_param, param in zip(self.target_policy_net.parameters(), self.policy_net.parameters()):
            target_param.data.copy_(param.data)

        self.value_optimizer = optim.Adam(self.value_net.parameters(), lr=self.value_lr)
        self.policy_optimizer = optim.Adam(self.policy_net.parameters(), lr=self.policy_lr)

        self.value_criterion = nn.MSELoss()

        self.replay_buffer = ReplayBuffer(self.replay_buffer_size)

    def ddpg_update(self):
        state, action, reward, next_state, done = self.replay_buffer.sample(self.batch_size)
        # action_temp = np.reshape(action,(128,2))
        action = np.squeeze(action)

        state = torch.FloatTensor(state).to(device)
        next_state = torch.FloatTensor(next_state).to(device)
        action = torch.FloatTensor(action).to(device)

        reward = torch.FloatTensor(reward).unsqueeze(1).to(device)
        done = torch.FloatTensor(np.float32(done)).unsqueeze(1).to(device)

        policy_loss = self.value_net(state, self.policy_net(state))
        policy_loss = -policy_loss.mean()

        next_action = self.target_policy_net(next_state)
        target_value = self.target_value_net(next_state, next_action.detach())
        expected_value = reward + (1.0 - done) * self.gamma * target_value
        expected_value = torch.clamp(expected_value, self.min_value, self.max_value)

        value = self.value_net(state, action)
        value_loss = self.value_criterion(value, expected_value.detach())

        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        self.policy_optimizer.step()

        self.value_optimizer.zero_grad()
        value_loss.backward()
        self.value_optimizer.step()

        for target_param, param in zip(self.target_value_net.parameters(), self.value_net.parameters()):
            target_param.data.copy_(
                target_param.data * (1.0 - self.soft_tau) + param.data * self.soft_tau
            )

        for target_param, param in zip(self.target_policy_net.parameters(), self.policy_net.parameters()):
            target_param.data.copy_(
                target_param.data * (1.0 - self.soft_tau) + param.data * self.soft_tau
            )


def road():
    y_ = 0
    plt.figure(figsize=(5, 20))
    while y_ < 50.5:
        x1 = 1.5 * ((y_ >= 0 and y_ <= 6) or (y_ >= 44 and y_ <= 50)) + 5.5 * (y_ > 6 and y_ < 44)
        x2 = -1.5 * ((y_ >= 0 and y_ <= 19.5) or (y_ >= 30.5 and y_ <= 50)) + 2.5 * (y_ > 19.5 and y_ < 30.5)
        plt.scatter(x1, y_, color='red', marker='x', )
        plt.scatter(x2, y_, color='red', marker='x', )
        y_ += 0.5


def main():
    # env = gym.make("Pendulum-v0")
    # env = NormalizedActions(env)

    # ou_noise = OUNoise(env.action_space)

    state_dim = 5
    action_dim = 2
    hidden_dim = 256

    ddpg = DDPG(action_dim, state_dim, hidden_dim)

    max_frames = 120000
    max_steps = 500
    frame_idx = 0
    # rewards = []
    batch_size = 128
    env = Env()
    rewards = []
    bestway_x = []
    bestway_y = []
    bestreward = -100000
    best_y = 0
    while frame_idx < max_frames:
        state = env.reset()
        # ou_noise.reset()
        episode_reward = 0
        way_x = []
        way_y = []
        y = 0
        for step in range(max_steps):
            action = ddpg.policy_net.get_action(state)
            action[0, 0] *=6
            action[0, 1] *= 2*3.14159


            # if action[0,0]<0:
            #     action[0,0]=0
            # else:
            #     if action[0,0]>2*3.14159:
            #         action[0,0]=2*3.14159
            #
            # if action[0,1]<0:
            #     action[0,1]=0
            # else:
            #     if action[0,1]>6:
            #         action[0,1]=6
            #action = ou_noise.get_action(action, step)
            print(action)
            next_state, reward, done, y = env.step(action, way_x, way_y)

            ddpg.replay_buffer.push(state, action, reward, next_state, done)
            if len(ddpg.replay_buffer) > batch_size:
                ddpg.ddpg_update()

            state = next_state
            episode_reward += env.Reward()

            if done:
                break

        rewards.append(episode_reward)
        plot(frame_idx, rewards)
        if episode_reward > bestreward:

            road()

            plt.axis("equal")
            plt.ylim(0, 50)
            plt.xlim(-2, 6)
            bestway_x = way_x
            bestway_y = way_y
            bestreward = episode_reward
            plt.title('bestway(R) y= %d., R= %d' % (y, episode_reward))
            plt.plot(bestway_x, bestway_y, color='blue', marker='o')
            plt.show()

        else:
            if y > best_y:
                road()

                plt.axis("equal")
                plt.ylim(0, 50)
                plt.xlim(-2, 6)
                best_y = y
                bestway_x = way_x
                bestway_y = way_y
                plt.title('bestway(y) y= %d, R= %d' % (y, episode_reward))
                plt.plot(bestway_x, bestway_y, color='blue', marker='o')
                plt.show()
        frame_idx += 1
        # rewards.append(episode_reward)
        print(episode_reward)
    # env.close()


if __name__ == '__main__':
    main()
