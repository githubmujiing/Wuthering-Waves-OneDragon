import os
import yaml
from pathlib import Path


def get_specific_mission_number(mission_name):
    # 获取当前脚本的绝对路径
    current_dir = Path(__file__).resolve().parent

    # 计算项目根目录路径（向上回退3级：operation → ww_od → src → project_root）
    project_root = current_dir.parent.parent.parent

    # 构建YAML文件路径
    yaml_path = project_root / "assets" / "game_data" / "compendium_data.yml"

    # 检查文件是否存在
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML文件未找到: {yaml_path}")

    # 读取并解析YAML文件
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)


    target_tab = "周期挑战"
    target_category = "无音清剿"

    for tab in data:
        if tab.get("tab_name") == target_tab:
            for category in tab.get("category_list", []):
                if category.get("category_name") == target_category:
                    missions = category.get("mission_type_list", [])
                    for idx, mission in enumerate(missions, start=1):
                        name = mission.get("mission_type_name")
                        if name == mission_name:
                            return idx
    return None  # 如果没找到

def determine_silent_cleanup_type(mission_name):
    """判断无音清剿的新旧类型"""

    mission_number = get_specific_mission_number(mission_name)
    if mission_number >= 6:
        return 'old'
    else:
        return 'new'

# 使用示例
if __name__ == "__main__":
    current_directory = os.getcwd()
    print(f"当前工作目录: {current_directory}")
    type = determine_silent_cleanup_type("荒石高地无音区I")
    print(type)
