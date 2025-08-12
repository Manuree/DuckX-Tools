import bpy
import types

def run_text_block_by_exec(text_name: str):
    text = bpy.data.texts.get(text_name)
    if not text:
        raise RuntimeError(f"Text '{text_name}' not found")

    code = text.as_string()
    filename = f"<Text:{text_name}>"

    g = {
        "__name__": "__main__",   # ให้บล็อค if __name__ == "__main__": ทำงาน
        "__file__": filename,     # เพื่อ stacktrace อ่านง่าย
        "bpy": bpy,               # ฉีด bpy ให้สคริปต์ใช้ได้โดยไม่ต้อง import
    }
    l = {}

    compiled = compile(code, filename, "exec")
    exec(compiled, g, l)

def run_text_block(text_name: str):
    text = bpy.data.texts.get(text_name)
    if not text:
        raise RuntimeError(f"Text '{text_name}' not found")

    try:
        win = bpy.context.window
        area = next((a for a in win.screen.areas if a.type == 'TEXT_EDITOR'), None)
        if area:
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            with bpy.context.temp_override(window=win, area=area, region=region, edit_text=text):
                bpy.ops.text.run_script()
            return
    except Exception as e:
        # ถ้าเป็นเคส bpy ไม่ถูก define หรือไม่มี UI -> fallback
        if "NameError: name 'bpy' is not defined" not in str(e):
            # error อื่นปล่อยตกลง fallback เช่นกัน
            pass

    # Fallback แบบฉีด namespace
    run_text_block_by_exec(text_name)