# addon/operators/func_core/json_tools.py
import json
import os
from typing import Any, Dict, Optional

def get_addon_root() -> str:
    """คืน path ของโฟลเดอร์ราก Add-on (ไต่ขึ้นจากตำแหน่งไฟล์นี้)"""
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # __file__ -> func_core -> operators -> addon(root)

def read_json(filename: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    อ่านไฟล์ JSON (filename เป็นชื่อไฟล์ เช่น 'setting.json')
    คืน dict หรือ default ถ้าไม่มีไฟล์
    """
    path = os.path.join(get_addon_root(), filename)
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return default if default is not None else {}
        return data
    except Exception:
        return default if default is not None else {}

def write_json(filename: str, data: Dict[str, Any]) -> bool:
    """
    เขียน dict ลงไฟล์ JSON (filename เป็นชื่อไฟล์ เช่น 'setting.json')
    """
    path = os.path.join(get_addon_root(), filename)
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_path, path)
        return True
    except Exception:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False
