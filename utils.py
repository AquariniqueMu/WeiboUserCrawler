# Description: 通用工具函数


def datatype_process(content, target_type):
    """
    处理数据类型, 将content转换为target_type类型, 并处理常见的数据格式。
    """
    try:
        # 去掉左右两端的空格
        content = content.strip() if isinstance(content, str) else content
        
        # 处理整型转换
        if target_type == "int":
            # 去掉逗号, 万, 亿等字符，并进行相应的转换
            if isinstance(content, str):
                if "," in content:
                    content = content.replace(",", "")
                if "万" in content:
                    content = content.replace("万", "")
                    return int(float(content) * 10000)
                if "亿" in content:
                    content = content.replace("亿", "")
                    return int(float(content) * 100000000)
            return int(float(content))  # 转换为int，如果内容是浮点数，先转换为浮点数再转换为整型
            
        # 处理浮点型转换
        elif target_type == "float":
            if isinstance(content, str):
                content = content.replace(",", "")  # 去除逗号
            return float(content)  # 转换为浮点数
            
        # 处理字符串转换
        elif target_type == "str":
            return str(content)  # 转换为字符串
            
        # 处理布尔型转换
        elif target_type == "bool":
            # 常见布尔值表示形式
            if isinstance(content, str):
                if content.lower() in ['true', '1', 'yes', 'y', 'on']:
                    return True
                elif content.lower() in ['false', '0', 'no', 'n', 'off']:
                    return False
            return bool(content)
        
        # 未知目标类型，直接返回原内容
        else:
            return content

    except (ValueError, TypeError) as e:
        print(f"Error converting '{content}' to {target_type}: {e}")
        return None  # 返回None表示转换失败



from datetime import datetime

# 时间格式转为时间戳的函数
def convert_date_to_timestamp(date_str):
    try:
        # 假设输入格式为 "2024-10-12"
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # 转换为时间戳
        timestamp = int(dt.timestamp())
        return timestamp
    except ValueError as e:
        print(f"日期格式不正确: {e}")
        return None