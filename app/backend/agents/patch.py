with open("scripts/setup_dynamodb.py", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "create_audit_logs_table()" in line:
        lines.insert(i+1, "    create_checkpoints_table()\n")
        break
with open("scripts/setup_dynamodb.py", "w") as f:
    f.writelines(lines)
