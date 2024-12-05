import os
import sys
import random
import torch
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from snake_game_custom_wrapper_cnn import SnakeEnv

if torch.backends.mps.is_available():
    NUM_ENV = 32 * 2
else:
    NUM_ENV = 32
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Linear scheduler
def linear_schedule(initial_value, final_value=0.0):
    def scheduler(progress):
        return final_value + progress * (initial_value - final_value)
    return scheduler

def make_env(seed=0):
    def _init():
        env = SnakeEnv(seed=seed)
        env = ActionMasker(env, SnakeEnv.get_action_mask)
        env = Monitor(env)
        env.seed(seed)
        return env
    return _init

# Custom callback to display epoch info
class EpochLoggerCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(EpochLoggerCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        if self.num_timesteps % self.locals['self'].batch_size == 0:
            current_epoch = self.num_timesteps // self.locals['self'].batch_size
            print(f"[INFO] Current Epoch: {current_epoch}", file=sys.stdout)
        return True

def main():
    seed_set = set()
    while len(seed_set) < NUM_ENV:
        seed_set.add(random.randint(0, 1e9))
    env = SubprocVecEnv([make_env(seed=s) for s in seed_set])

    if torch.backends.mps.is_available():
        lr_schedule = linear_schedule(5e-4, 2.5e-6)
        clip_range_schedule = linear_schedule(0.150, 0.025)
        model = MaskablePPO(
            "CnnPolicy",
            env,
            device="mps",
            verbose=1,
            n_steps=2048,
            batch_size=512*8,
            n_epochs=4,
            gamma=0.94,
            learning_rate=lr_schedule,
            clip_range=clip_range_schedule,
            tensorboard_log=LOG_DIR
        )
    else:
        lr_schedule = linear_schedule(2.5e-4, 2.5e-6)
        clip_range_schedule = linear_schedule(0.150, 0.025)
        model = MaskablePPO(
            "CnnPolicy",
            env,
            device="cuda",
            verbose=1,
            n_steps=2048,
            batch_size=512,
            n_epochs=4,
            gamma=0.94,
            learning_rate=lr_schedule,
            clip_range=clip_range_schedule,
            tensorboard_log=LOG_DIR
        )

    save_dir = "trained_models_cnn_mps" if torch.backends.mps.is_available() else "trained_models_cnn"
    os.makedirs(save_dir, exist_ok=True)

    checkpoint_interval = 15625
    checkpoint_callback = CheckpointCallback(save_freq=checkpoint_interval, save_path=save_dir, name_prefix="ppo_snake")
    epoch_logger_callback = EpochLoggerCallback()

    original_stdout = sys.stdout
    log_file_path = os.path.join(save_dir, "training_log.txt")
    with open(log_file_path, 'w') as log_file:
        sys.stdout = log_file

        model.learn(
            total_timesteps=int(100000000),
            callback=[checkpoint_callback, epoch_logger_callback]
        )
        env.close()

    sys.stdout = original_stdout
    model.save(os.path.join(save_dir, "ppo_snake_final.zip"))

if __name__ == "__main__":
    main()
