#!/bin/bash

# 设置环境变量（请替换成你的实际值）
export OPENAI_API_KEY=
export OPENAI_BASE_URL=

export OPENAI_API_KEY=
export OPENAI_BASE_URL=

# 进入 evaluation 目录
cd "$(dirname "$0")"

# 运行三种 prompt
for prompt in zero_shot one_shot direct_answer
do
    echo "Running $prompt ..."
    python run.py --model OpenAI/gpt-4o-mini --prompt $prompt
done

# 合并所有结果为一个 json 文件
echo "[" > ../outputs/all_results_gpt-4o-mini.json
first=1
for prompt in zero_shot one_shot direct_answer
do
    file="../outputs/gpt-4o-mini_${prompt}.jsonl"
    if [ -f "$file" ]; then
        while IFS= read -r line
        do
            if [ $first -eq 1 ]; then
                first=0
            else
                echo "," >> ../outputs/all_results_gpt-4o-mini.json
            fi
            echo "$line" >> ../outputs/all_results_gpt-4o-mini.json
        done < "$file"
    fi
done
echo "]" >> ../outputs/all_results_gpt-4o-mini.json

echo "所有结果已合并到 outputs/all_results_gpt-4o-mini.json"