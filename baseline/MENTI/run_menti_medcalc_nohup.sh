#!/bin/bash

# 使用nohup运行指定Calculator ID列表的评估脚本

# 设置环境变量
export OPENAI_API_KEY=
export OPENAI_BASE_URL=

# 生成时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="menti_medcalc_${TIMESTAMP}.log"

echo "=== 使用nohup运行指定Calculator ID评估 ==="
echo "日志文件: $LOG_FILE"
echo "开始时间: $(date)"

# 指定的Calculator ID列表
CALCULATOR_IDS=("2" "3" "5" "6" "7" "8" "9" "10" "11" "19" "22" "26" "30" "31" "38" "39" "40" "44" "56" "57" "58" "59" "60" "61" "62" "63" "64" "65" "66" "67")

echo "将评估以下Calculator ID:"
echo "${CALCULATOR_IDS[@]}"
echo ""

# 检查数据集是否存在
if [ ! -f "./MedCalc-Bench-main/dataset/test_data.csv" ]; then
    echo "错误：找不到MedCalc-Bench数据集"
    echo "请确保MedCalc-Bench-main/dataset/test_data.csv文件存在"
    exit 1
fi

# 创建输出目录
mkdir -p menti_outputs

echo "开始后台运行评估..."
echo "使用以下命令查看日志: tail -f $LOG_FILE"
echo "使用以下命令查看进程: ps aux | grep menti_medcalc_eval"
echo ""

            # 使用nohup运行评估（使用优化版本）
            nohup python menti_medcalc_eval_simple.py \
                --llm_model gpt-4o-mini \
                --embedding_model openai \
                --calculator_ids "${CALCULATOR_IDS[@]}" \
                --compute_stats \
                --parallel > "$LOG_FILE" 2>&1 &

# 获取进程ID
PID=$!
echo "进程已启动，PID: $PID"
echo "进程ID已保存到: menti_medcalc_${TIMESTAMP}.pid"

# 保存进程ID到文件
#echo $PID > "menti_medcalc_${TIMESTAMP}.pid"

echo ""
echo "=== 运行信息 ==="
echo "进程ID: $PID"
echo "日志文件: $LOG_FILE"
echo "PID文件: menti_medcalc_${TIMESTAMP}.pid"
echo "开始时间: $(date)"
echo ""
echo "=== 常用命令 ==="
echo "查看实时日志: tail -f $LOG_FILE"
echo "查看进程状态: ps aux | grep $PID"
echo "停止进程: kill $PID"
echo "查看输出目录: ls -la menti_outputs/"
echo ""
echo "评估正在后台运行，您可以安全地关闭终端。" 