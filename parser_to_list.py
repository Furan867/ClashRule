import yaml
import os
from datetime import datetime


script_dir = os.path.dirname(os.path.abspath(__file__))

PARSER_FILE = r"C:\Users\Furan\.config\clash\profiles\main.yaml"
OUTPUT_FILENAME = os.path.join(script_dir, r"rule\main_rule.list")
LOG_FILENAME = os.path.join(script_dir, r'log\log_rule.txt')
# OUTPUT_FILENAME = r"./my_main_rule.list"
# LOG_FILENAME = r"./log_rule.list"

def cast(
    parser_filename=PARSER_FILE,
    output_filename=OUTPUT_FILENAME,
    log_filename=LOG_FILENAME,
):
    print("--- 开始转换: 预处理文件 -> .list ---")
    print(f"源文件: {parser_filename}")
    print(f"目标文件{output_filename}")
    print(f"处理日志: {log_filename}")
    try:
        with open(parser_filename, "r", encoding="utf-8") as f:
            main_config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ℹ️ 源文件 '{parser_filename}' 为空。")
        return
    except yaml.YAMLError as exc:
        print(f"❌ 错误解析 YAML 文件 '{parser_filename}': {exc}")
        return

    if ("prepend-rules" not in main_config) and (
        not isinstance(main_config["prepend-rules"], list)
    ):
        print("ℹ️ 源文件中未找到 'prepend-rules' 部分或其不是一个列表。无需处理。")
        return

    original_rules = main_config["prepend-rules"]

    existed_rules = set()
    if os.path.exists(output_filename):
        try:
            with open(output_filename, "r", encoding="utf-8") as f:
                for line in f:
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith('#'): # 忽略空行和注释行
                        existed_rules.add(stripped_line)
            print(f"✅ 已加载 '{output_filename}' 中 {len(existed_rules)} 条现有规则用于去重。")
        except Exception as e:
            print(f"❌ 警告: 读取 '{output_filename}' 失败，可能无法完全去重: {e}")
    else:
        print(f"ℹ️ '{output_filename}' 不存在，将创建新文件。")
    
    """###########################################################"""

    # 5. 处理规则，准备写入
    rules_to_add_to_list = []      # 存储要添加到 new_rule.list 的规则 (TYPE,VALUE)
    original_rules_to_log = []     # 存储要记录到 processed_rules_log.txt 的原始规则 (原始字符串)
    processed_count = 0

    for original_rule_str in original_rules:
        if not isinstance(original_rule_str, str):
            print(f"❌ 警告: 规则 '{original_rule_str}' 不是字符串类型，跳过。")
            continue
        trimmed_original_rule_str = original_rule_str.strip()  # 去除原始字符串首尾空白
        if trimmed_original_rule_str in existed_rules:
            continue

        parts = trimmed_original_rule_str.split(',')

        # 检查规则是否至少包含 RuleType,Value 两部分
        if len(parts) < 2:
            print(f"❌ 警告: 规则 '{trimmed_original_rule_str}' 格式不正确 (缺少 RuleType 或 Value)，跳过。")
            continue

        # 构造纯净的 RuleType,Value 形式
        new_rule_for_list = ','.join(parts[:2]).strip()

        # 检查是否已存在于 output_filename 中
        if new_rule_for_list not in existed_rules:
            rules_to_add_to_list.append(new_rule_for_list)
            existed_rules.add(new_rule_for_list) # 立即添加到集合，防止后续重复
            
            original_rules_to_log.append(trimmed_original_rule_str)
            processed_count += 1

    # 6. 将新规则追加到 OUTPUT_FILENAME
    if rules_to_add_to_list:
        try:
            # 如果文件不存在，mode 'a' 会创建它
            with open(output_filename, "a", encoding="utf-8") as f:
                # 只有当文件是新建且没有内容时，才写入头部（可选，如果你希望每次都追加就不要了）
                # 为了保持简单且符合追加模式，这里不写入头部
                for rule in rules_to_add_to_list:
                    f.write(rule + '\n')
            print(f"✅ 已将 {len(rules_to_add_to_list)} 条新规则追加到 '{output_filename}'。")
        except Exception as e:
            print(f"❌ 写入 '{output_filename}' 失败: {e}")
    else:
        print(f"ℹ️ 未发现需要添加到 '{output_filename}' 的新规则。")

    # 7. 将原始规则追加到 PROCESSED_RULES_LOG_FILE
    if original_rules_to_log:
        try:
            with open(log_filename, "a", encoding="utf-8") as f:
                f.write(
                    f"\n---------- Processed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ----------\n"
                )
                for original_rule in original_rules_to_log:
                    f.write(original_rule + '\n')
            print(f"✅ 已将 {len(original_rules_to_log)} 条原始规则记录到 '{log_filename}'。")
        except Exception as e:
            print(f"❌ 写入 '{log_filename}' 失败: {e}")
    else:
        print(f"ℹ️ 未发现需要记录到 '{log_filename}' 的新原始规则。")

    print(f"--- 规则处理完成。总计处理了 {processed_count} 条新原始规则。---")

    # processed_rules = []
    # for line in original_rules:
    #     parts = line.split(",")

    #     if len(parts) < 2:
    #         print(f"错误规则{line}")
    #         continue

    #     new_rule = ",".join(parts[:2])
    #     if new_rule in processed_rules:
    #         continue
    #     processed_rules.append(new_rule)

    # # for end
    # with open(output_filename, "w", encoding="utf-8") as f:
    #     f.write("my custom rule" + "\n")
    #     for rule in processed_rules:
    #         if rule.strip():
    #             f.write(rule.strip() + "\n")
    # # debug print
    # with open(output_filename, "r", encoding="utf-8") as f:
    #     print("{0}{1}{0}".format("=" * 80 + "\n", f.read()))


if __name__ == "__main__":
    cast()

    # 脚本功能不全

    print("end")
    pass
