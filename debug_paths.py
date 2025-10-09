import os
import sys

# 模拟config.py中的路径计算
current_file = "lib/modules/config.py"
abs_path = os.path.abspath(current_file)
print(f"Absolute path of config.py: {abs_path}")

parent_dir = os.path.dirname(os.path.dirname(abs_path))
print(f"Parent directory (should be project root): {parent_dir}")

lib_dir = os.path.join(parent_dir, 'lib')
model_dir = os.path.join(parent_dir, 'model')
print(f"lib_dir: {lib_dir}")
print(f"model_dir: {model_dir}")

# 检查目录是否存在
print(f"lib_dir exists: {os.path.exists(lib_dir)}")
print(f"model_dir exists: {os.path.exists(model_dir)}")
