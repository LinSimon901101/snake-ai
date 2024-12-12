import matplotlib.pyplot as plt

# 定義進度
progress = [i / 100 for i in range(101)]

# 定義 linear_schedule 函數
def linear_schedule(initial_value, final_value=0.0):
    def scheduler(progress):
        return final_value + (1 - progress) * (initial_value - final_value)
    return scheduler

# 計算學習率
lr_schedule = linear_schedule(2.5e-4, 2.5e-6)
lr_values = [lr_schedule(p) for p in progress]

# 繪圖
plt.plot(progress, lr_values, label="Learning Rate")
plt.xlabel("Training Progress")
plt.ylabel("Value")
plt.legend()
plt.title("Linear Learning Rate Schedule")
plt.show()
