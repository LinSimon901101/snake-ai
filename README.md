# SnakeAI
### 文件结构

```bash
├───main
│   ├───logs
│   ├───trained_models_cnn
│   ├───trained_models_mlp
│   └───scripts
├───utils
│   └───scripts
```
### 环境配置
```bash
# python version = 3.8.16
conda create -n SnakeAI python=3.8.16
conda activate SnakeAI
```

Windows:
```bash 
# manually install pytorch
conda install pytorch=2.0.0 torchvision pytorch-cuda=11.8 -c pytorch -c nvidia

#  testout could pytorch access GPU
python .\utils\check_gpu_status.py

# install python kit from requirement.txt
pip install -r requirements.txt
```

### 运行测试


```bash
# test for game play
cd [项目上级文件夹]/snake-ai/main
python .\snake_game.py
```

After game stepup, testout `test_cnn.py` in main

```bash
cd [项目上级文件夹]/snake-ai/main
python test_cnn.py
```
weight file for model will store in `main/trained_models_cnn/`, change `Model_PATH` in `test_cnn.py` in
order to observe the difference between different training steps

### 训练模型

While re-training model,  execute the command in main

```bash
cd [项目上级文件夹]/snake-ai/main
python train_cnn.py
```

### 查看曲线

The project includes Tensorboard curve graphs of the training process. You can use Tensorboard to view detailed data. It is recommended to use the integrated Tensorboard plugin in VSCode for direct viewing, or you can use the traditional method:

```bash
# in main file
tensorboard --logdir=logs/
```

Open the default Tensorboard service address http://localhost:6006/ in your browser to view the interactive curve graphs of the training process.

# Fully Command for build up project

```bash
Step1.
    conda create -n SnakeAI python=3.8.16
    conda activate SnakeAI

Step2.
    conda install pytorch=2.0.0 torchvision pytorch-cuda=11.8 -c pytorch -c nvidia
    python .\utils\check_gpu_status.py
    (In gym-0.21.0 file)python setup.py install
    pip install -r requirements.txt
```