import json

valid_ids = {2, 3, 5, 6, 7, 8, 9, 10, 11, 19, 22, 26, 30, 31, 38, 39, 40, 44, 56, 57, 58, 59, 60, 62, 63, 64, 65, 66, 67, 61}

# 新增：每个id的统计
id_total = {}
id_correct = {}

total = 0
correct = 0

with open('/Users/songg/MedCalc-Bench-main/evaluation/outputs/OpenAI_gpt-4o-mini_one_shot.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue  # 跳过空行
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            print(f"跳过格式错误的行: {line}")
            continue
        calc_id = data.get("Calculator ID")
        # 兼容数字和字符串类型
        if isinstance(calc_id, str) and calc_id.isdigit():
            calc_id = int(calc_id)
        if calc_id in valid_ids:
            total += 1
            id_total[calc_id] = id_total.get(calc_id, 0) + 1
            if data.get("Result") == "Correct":
                correct += 1
                id_correct[calc_id] = id_correct.get(calc_id, 0) + 1

if total == 0:
    print("没有符合条件的数据。")
else:
    accuracy = correct / total
    print(f"总数: {total}")
    print(f"正确数: {correct}")
    print(f"正确率: {accuracy:.2%}")
    # print("各ID正确数/总数：")
    # for cid in sorted(id_total.keys()):
    #     c = id_correct.get(cid, 0)
    #     t = id_total[cid]
    #     print(f"ID {cid}: {c}/{t}")
