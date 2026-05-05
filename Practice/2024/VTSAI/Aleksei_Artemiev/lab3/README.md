# Lab #3.

Task Description
In this lab, we focused on implementing and analyzing a Deep Q-Network (DQN) to solve the "LunarLander-v2" environment. The primary goal was to train a reinforcement learning agent using DQN and observe how different discount factors affect the learning process and the convergence of Q-values. We experimented with three different discount factors: 0.01, 0.5, and 0.99, and evaluated the agent's performance and the evolution of Q-values over time.

Conclusion and Analysis
1. Discount Factor 0.01:

**Observation:** The Q-values showed small and smooth changes over time, indicating a slow convergence rate.

**Analysis:** A low discount factor like 0.01 makes the agent prioritize immediate rewards and pay less attention to future rewards. This can lead to short-sighted policies where long-term benefits are undervalued. The slow convergence suggests that the agent may struggle to learn the optimal long-term strategy, focusing instead on immediate outcomes.

2. Discount Factor 0.5:

**Observation:** The Q-values converged within approximately 250 steps.

**Analysis:** A moderate discount factor of 0.5 provides a balance between valuing immediate and future rewards. This balance allows the agent to consider both short-term and long-term consequences of actions, leading to a more stable and quicker convergence of Q-values. The agent is likely learning a policy that reasonably accounts for both immediate and future outcomes.

3. Discount Factor 0.99:

**Observation:** The Q-values converged within 200-250 steps, with a larger magnitude compared to the 0.5 discount factor.

**Analysis:** A high discount factor like 0.99 places significant importance on future rewards, encouraging the agent to develop strategies that maximize long-term gains. The quicker convergence and larger magnitude of Q-values indicate that the agent effectively learns to anticipate and optimize for future rewards. This can lead to a more forward-looking policy, though it may also risk overestimating long-term benefits in some cases.

Overall, the choice of discount factor significantly impacts the learning dynamics and policy development in DQN. Lower discount factors can lead to slower convergence and potentially suboptimal long-term strategies, while higher discount factors encourage the agent to focus on future rewards, often leading to quicker convergence and potentially more optimal long-term strategies. The results highlight the importance of carefully choosing the discount factor to balance immediate and future rewards according to the specific requirements of the task at hand.