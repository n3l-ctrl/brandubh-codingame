import subprocess

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

p = subprocess.Popen(["python", "config/Boss.py3"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = p.communicate(input_data)
print("STDOUT:", stdout)
print("STDERR:", stderr)
