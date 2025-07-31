import json
import re
import inspect
from openai import OpenAI
from typing import Dict, Any, List, Optional, Callable

# --- Configuration Section ---

# API and Model Configs
API_CONFIG = {
    "key": "", #openai key
    "base_url": "", #openai base url
    "extraction_model": "gpt-4o-mini-2024-07-18",
    "conversion_model": "gpt-4o-mini-2024-07-18"
}
API_CONFIG_QWEN = {
    "key": "",
    "base_url": "",
    "extraction_model": "qwen2.5-72b-instruct",
    "conversion_model": "qwen2.5-72b-instruct"
}
# Task Execution Config
# Change 'task_type' to 'cmqcic' to run the other task.
EXECUTION_CONFIG = {
    "task_type": "cmqcic",  # Supported types: "medcalc", "cmqcic"
    "generated_functions_file": 'generate_function/indicator_gpt-4o-mini_0721_none.jsonl', #generated functions file
    "results_output_file": "exe_results/mqcic_gpt-4o-mini_0721_1by1.jsonl", #results output file
    # Filter to run only specific IDs. Leave empty (e.g., []) to run all.
    "include_ids": []
}

# Task-specific settings (e.g., file paths, data keys)
TASK_SPECIFIC_CONFIGS = {
    "medcalc": {
        "patient_data_file": 'MedCalc_test_data.jsonl',
        "patient_id_key": "Calculator ID",
        "patient_note_key": "Patient Note"
    },
    "cmqcic": {
        "patient_data_file": 'data.jsonl',
        "patient_id_key": "unique_id",
        "patient_note_key": "patient note"
    }
}

# Prompts and System Messages
PROMPTS = {
    "param_extraction_system": "You are an expert in medical information extraction. Your task is to extract relevant facts from an electronic medical record (EMR). When dealing with time-related judgments, your reasoning must be based on the time documented within the EMR. if theres no fact related to the properties,using other facts in EMR to calculate it,if still cant get, return 0.01",
    "param_extraction_system_cn":"你是一名医学信息抽取专家，你的任务是从电子病历（EMR）中抽取相关事实。在涉及时间相关判断时，你的推理必须基于病历中记录的时间。若病历中对同一事实提及多次，需返回最符合要求的那一项，通常为最后出现的项。你可以调用工具来进行抽取，并且事实的抽取结果返回为True/False",
    "param_extraction_desc": "From the provided electronic medical record (EMR) excerpts, extract the necessary properties.",
    "param_extraction_desc_cn": """你是一名医学信息抽取专家，请从用户提供的电子病历段落中抽取与属性properties中事实的逻辑值。需要严格确诊才可以返回True，而不是简单地字段匹配，其它情况均应该为False，其它类型也类似。当病历中对同一事实提及多次或有时间先后时，取最后的结果。""",
    "unit_conversion": "you are an expert in unit conversion,u need to convert {key}:{original_value} {original_unit} to {target_unit}，your output format must be {{\"value\": \"converted value\", \"unit\": \"target unit\"}}in json format at last. important: converted value must be a number,not a string，not a character"
}#notice: creatinine unit:μmol/L=mg/dL×88.4


# --- Utility Functions ---

def get_json_from_response(text: str) -> Optional[Dict]:
    """Extracts a JSON object from a string, checking for markdown-wrapped JSON first."""
    match = re.search(r'```json\s*([\s\S]+?)\s*```', text, re.IGNORECASE)
    json_str = match.group(1) if match else text
    
    match = re.search(r'\{[\s\S]*\}', json_str)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON. Error: {e}. Content: '{match.group(0)}'")
        return None

def append_result_to_jsonl(file_path: str, data: Dict[str, Any]):
    """Appends a dictionary as a new line in a JSONL file."""
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write('\n')
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

# --- Core Logic Functions ---

def call_unit_conversion_llm(client: OpenAI, key: str, value: Any, from_unit: str, to_unit: str) -> tuple:
    """Uses an LLM to perform unit conversion, returning original values on failure."""
    prompt = PROMPTS["unit_conversion"].format(key=key, original_value=value, original_unit=from_unit, target_unit=to_unit)
    try:
        print(f"Unit conversion prompt: {prompt}")
        response = client.chat.completions.create(
            model=API_CONFIG["conversion_model"],
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        print(f'{value} {from_unit} to {to_unit}')
        print(f"Unit conversion response: {response.choices[0].message.content}")
        
        result_json = get_json_from_response(response.choices[0].message.content)
        if result_json and "value" in result_json:
            #print(f"Unit conversion result: {result_json}")
            return result_json["value"], result_json.get("unit", to_unit)
    except Exception as e:
        print(f"Error during unit conversion for key '{key}': {e}")
    return value, from_unit

def extract_parameters(client: OpenAI, properties: Dict[str, Any], patient_note: str, need_unit: Dict[str, str]) -> Dict[str, Any]:
    """Extracts and processes parameters from a patient note using an LLM."""
    tools = [{
        "type": "function",
        "function": {
            "name": "parametersExtraction",
            "description": PROMPTS["param_extraction_desc_cn"],
            "parameters": {"type": "object", "properties": properties, "required": list(properties.keys())}
        }
    }]
    messages = [{"role": "system", "content": PROMPTS["param_extraction_system_cn"]}, {"role": "user", "content": patient_note}]

    try:
        response = client.chat.completions.create(
            model=API_CONFIG["extraction_model"], messages=messages, tools=tools, tool_choice="required"
        )
        params = json.loads(response.choices[0].message.tool_calls[0].function.arguments)#['properties']
        if params.get('properties', {}):
            params_properties = params.get('properties', {})
        else:
            params_properties = params
        params = params_properties
        print(params_properties)
        print(f"Parameter extraction response: {params}")
    except Exception as e:
        print(f"Error during parameter extraction API call: {e}")
        return {}

    # Post-process extracted parameters
    for key, value in params.items():
        if isinstance(value, str):
            if value.lower() in ["true", "false"]:
                params[key] = value.lower() == "true"
        elif value is None or value == "" or value == []:
            params[key] = None

        if key in need_unit and isinstance(params[key], list) and params[key]:
            item = params[key][0]
            val, unit = item.get("value"), item.get("unit", "").strip()
            target_unit = need_unit[key].strip()

            # if unit.lower() != target_unit.lower() and val is not None and target_unit:
            #     new_val, _ = call_unit_conversion_llm(client, key, val, unit, target_unit)
            #     params[key] = float(new_val)
            # else:
                #params[key] = float(val) if val is not None else 0.01
            params[key] = float(val) if val is not None else None
    return params

def load_generated_functions(file_path: str) -> List[Dict[str, Any]]:
    """Loads tasks (code, properties, etc.) from a JSONL file."""
    tasks = []
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            for i, line in enumerate(file):
                try:
                    tasks.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON on line {i+1} in {file_path}")
    except FileNotFoundError:
        print(f"Error: Generated functions file not found at {file_path}")
    return tasks

def load_patient_data(file_path: str, id_key: str, note_key: str) -> Dict[str, List[str]]:
    """Loads all patient notes from a file and groups them by ID."""
    data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    record = json.loads(line.strip())
                    patient_id = str(record.get(id_key))
                    note = record.get(note_key)
                    if patient_id and note:
                        if patient_id not in data:
                            data[patient_id] = []
                        data[patient_id].append(note)
                except (json.JSONDecodeError, AttributeError):
                    continue
    except FileNotFoundError:
        print(f"Error: Patient data file not found at {file_path}")
    return data

def execute_task(task: Dict, client: OpenAI, patient_notes: List[str]) -> List[Dict]:
    """Processes a single task against a list of patient notes."""
    function_code = task.get("python_code")
    properties_raw = task.get("properties", {}).get("row", "")

    if not function_code or not properties_raw:
        print(f"Skipping Task ID {task.get('task_index')} due to missing code or properties.")
        return []

    try:
        properties_str = re.sub(r"properties\s*=\s*", "", properties_raw)
        properties = json.loads(properties_str)
    except json.JSONDecodeError:
        print(f"Error decoding properties for Task ID {task.get('task_index')}.")
        return []

    namespace = {}
    try:
        exec(function_code, namespace)
        func_name = next((name for name, obj in namespace.items() if callable(obj)), None)
        if not func_name:
            print(f"No callable function found for Task ID {task.get('task_index')}.")
            return []
        generated_func = namespace[func_name]
    except Exception as e:
        print(f"Error executing function code for Task ID {task.get('task_index')}: {e}")
        return []
        
    results = []
    need_unit = {k: re.sub(r'[:：\s]', '', v) for k, v in task.get("need_unit", {}).items()}

    for i, note in enumerate(patient_notes):
        print(f"  - Processing patient note {i+1}/{len(patient_notes)}...")
        extracted_params = extract_parameters(client, properties, note, need_unit)
        if not extracted_params:
            print("    ...failed to extract parameters, skipping execution.")
            continue
        try:
            result_val = generated_func(**extracted_params)
            results.append({'extract_para': extracted_params, 'result': result_val})
        except Exception as e:
            print(f"    ...error calling generated function: {e}")
            results.append({'extract_para': extracted_params, 'error': str(e)})

    return results

# --- Main Execution ---

def main():
    """Main execution script."""
    # 1. Load Configurations
    cfg = EXECUTION_CONFIG
    task_specific_cfg = TASK_SPECIFIC_CONFIGS[cfg["task_type"]]
    
    print(f"Starting execution for task type: '{cfg['task_type']}'")
    
    # 2. Initialize OpenAI Client
    client = OpenAI(api_key=API_CONFIG["key"], base_url=API_CONFIG["base_url"])

    # 3. Load Data
    all_tasks = load_generated_functions(cfg["generated_functions_file"])
    patient_data_map = load_patient_data(
        task_specific_cfg["patient_data_file"],
        task_specific_cfg["patient_id_key"],
        task_specific_cfg["patient_note_key"]
    )
    
    if not all_tasks or not patient_data_map:
        print("Could not load tasks or patient data. Exiting.")
        return

    # 4. Process each task
    for task in all_tasks:
        task_id = str(task.get('task_index', 'unknown'))
        print(task_id)
        if task_id not in ['肺癌_手术指征符合率（核心指标）', '脑出血（ICH）质控指标_手术适应症符合率', '脑膜瘤（初发，手术治疗）（MEN）质控指标_手术适应症符合率（核心指标）', '消化道出血质控指标_内镜下止血成功率', '肾癌质控指标_肾癌患者首次非手术治疗前病理学诊断率', '甲状腺癌质控指标_中央区淋巴结清扫率', '胃癌质控指标_I-III期胃癌患者手术治疗术中淋巴结清扫充分率(核心指标)', '肺癌_肺癌切除术术中纵隔淋巴结清扫充分率']:
        #['肺癌_手术指征符合率（核心指标）', '脑出血（ICH）质控指标_手术适应症符合率', '脑膜瘤（初发，手术治疗）（MEN）质控指标_手术适应症符合率（核心指标）', '胃癌质控指标_I-III期胃癌患者手术治疗术中淋巴结清扫充分率(核心指标)', '子宫肌瘤（手术治疗）（UM）_手术指征符合率', '原发性急性闭角型青光眼（手术治疗）_前房深度小于1.5mm术眼率', '消化道出血质控指标_内镜下止血成功率', '肺癌_肺癌切除术术中纵隔淋巴结清扫充分率', '肾癌质控指标_肾癌患者首次非手术治疗前病理学诊断率', '食管癌_食管癌患者根治性手术淋巴结清扫充分率', '甲状腺癌质控指标_颈侧区淋巴结清扫率', '甲状腺癌质控指标_中央区淋巴结清扫率', '冠状动脉旁路移植术（CABG）质控指标_桥血管流量测定率（核心指标）', '冠心病介入治疗技术质控指标_冠脉介入治疗术后即刻冠状动脉造影成功率', '脑出血（ICH）质控指标_出院时好转/稳定率', '帕金森病（PD）质控指标_住院帕金森病患者运动并发症筛查率', '乳腺癌_乳腺癌患者非手术治疗前病理学诊断率']:
            continue
        # Filter by ID if specified
        if cfg["include_ids"] and task_id not in cfg["include_ids"]:
            continue
            
        print(f"\n--- Processing Task ID: {task_id} ---")
        
        patient_notes = patient_data_map.get(task_id)
        
        if not patient_notes:
            print(f"No patient data found for ID {task_id}. Skipping.")
            continue

        # Execute the task against all found patient notes
        task_results = execute_task(task, client, patient_notes)

        # Save results to output file
        if task_results:
            final_output = {"id": task_id, "results": task_results}
            append_result_to_jsonl(cfg["results_output_file"], final_output)
            print(f"--- Results for Task ID {task_id} saved to {cfg['results_output_file']} ---")

    print("\nExecution complete.")

if __name__ == "__main__":
    main() 