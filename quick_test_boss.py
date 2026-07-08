import subprocess
import os

boss_path = os.path.join("config", "Boss.py3")

# Input format:
# Player index (0 or 1)
# Number of pieces
# For each piece: owner, type, x, y

input_data = """0
13
0 ATTACKER 3 0
0 ATTACKER 3 1
0 ATTACKER 0 3
0 ATTACKER 1 3
0 ATTACKER 6 3
0 ATTACKER 5 3
0 ATTACKER 3 6
0 ATTACKER 3 5
1 DEFENDER 3 2
1 DEFENDER 2 3
1 DEFENDER 4 3
1 DEFENDER 3 4
1 KING 3 3
"""

process = subprocess.Popen(["python", boss_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate(input=input_data)

print("STDOUT:", stdout)
print("STDERR:", stderr)
