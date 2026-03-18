# Examples: Robotics RL Design

## Example 1: Robotic Arm Reaching (PyBullet)

**Task**: Move a robot arm end-effector to a target position.

**Design**:
```
Task: Reach target XYZ position with end-effector
Simulator: PyBullet (free, good for learning)
Observation (10-dim):
  - Joint angles (6)
  - End-effector position (3)
  - Target position (3) [relative to end-effector]
  Total: 12-dim
Action: Joint velocity commands (6-dim, continuous)
Reward:
  task_reward: -L2_distance(end_effector, target)
  control_cost: -0.001 * sum(action^2)
  success_bonus: +10 if distance < 0.05
Safety:
  - Joint position limits from URDF
  - Max velocity: 2.0 rad/s per joint
Control Frequency: 50 Hz
Algorithm: PPO with VecNormalize
```

**Training**:
```python
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv

env = DummyVecEnv([lambda: ReachEnv()])
env = VecNormalize(env, norm_obs=True, norm_reward=True)

model = PPO("MlpPolicy", env, n_steps=2048, batch_size=64, verbose=1)
model.learn(total_timesteps=500_000)
```

**Result**: Agent reaches target within 0.05m consistently after ~300K steps.

---

## Example 2: Locomotion (MuJoCo HalfCheetah)

**Task**: Make a 2D cheetah run forward as fast as possible.

**Design**:
```
Task: Maximize forward velocity
Simulator: MuJoCo (HalfCheetah-v4)
Observation (17-dim): Joint angles, velocities, body orientation
Action (6-dim): Joint torques for 6 actuated joints
Reward:
  forward_velocity: velocity_x (primary)
  control_cost: -0.1 * sum(action^2)
Safety:
  - Torque limits from model definition
  - No explicit joint limits (model handles)
Control Frequency: 50 Hz (20ms timestep with frame_skip=5)
Algorithm: PPO, 8 parallel envs, VecNormalize
Training Budget: 2,000,000 timesteps
```

**Key insight**: HalfCheetah reward is straightforward — maximize forward speed. The control cost prevents energy-wasteful gaits. No alive bonus needed since HalfCheetah cannot fall over.

**Result**: Mean return ~5000+ after 2M steps.

---

## Example 3: Manipulation with Domain Randomization

**Task**: Pick up an object and place it at a target location, with sim-to-real transfer planned.

**Design**:
```
Task: Pick-and-place with 7-DOF robot arm + parallel gripper
Simulator: MuJoCo (custom MJCF)
Observation (25-dim):
  - Joint angles (7) + gripper state (1)
  - End-effector pose (6)
  - Object pose (6)
  - Target pose (3)
  - Gripper-object distance (1)
  - Object-target distance (1)
Action (8-dim): Joint velocities (7) + gripper command (1)
Reward:
  reach: -distance(gripper, object) [phase 1]
  grasp: +1.0 when object lifted
  place: -distance(object, target) [phase 2]
  success: +10 when placed within 0.02m
Safety:
  - Joint limits enforced via clipping
  - Max end-effector velocity: 0.5 m/s
  - Force limit: 20N at gripper
Domain Randomization:
  - Object mass: [0.05, 0.5] kg
  - Friction: [0.5, 1.5]
  - Action delay: [0, 2] timesteps
  - Observation noise: N(0, 0.01)
Algorithm: PPO, 16 parallel envs
Training Budget: 10,000,000 timesteps
```

**Key insight**: Multi-phase rewards (reach, grasp, place) guide learning through the task stages. Domain randomization across mass, friction, and delays builds robustness for real-world transfer.
