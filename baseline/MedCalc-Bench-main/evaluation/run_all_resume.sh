#!/bin/bash

# 设置环境变量（请替换成你的实际值）
export OPENAI_API_KEY=sk-593f44bd25a24ba19d966843c199b3d4
export OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 进入 evaluation 目录
cd "$(dirname "$0")"

# 运行三种 prompt，使用 run_resume.py 以支持断点续传
for prompt in one_shot #zero_shot one_shot #direct_answer
do
    echo "Running $prompt with resume capability..."
    python run_resume.py --model OpenAI/qwen2.5-72b-instruct --prompt $prompt
done

# 合并所有结果为一个 json 文件
# 确保合并的目标文件路径与单个结果文件的输出路径在同一目录下 (evaluation/outputs)
MERGED_OUTPUT_FILE="outputs/all_results_qwen2.5-72b-instruct.json"
echo "[" > "$MERGED_OUTPUT_FILE"
first=1
for prompt in zero_shot  #direct_answer
do
    # run_resume.py 生成的文件名是 OpenAI_qwen2.5-72b-instruct_{prompt}.jsonl
    # 并且这些文件位于 evaluation/outputs/ 目录下
    file="outputs/OpenAI_qwen2.5-72b-instruct_${prompt}.jsonl"
    if [ -f "$file" ]; then
        echo "Merging $file..."
        while IFS= read -r line
        do
            if [ $first -eq 1 ]; then
                first=0
            else
                echo "," >> "$MERGED_OUTPUT_FILE"
            fi
            echo "$line" >> "$MERGED_OUTPUT_FILE"
        done < "$file"
    else
        echo "Warning: File $file not found, skipping for merge."
    fi
done
echo "]" >> "$MERGED_OUTPUT_FILE"

echo "所有结果已合并到 $MERGED_OUTPUT_FILE" 