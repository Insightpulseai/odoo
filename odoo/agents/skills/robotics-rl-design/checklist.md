# Checklist: Robotics RL Design

## Task Definition

- [ ] Physical task clearly described
- [ ] Success criteria defined (quantitative)
- [ ] Relevant physical constraints identified
- [ ] Control modality chosen (position, velocity, torque)

## Simulator Setup

- [ ] Simulator selected and justified
- [ ] Robot model loaded (URDF/MJCF)
- [ ] Physics parameters configured (timestep, solver iterations)
- [ ] Control frequency set appropriately
- [ ] Rendering available for debugging

## Observation Space

- [ ] Joint angles included
- [ ] Joint velocities included
- [ ] End-effector pose included (if manipulation)
- [ ] Goal specification included
- [ ] Contact/force sensor data included (if relevant)
- [ ] Observation normalization applied

## Action Space

- [ ] Action type matches control modality
- [ ] Action bounds match physical joint limits
- [ ] Action scaling applied (normalize to [-1, 1])
- [ ] Action clipping enforced

## Reward Function

- [ ] Task reward component defined
- [ ] Control cost component added
- [ ] Alive/upright bonus added (if locomotion)
- [ ] Safety penalty for constraint violations
- [ ] Reward components weighted and balanced
- [ ] No reward hacking paths identified

## Safety Constraints

- [ ] Joint position limits enforced
- [ ] Joint velocity limits enforced
- [ ] Joint torque limits enforced
- [ ] Self-collision avoidance (if applicable)
- [ ] Workspace boundaries defined

## Domain Randomization (if sim-to-real)

- [ ] Dynamic parameters to randomize identified
- [ ] Randomization ranges set
- [ ] Sensor noise model defined
- [ ] Action delay model defined
- [ ] Visual randomization (if using vision)

## Training

- [ ] PPO selected as default algorithm
- [ ] Observation and reward normalization via VecNormalize
- [ ] Multiple parallel environments
- [ ] Training budget established
- [ ] Evaluation protocol defined
