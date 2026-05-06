# Lab #2. DDPG and SAC with BipedalWalker-v3 

In this lab, we experimented with the Deep Deterministic Policy Gradient (DDPG) and Soft Actor-Critic (SAC) reinforcement learning algorithms to train an agent in the BipedalWalker-v3 environment. Our focus was on tuning key parameters, specifically the noise sigma for DDPG and the learning rate for SAC, to observe their effects on the agent's performance. We conducted a series of experiments with varying values for these parameters and total training timesteps, analyzing the changes in actor and critic losses, as well as the agent's ability to navigate the environment.

Observations and Conclusions
1. DDPG with noise_sigma=0.01 (20,000 timesteps): The actor loss increased while the critic loss remained stable. Despite training, the agent struggled with walking.

2. DDPG with noise_sigma=0.2 (20,000 timesteps): We observed a decrease in actor loss and fluctuations in critic loss. The agent showed improved performance with attempts to step. Increasing the number of timesteps might enhance learning further.

3. DDPG with noise_sigma=0.5 (20,000 timesteps): Similar to the previous setting, but with a lower mean reward. The agent attempted to jump instead of walking.

4. SAC with lr=5e-5 (20,000 timesteps): Both actor and critic losses decreased, but the agent fell and was unable to recover after falling.

5. SAC with lr=2e-4 (20,000 timesteps): Losses did not change significantly, and the agent fell after the first step.

6. SAC with lr=1e-3 (20,000 timesteps): Losses fluctuated without a clear pattern, and the agent was unable to walk.

7. (best) SAC with lr=5e-5 (50,000 timesteps): The agent managed to make a step but then got stuck, indicating some learning but insufficient to complete the task.

Overall, the experiments suggest that fine-tuning the noise sigma for DDPG and the learning rate for SAC is crucial for the agent's performance in the BipedalWalker-v3 environment. Both algorithms showed different behaviors with varying parameters, highlighting the need for careful parameter selection and possibly longer training durations to achieve better results. The observations indicate that a balanced approach between exploration and exploitation, along with adequate training time, is essential for the agent to learn effectively in this complex environment.