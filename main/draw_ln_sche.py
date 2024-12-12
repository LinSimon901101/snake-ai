import matplotlib.pyplot as plt

# 定義進度
progress = [i / 100 for i in range(101)]

# 定義 linear_schedule 函數
def linear_schedule(initial_value, final_value=0.0):
    def scheduler(progress):
        return final_value + (1 - progress) * (initial_value - final_value)
    return scheduler

# 計算學習率和剪裁範圍
lr_schedule = linear_schedule(2.5e-4, 2.5e-6)
clip_range_schedule = linear_schedule(0.150, 0.025)
lr_values = [lr_schedule(p) for p in progress]
clip_range_values = [clip_range_schedule(p) for p in progress]

# 繪圖
plt.plot(progress, lr_values, label="Learning Rate")
plt.plot(progress, clip_range_values, label="Clip Range")
plt.xlabel("Training Progress")
plt.ylabel("Value")
plt.legend()
plt.title("Linear Schedule Effect")
plt.show()
