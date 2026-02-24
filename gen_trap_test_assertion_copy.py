"""
RVV指令trap测试断言生成脚本
根据CSV约束表格生成对应的SystemVerilog断言
"""

import sys
from tkinter import W
import pandas as pd
from io import StringIO

# CSV文件路径 - 用户需要根据实际情况修改
csv_path = "./RVV_instr_constrain.csv"

# RTL信号名称定义 - 用户可以根据实际设计修改
opcode_rtl_name = "cpu_opcode"
expt_rtl_name = "expt"
vm_rtl_name = "vm"
vd_rtl_name = "vd"
vs1_rtl_name = "vs1"
vs2_rtl_name = "vs2"
vs3_rtl_name = "vs3"
vstart_rtl_name = "vstart"
sew_rtl_name = "sew"
lmul_rtl_name = "lmul"
lmul_map_name = "lmul_map"
lmul_map_m2_name = "lmul_map_m2"
lmul_map_d2_name = "lmul_map_d2"
lmul_map_d4_name = "lmul_map_d4"
lmul_map_d8_name = "lmul_map_d8"
emul_rtl_name = "emul"

# 列号定义（从1开始）- 需要根据实际CSV文件调整
started_row = 2
# instr_num = 134
vm_not_eq_1_num = 2
vm_eq_1_vd_eq_1_num = 3
vstart_not_eq_0_num = 4
unsupported_sew_num = 5
unsupported_lmul_num = 9
reg_index_alignment_num = 16
overlap_constain0_num = 37
overlap_constain1_num = 39
reg_index_not_equal_num = 42
other_constraint_num = 47
index_load_constraint_num = 52
eew_num = 53  # eew相关列
no_constraint_num = 55
match_num = 57
mask_num = 58
is_ready_num = 61



def read_full_dataframe(csv_file_path):
    """读取完整的CSV文件，处理编码问题和NUL字节"""
    try:
        with open(csv_file_path, "rb") as f:
            raw_content = f.read()
        
        # 清除NUL字节
        nul_count = raw_content.count(b"\x00")
        if nul_count > 0:
            print(f"检测到 {nul_count} 个 NUL 字节，已清除", file=sys.stderr)
            raw_content = raw_content.replace(b"\x00", b"")
        
        # 尝试不同编码
        encodings = ["utf-8", "utf-8-sig", "gbk", "latin1"]
        text_content = None
        for encoding in encodings:
            try:
                text_content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if text_content is None:
            text_content = raw_content.decode("latin1")
        
        # 读取CSV
        df = pd.read_csv(
            StringIO(text_content),
            engine="python",
            on_bad_lines="warn",
            skip_blank_lines=False,
            keep_default_na=False
        )
        
        return df
        
    except Exception as e:
        print(f"读取CSV文件失败: {e}", file=sys.stderr)
        sys.exit(1)

def no_unsupport_flag_func(df, i, start_col_num, target_num):
    no_unsupport_flag = 1
    for n in range(0,target_num):
        flag = df.iloc[i, start_col_num]
        if "1" in str(flag):
            no_unsupport_flag &= 0
        else:
            no_unsupport_flag &= 1
        start_col_num += 1

    return no_unsupport_flag

def vm_not_eq_1_assertion(instr_name, flag, match, mask):
    """生成vm != 1的trap断言"""
    text_context = "//vm != 1\n"
    text_context += f"logic {instr_name}_vm_not_eq_1_expt_con;\n"
    
    if "1" in str(flag):
        text_context += f"assign {instr_name}_vm_not_eq_1_expt_con = !{vm_rtl_name};\n"
        text_context += f"ast_{instr_name}_vm_not_eq_1: assert property( (("
        text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
        text_context += f"{instr_name}_vm_not_eq_1_expt_con |-> {expt_rtl_name});\n"
    else:
        text_context += f"assign {instr_name}_vm_not_eq_1_expt_con = 0;\n"
    
    text_context += "\n"
    return text_context

def vm_vd_eq_0_assertion(instr_name, flag, match, mask):
    """生成vm == 0时vd == 0的trap断言"""
    text_context = "//vm == 0 and vd == 0\n"
    text_context += f"logic {instr_name}_vm_vd_eq_0_expt_con;\n"
    
    if "1" in str(flag):
        text_context += f"assign {instr_name}_vm_vd_eq_0_expt_con = !{vm_rtl_name} && !{vd_rtl_name};\n"
        text_context += f"ast_{instr_name}_vm_vd_eq_0: assert property( ( ("
        text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
        text_context += f"{instr_name}_vm_vd_eq_0_expt_con |-> {expt_rtl_name});\n"
    else:
        text_context += f"assign {instr_name}_vm_vd_eq_0_expt_con = 0;\n"
    
    text_context += "\n"
    return text_context

def vstart_not_eq_0_assertion(instr_name, flag, match, mask):
    """生成vstart != 0的trap断言"""
    text_context = "//vstart != 0\n"
    text_context += f"logic {instr_name}_vstart_not_eq_0_expt_con;\n"
    
    if "1" in str(flag):
        text_context += f"assign {instr_name}_vstart_not_eq_0_expt_con = {vstart_rtl_name} != 'h0;\n"
        text_context += f"ast_{instr_name}_vstart_not_eq_0: assert property( (("
        text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
        text_context += f"{instr_name}_vstart_not_eq_0_expt_con |-> {expt_rtl_name});\n"
    else:
        text_context += f"assign {instr_name}_vstart_not_eq_0_expt_con = 0;\n"
    
    text_context += "\n"
    return text_context

def unsupported_sew_sub_con(instr_name, sew):
    """生成不支持的SEW子约束"""
    text_context = ""
    text_context += f"logic {instr_name}_unsupported_sew{sew};\n"
    
    sew_mapping = {8: 'b000', 16: 'b001', 32: 'b010', 64: 'b011'}
    if sew in sew_mapping:
        text_context += f"assign {instr_name}_unsupported_sew{sew} = {sew_rtl_name} == '{sew_mapping[sew]} ? 1 : 0;\n"
    
    return text_context

def unsupported_sew_assertion(instr_name, df, i, match, mask):
    """生成不支持的SEW断言"""
    text_context = "//unsupported sew\n"
    text_context += f"logic {instr_name}_unsupported_sew_expt_con;\n"
    
    con_str = f"assign {instr_name}_unsupported_sew_expt_con = "
    start_col_num = unsupported_sew_num - 1
    
    for sew in [8, 16, 32, 64]:
        flag = df.iloc[i, start_col_num] if start_col_num < len(df.columns) else ""
        if "1" in str(flag):
            text_context += unsupported_sew_sub_con(instr_name, sew)
        else:
            text_context += f"assign {instr_name}_unsupported_sew{sew} = 0;\n"
        
        con_str += f"{instr_name}_unsupported_sew{sew} || "
        start_col_num += 1
    
    text_context += con_str[:-3] + ";\n"
    no_unsupport_flag = no_unsupport_flag_func(df, i, unsupported_sew_num - 1, 4)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_unsupported_sew: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_unsupported_sew_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def unsupported_lmul_sub_con(instr_name, lmul):
    """生成不支持的LMUL子约束"""
    text_context = ""
    lmul_str = str(lmul).replace('/', '_')
    text_context += f"logic {instr_name}_unsupported_lmul{lmul_str};\n"
    
    lmul_mapping = {"1_8": 'b101', "1_4": 'b110', "1_2": 'b111', 
                   "1": 'b000', "2": 'b001', "4": 'b010', "8": 'b011'}
    if lmul_str in lmul_mapping:
        text_context += f"assign {instr_name}_unsupported_lmul{lmul_str} = {lmul_rtl_name} == '{lmul_mapping[lmul_str]} ? 1 : 0;\n"
    
    return text_context

def unsupported_lmul_assertion(instr_name, df, i, match, mask):
    """生成不支持的LMUL断言"""
    text_context = "//unsupported lmul\n"
    text_context += f"logic {instr_name}_unsupported_lmul_expt_con;\n"
    
    con_str = f"assign {instr_name}_unsupported_lmul_expt_con = "
    start_col_num = unsupported_lmul_num - 1
    
    for lmul in ["1_8", "1_4", "1_2", "1", "2", "4", "8"]:
        flag = df.iloc[i, start_col_num] if start_col_num < len(df.columns) else ""
        if "1" in str(flag):
            text_context += unsupported_lmul_sub_con(instr_name, lmul)
        else:
            lmul_str = lmul.replace('/', '_')
            text_context += f"assign {instr_name}_unsupported_lmul{lmul_str} = 0;\n"
        
        lmul_str = lmul.replace('/', '_')
        con_str += f"{instr_name}_unsupported_lmul{lmul_str} || "
        start_col_num += 1
    
    text_context += con_str[:-3] + ";\n"
    no_unsupport_flag = no_unsupport_flag_func(df, i, unsupported_lmul_num - 1, 7)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_unsupported_lmul: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_unsupported_lmul_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def reg_index_alignment_sub_con(instr_name, ref1, ref2):
    """生成寄存器索引对齐子约束"""
    text_context = ""
    text_context += f"logic {instr_name}_reg_index_alignment_{ref1}_{ref2};\n"

    
    ref_mapping = {"vd": vd_rtl_name, "vs1": vs1_rtl_name, "vs2": vs2_rtl_name, "vs3": vs3_rtl_name}
    if ref1 in ref_mapping:
        ref_signal = ref_mapping[ref1]
        
        # print(f"instr_name={instr_name},ref2={ref2}")
        if ref2 == "lmul":
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % {lmul_map_name}) != 'h0 ? 1 : 0;\n"
        elif ref2 == "2lmul":
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % {lmul_map_m2_name} ) != 'h0 ? 1 : 0;\n"
        elif ref2 == "emul":
            # print(f"instr_name={instr_name}")
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % emul_map ) != 'h0 ? 1 : 0;\n"
        elif ref2 == "lmul1_2":
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % {lmul_map_d2_name}) != 'h0 ? 1 : 0;\n"
        elif ref2 == "lmul1_4":
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % {lmul_map_d4_name}) != 'h0 ? 1 : 0;\n"
        elif ref2 == "lmul1_8":
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % {lmul_map_d8_name}) != 'h0 ? 1 : 0;\n"
        elif ref2 in ["2", "4", "8"]:
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % {ref2}) != 'h0 ? 1 : 0;\n"
        elif ref2 == "nfields":
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = ({ref_signal} % nfields) != 'h0 ? 1 : 0;\n"
    
    return text_context

def reg_index_alignment_assertion(instr_name, df, i, match, mask):
    """生成寄存器索引对齐断言"""
    text_context = "//reg index alignment\n"
    text_context += f"logic {instr_name}_reg_index_alignment_expt_con;\n"
    
    con_str = f"assign {instr_name}_reg_index_alignment_expt_con = "
    start_col_num = reg_index_alignment_num - 1
    
    align_list = [
        ("vd", "lmul"), ("vd", "2lmul"), ("vd", "emul"),
        ("vs2", "lmul"), ("vs2", "emul"), ("vs2", "2lmul"),
        ("vs2", "lmul1_2"), ("vs2", "lmul1_4"), ("vs2", "lmul1_8"),
        ("vs1", "lmul"), ("vs1", "emul"),
        ("vd", "2"), ("vd", "4"), ("vd", "8"),
        ("vs2", "2"), ("vs2", "4"), ("vs2", "8"),
        ("vs3", "2"), ("vs3", "4"), ("vs3", "8"), ("vs3", "nfields")
    ]
    
    for ref1, ref2 in align_list:
        if start_col_num >= len(df.columns):
            flag = ""
        else:
            flag = df.iloc[i, start_col_num]
        
        if "1" in str(flag):
            text_context += reg_index_alignment_sub_con(instr_name, ref1, ref2)
        else:
            text_context += f"assign {instr_name}_reg_index_alignment_{ref1}_{ref2} = 0;\n"
        
        con_str += f"{instr_name}_reg_index_alignment_{ref1}_{ref2} || "
        start_col_num += 1
    
    text_context += con_str[:-3] + ";\n"
    no_unsupport_flag = no_unsupport_flag_func(df, i, reg_index_alignment_num - 1, 20)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_reg_index_alignment: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_reg_index_alignment_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def emul_eew_value(instr_name, df, i, match, mask):
    """生成EMUL和EEW相关信号"""
    text_context = "//emul and eew calculation\n"
    
    text_context += f"logic is_{instr_name};\n"
    text_context += f"assign is_{instr_name} = (" + opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ f";\n"
    text_context += f"asm_{instr_name}_eew: assume property( "
    text_context += f"is_{instr_name} |-> eew == {instr_name}_eew);\n"
    try:
        # 获取eew配置
        flag0 = df.iloc[i, eew_num - 1] if (eew_num - 1) < len(df.columns) else ""  # eew=16
        flag1 = df.iloc[i, eew_num] if eew_num < len(df.columns) else ""           # eew=width[2:0]
        
        text_context += f"logic [4:0] {instr_name}_eew;\n"
        if "1" in str(flag0):
            text_context += f"assign {instr_name}_eew = 'b01;\n"
        elif "1" in str(flag1):
            text_context += f"assign {instr_name}_eew = width_map;\n"
            text_context += f"asm_{instr_name}_width: assume property( is_{instr_name} |-> width inside" + "{3'b000, 3'b101, 3'b110, 3'b111});\n"
        else:
            text_context += f"assign {instr_name}_eew = {sew_rtl_name};\n"
        
        #  1/8 <= emul <= 8
        text_context += f"logic {instr_name}_emul_check;"
        text_context += f"assign {instr_name}_emul_check = "
        text_context += f"is_{instr_name} && (((emul_x8 > 'd64) && (emul_x8 != 'hffff)) || emul_x8 == 'hffff);\n"
        # 计算emul = lmul * eew / sew
        text_context += f"logic [4:0] {instr_name}_emul;\n"
        text_context += f"logic [4:0] {instr_name}_sew_eew_diff_val;\n"
        text_context += f"assign {instr_name}_sew_eew_diff_val = {instr_name}_emul;\n"
        # text_context += f"assign {instr_name}_emul = ({lmul_rtl_name} * {instr_name}_eew) / {sew_rtl_name};\n"
        
    except Exception as e:
        # 如果EEW列不存在，使用默认值
        text_context += f"logic [4:0] {instr_name}_eew = {sew_rtl_name};\n"
        text_context += f"logic [4:0] {instr_name}_emul = {lmul_rtl_name};\n"
    
    text_context += "\n"
    return text_context

def overlap_constain0(instr_name, df, i, match, mask):
    """生成重叠约束0断言"""
    text_context = "//overlap constrain 0: if(lmul<1) overlap($); else overlap_widen($)\n"
    text_context += f"logic {instr_name}_overlap_constain0_expt_con;\n"
    
    con_str = f"assign {instr_name}_overlap_constain0_expt_con = "
    start_col_num = overlap_constain0_num - 1
    
    for item in ["a", "b"]:
        if start_col_num >= len(df.columns):
            flag = ""
        else:
            flag = df.iloc[i, start_col_num]
        
        text_context += f"logic {instr_name}_overlap_constain0_{item}_expt;\n"
        
        if "1" in str(flag):
            if item == "a":
                # (vd, lmul*2, vs2, lmul)
                param_str = f"{vd_rtl_name}, {lmul_map_m2_name}, {vs2_rtl_name}, {lmul_map_name}"
                text_context += f"assign {instr_name}_overlap_constain0_{item}_expt = ({lmul_rtl_name}[2] == 1'b1) ? overlap({param_str}) : overlap_widen({param_str});\n"
            elif item == "b":
                # (vd, lmul*2, vs1, lmul)
                param_str = f"{vd_rtl_name}, {lmul_map_m2_name}, {vs1_rtl_name}, {lmul_map_name}"
                text_context += f"assign {instr_name}_overlap_constain0_{item}_expt = ({lmul_rtl_name}[2] == 1'b1) ? overlap({param_str}) : overlap_widen({param_str});\n"
        else:
            text_context += f"assign {instr_name}_overlap_constain0_{item}_expt = 0;\n"
        
        con_str += f"{instr_name}_overlap_constain0_{item}_expt || "
        start_col_num += 1
    
    text_context += con_str[:-3] + ";\n"
    no_unsupport_flag = no_unsupport_flag_func(df, i, overlap_constain0_num - 1, 2)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_overlap_constain0: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_overlap_constain0_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def overlap_constain1(instr_name, df, i, match, mask):
    """生成重叠约束1断言"""
    text_context = "//overlap constrain 1: if($<1) overlap(vd,lmul,vs2,$); else overlap_widen((vd,lmul,vs2,$)\n"
    text_context += f"logic {instr_name}_overlap_constain1_expt_con;\n"
    
    con_str = f"assign {instr_name}_overlap_constain1_expt_con = "
    start_col_num = overlap_constain1_num - 1
    
    for item, divisor in [("a", 2), ("b", 4), ("c", 8)]:
        if start_col_num >= len(df.columns):
            flag = ""
        else:
            flag = df.iloc[i, start_col_num]
        
        text_context += f"logic {instr_name}_overlap_constain1_{item}_expt;\n"
        
        if "1" in str(flag):
            lmul_div = f"({lmul_map_name} < {divisor})"
            if divisor == 2:
                param_str = f"{vd_rtl_name}, {lmul_map_name}, {vs2_rtl_name}, {lmul_map_d2_name}"
            elif divisor == 4:
                param_str = f"{vd_rtl_name}, {lmul_map_name}, {vs2_rtl_name}, {lmul_map_d4_name}"
            elif divisor == 8:
                param_str = f"{vd_rtl_name}, {lmul_map_name}, {vs2_rtl_name}, {lmul_map_d8_name}"
            text_context += f"assign {instr_name}_overlap_constain1_{item}_expt = ({lmul_div}) ? overlap({param_str}) : overlap_widen({param_str});\n"
        else:
            text_context += f"assign {instr_name}_overlap_constain1_{item}_expt = 0;\n"
        
        con_str += f"{instr_name}_overlap_constain1_{item}_expt || "
        start_col_num += 1
    
    text_context += con_str[:-3] + ";\n"
    no_unsupport_flag = no_unsupport_flag_func(df, i, overlap_constain1_num - 1, 3)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_overlap_constain1: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_overlap_constain1_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def reg_index_not_equal(instr_name, df, i, match, mask):
    """生成寄存器索引不相等断言"""
    text_context = "//register index not equal\n"
    text_context += f"logic {instr_name}_reg_index_not_equal_expt_con;\n"
    
    con_str = f"assign {instr_name}_reg_index_not_equal_expt_con = "
    start_col_num = reg_index_not_equal_num - 1
    
    # 寄存器索引不相等条件列表
    cond_list = [
        ("vd_ne_vs2", "vd != vs2"),
        ("vd_ne_vs2_vs1", "vd != vs2 && vd != vs1"),
        ("vd_ne_vs2_overlap1", "if(vd != vs2) overlap(vd, 1, vs2, lmul)"),
        ("vd_ne_vs2_overlap2", "if(vd != vs2) overlap(vd, 1, vs2, lmul*2)"),
        ("vd_ne_vs1_overlap", "if(vd != vs1) overlap(vd, 1, vs1, lmul)")
    ]
    
    for cond_name, cond_expr in cond_list:
        if start_col_num >= len(df.columns):
            flag = ""
        else:
            flag = df.iloc[i, start_col_num]
        
        text_context += f"logic {instr_name}_{cond_name};\n"
        
        if "1" in str(flag):
            # 根据条件表达式生成逻辑
            if "vd != vs2" in cond_expr and "&&" not in cond_expr and "overlap" not in cond_expr:
                text_context += f"assign {instr_name}_{cond_name} = {vd_rtl_name} == {vs2_rtl_name};\n"
            elif "vd != vs2 && vd != vs1" in cond_expr:
                text_context += f"assign {instr_name}_{cond_name} = ({vd_rtl_name} == {vs2_rtl_name} || {vd_rtl_name} == {vs1_rtl_name});\n"
            elif "overlap" in cond_expr:
                # 处理overlap条件
                if "lmul*2" in cond_expr:
                    text_context += f"assign {instr_name}_{cond_name} = ({vd_rtl_name} != {vs2_rtl_name}) ? overlap({vd_rtl_name}, 1, {vs2_rtl_name}, {lmul_map_m2_name}) : 0;\n"
                elif "vs1" in cond_expr:
                    text_context += f"assign {instr_name}_{cond_name} = ({vd_rtl_name} != {vs1_rtl_name}) ? overlap({vd_rtl_name}, 1, {vs1_rtl_name}, {lmul_map_name}) : 0;\n"
                else:
                    text_context += f"assign {instr_name}_{cond_name} = ({vd_rtl_name} != {vs2_rtl_name}) ? overlap({vd_rtl_name}, 1, {vs2_rtl_name}, {lmul_map_name}) : 0;\n"
        else:
            text_context += f"assign {instr_name}_{cond_name} = 0;\n"
        
        con_str += f"{instr_name}_{cond_name} || "
        start_col_num += 1
    
    text_context += con_str[:-3] + ";\n"
    no_unsupport_flag = no_unsupport_flag_func(df, i, reg_index_not_equal_num - 1, 5)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_reg_index_not_equal: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_reg_index_not_equal_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def other_constrain(instr_name, df, i, match, mask):
    """生成其他约束断言"""
    text_context = "//other constraints\n"
    text_context += f"logic {instr_name}_other_constraint_expt_con;\n"
    
    con_str = f"assign {instr_name}_other_constraint_expt_con = "
    start_col_num = other_constraint_num - 1
    
    # 其他约束条件列表
    other_conds = [
        ("vd_eq_0_lmul_gt_1", "vm == 0 && vd == 0 && lmul > 1"),
        ("overlap_vd_lmul_vs2_1", "overlap(vd, lmul, vs2, 1)"),
        ("overlap_vd_lmul_vs1_1", "overlap(vd, lmul, vs1, 1)"),
        ("overlap_vd_lmul_vs1_emul", "overlap(vd, lmul, vs1, emul)"),
        ("nf_emul_check", "(nfields * emul <= 8) && (vd + nfields * emul <= 32)")
    ]
    
    for cond_name, cond_desc in other_conds:
        if start_col_num >= len(df.columns):
            flag = ""
        else:
            flag = df.iloc[i, start_col_num]
        
        text_context += f"logic {instr_name}_{cond_name};\n"
        
        if "1" in str(flag):
            if "vm == 0 && vd == 0 && lmul > 1" in cond_desc:
                text_context += f"assign {instr_name}_{cond_name} = {vm_rtl_name} == 0 && ({vd_rtl_name} == 0) && ((|{lmul_rtl_name}) && ({lmul_rtl_name}[2]==0));\n"
            elif "overlap(vd, lmul, vs2, 1)" in cond_desc:
                text_context += f"assign {instr_name}_{cond_name} = overlap({vd_rtl_name}, {lmul_map_name}, {vs2_rtl_name}, 1);\n"
            elif "overlap(vd, lmul, vs1, 1)" in cond_desc:
                text_context += f"assign {instr_name}_{cond_name} = overlap({vd_rtl_name}, {lmul_map_name}, {vs1_rtl_name}, 1);\n"
            elif "overlap(vd, lmul, vs1, emul)" in cond_desc:
                text_context += f"assign {instr_name}_{cond_name} = overlap({vd_rtl_name}, {lmul_map_name}, {vs1_rtl_name}, emul_map);\n"
            elif "nfields * emul" in cond_desc:
                text_context += f"assign {instr_name}_{cond_name} = is_index_ldst ? (!(((nfields * lmul_map) <= 'd8) && (({vd_rtl_name} + (nfields * lmul_map ) <= 32)))) : (!(((nfields * emul_map) <= 'd8) && (({vd_rtl_name} + (nfields * emul_map ) <= 32))));\n"
        else:
            text_context += f"assign {instr_name}_{cond_name} = 0;\n"
        
        con_str += f"{instr_name}_{cond_name} || "
        start_col_num += 1
    
    text_context += con_str[:-3] + ";\n"
    no_unsupport_flag = no_unsupport_flag_func(df, i, other_constraint_num - 1, 5)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_other_constrain: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_other_constraint_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def index_load_constrain(instr_name, df, i, match, mask):
    # print("aaaaaa\n")
    """生成index load约束断言"""
    text_context = "//index load constraints\n"
    start_col_num = index_load_constraint_num - 1
    
    flag = df.iloc[i, start_col_num]
    if "1" in str(flag):
        text_context += f'''
logic {instr_name}_dst_not_eq_src;
always @(*) begin
    case (nfields)
      'd1: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map);
      'd2: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map) || overlap_not_eq(vd+1,lmul_map,vs2,emul_map);
      'd3: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map) || overlap_not_eq(vd+1,lmul_map,vs2,emul_map) || overlap_not_eq(vd+2,lmul_map,vs2,emul_map);
      'd4: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map) || overlap_not_eq(vd+1,lmul_map,vs2,emul_map) || overlap_not_eq(vd+2,lmul_map,vs2,emul_map) || overlap_not_eq(vd+3,lmul_map,vs2,emul_map);
      'd5: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map) || overlap_not_eq(vd+1,lmul_map,vs2,emul_map) || overlap_not_eq(vd+2,lmul_map,vs2,emul_map) || overlap_not_eq(vd+3,lmul_map,vs2,emul_map) || overlap_not_eq(vd+4,lmul_map,vs2,emul_map);
      'd6: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map) || overlap_not_eq(vd+1,lmul_map,vs2,emul_map) || overlap_not_eq(vd+2,lmul_map,vs2,emul_map) || overlap_not_eq(vd+3,lmul_map,vs2,emul_map) || overlap_not_eq(vd+4,lmul_map,vs2,emul_map) || overlap_not_eq(vd+5,lmul_map,vs2,emul_map);
      'd7: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map) || overlap_not_eq(vd+1,lmul_map,vs2,emul_map) || overlap_not_eq(vd+2,lmul_map,vs2,emul_map) || overlap_not_eq(vd+3,lmul_map,vs2,emul_map) || overlap_not_eq(vd+4,lmul_map,vs2,emul_map) || overlap_not_eq(vd+5,lmul_map,vs2,emul_map) || overlap_not_eq(vd+6,lmul_map,vs2,emul_map);
      'd8: {instr_name}_dst_not_eq_src = overlap_not_eq(vd,lmul_map,vs2,emul_map) || overlap_not_eq(vd+1,lmul_map,vs2,emul_map) || overlap_not_eq(vd+2,lmul_map,vs2,emul_map) || overlap_not_eq(vd+3,lmul_map,vs2,emul_map) || overlap_not_eq(vd+4,lmul_map,vs2,emul_map) || overlap_not_eq(vd+5,lmul_map,vs2,emul_map) || overlap_not_eq(vd+6,lmul_map,vs2,emul_map) || overlap_not_eq(vd+7,lmul_map,vs2,emul_map);
    endcase
    end

logic {instr_name}_eew_gt_sew_check;
assign {instr_name}_eew_gt_sew_check = (eew > sew) ? {instr_name}_dst_not_eq_src : 0;
logic [8:0] {instr_name}_vd_overflow_index;
assign {instr_name}_vd_overflow_index = vd + (nfields * lmul_map) ;
logic {instr_name}_eew_lt_sew_check;
assign {instr_name}_eew_lt_sew_check = (eew < sew) ? ((emul_x8 < 'd8) ? overlap_contiguous(vd,lmul_map,vs2,emul_map,lmul_map,nfields) : overlap_widen_contiguous(vd,lmul_map,vs2,emul_map,lmul_map,nfields)) : 0;
logic {instr_name}_nfields_gt_eq_2;
assign {instr_name}_nfields_gt_eq_2 = (nfields >=2) ? overlap_contiguous(vd,lmul_map,vs2,emul_map,lmul_map,nfields): 0;
logic {instr_name}_index_load_constraint_expt_con;
assign {instr_name}_index_load_constraint_expt_con = {instr_name}_eew_gt_sew_check || {instr_name}_eew_lt_sew_check || {instr_name}_nfields_gt_eq_2;
'''
    else:
        text_context += f"assign {instr_name}_index_load_constraint_expt_con = 0;\n"

    
    no_unsupport_flag = no_unsupport_flag_func(df, i, index_load_constraint_num - 1, 1)
    if no_unsupport_flag == 1:
        text_context += '//'
    text_context += f"ast_{instr_name}_index_load_constrain: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_index_load_constraint_expt_con |-> {expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def generate_all_constraints(instr_name, df, i, match, mask):
    """生成所有约束的总断言"""
    text_context = "//all constraints combined\n"
    text_context += f"logic {instr_name}_all_constraints_expt_con;\n"
    text_context += f"assign {instr_name}_all_constraints_expt_con = "
    # text_context += f"{instr_name}_vm_not_eq_1_expt_con || "
    # text_context += f"{instr_name}_vm_vd_eq_0_expt_con || "
    # text_context += f"{instr_name}_vstart_not_eq_0_expt_con || "
    text_context += f"{instr_name}_unsupported_sew_expt_con || "
    text_context += f"{instr_name}_emul_check || "
    text_context += f"{instr_name}_unsupported_lmul_expt_con || "
    text_context += f"{instr_name}_reg_index_alignment_expt_con || "
    text_context += f"{instr_name}_overlap_constain0_expt_con || "
    text_context += f"{instr_name}_overlap_constain1_expt_con || "
    text_context += f"{instr_name}_reg_index_not_equal_expt_con || "
    text_context += f"{instr_name}_index_load_constraint_expt_con || "
    text_context += f"{instr_name}_other_constraint_expt_con;\n"
    
    no_cons_flag = df.iloc[i, no_constraint_num - 1]
    # print(f"no_cons_flag={no_cons_flag}")
    if str(no_cons_flag) == "0":
        text_context += '//'
    text_context += f"ast_{instr_name}_all_constraints: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"{instr_name}_all_constraints_expt_con |-> {expt_rtl_name});\n"

    text_context += "//all constraints combined reversion\n"
    text_context += f"ast_{instr_name}_all_constraints_rev: assert property( (("
    text_context += opcode_rtl_name+ " & "+ str(mask).replace("0x", "32'h")+ ") == "+ str(match).replace("0x", "32'h")+ ") && "
    text_context += f"!{instr_name}_all_constraints_expt_con |-> !{expt_rtl_name});\n"
    
    text_context += "\n"
    return text_context

def main():
    """主函数"""
    print("=" * 60)
    print("RVV指令trap测试断言生成工具")
    print("=" * 60)
    
    try:
        # 读取CSV文件
        df = read_full_dataframe(csv_path)
        print(f"成功读取CSV文件，共{len(df)}行数据，{len(df.columns)}列")
        
        final_text = ""
        final_text += "// ==============================================\n"
        final_text += "// RVV指令trap测试断言自动生成\n"
        final_text += "// Generated by gen_trap_test_assertion.py\n"
        final_text += "// ==============================================\n\n"
        
        # 获取指令列表
        if "instr" not in df.columns:
            print("CSV文件中未找到'instr'列", file=sys.stderr)
            sys.exit(1)
        
        instr_list = df["instr"].tolist()
        row_len = len(instr_list)
        print(f"发现{row_len}条指令记录")
        
        generated_count = 0
        for i in range(started_row - 1, row_len):
            is_ready = df.iloc[i, is_ready_num - 1]
            if pd.isna(instr_list[i]) or instr_list[i] == "" or str(is_ready) == "no":
                continue
                
            # 获取match和mask
            match = df.iloc[i, match_num - 1]
            mask = df.iloc[i, mask_num - 1]
            # print(fr"mask={mask},match={match}")
                
            
            if pd.isna(match) or pd.isna(mask):
                continue
                
            # 清理指令名称，使其适合作为标识符
            instr_name = instr_list[i].replace(".", "_").replace("<", "_").replace(">", "_").replace("*", "_star_").replace(" ", "_")
            
            # 添加指令分隔符
            tmp_str = f"\n/*{'='*70} {instr_name} {'='*70}*/\n"
            final_text += tmp_str
            
            try:
                # 按顺序生成各种断言
                # 1. EMUL和EEW计算
                final_text += emul_eew_value(instr_name, df, i, match, mask)
                
                # 2. vm != 1 (trap)
                # if vm_not_eq_1_num <= len(df.columns):
                #     flag = df.iloc[i, vm_not_eq_1_num - 1]
                #     final_text += vm_not_eq_1_assertion(instr_name, flag, match, mask)
                
                # 3. vm == 0时vd == 0 (trap)
                # if vm_eq_1_vd_eq_1_num <= len(df.columns):
                #     flag = df.iloc[i, vm_eq_1_vd_eq_1_num - 1]
                #     final_text += vm_vd_eq_0_assertion(instr_name, flag, match, mask)
                
                # 4. vstart != 0 (trap)
                # if vstart_not_eq_0_num <= len(df.columns):
                #     flag = df.iloc[i, vstart_not_eq_0_num - 1]
                #     final_text += vstart_not_eq_0_assertion(instr_name, flag, match, mask)
                
                # 5. 不支持的SEW
                if unsupported_sew_num <= len(df.columns):
                    final_text += unsupported_sew_assertion(instr_name, df, i, match, mask)
                
                # 6. 不支持的LMUL
                if unsupported_lmul_num <= len(df.columns):
                    final_text += unsupported_lmul_assertion(instr_name, df, i, match, mask)
                
                # 7. 寄存器索引对齐
                if reg_index_alignment_num <= len(df.columns):
                    final_text += reg_index_alignment_assertion(instr_name, df, i, match, mask)
                
                # 8. 重叠约束0
                if overlap_constain0_num <= len(df.columns):
                    final_text += overlap_constain0(instr_name, df, i, match, mask)
                
                # 9. 重叠约束1
                if overlap_constain1_num <= len(df.columns):
                    final_text += overlap_constain1(instr_name, df, i, match, mask)
                
                # 10. 寄存器索引不相等
                if reg_index_not_equal_num <= len(df.columns):
                    final_text += reg_index_not_equal(instr_name, df, i, match, mask)
                
                # 11. 其他约束
                if other_constraint_num <= len(df.columns):
                    final_text += other_constrain(instr_name, df, i, match, mask)
                
                # 11. 其他约束
                if index_load_constraint_num <= len(df.columns):
                    final_text += index_load_constrain(instr_name, df, i, match, mask)
                
                # 13. 所有约束组合
                final_text += generate_all_constraints(instr_name, df, i, match, mask)
                
                generated_count += 1
                # print(f"[{generated_count}] 已生成 {instr_name} 的断言")
                
            except Exception as e:
                print(f"生成 {instr_name} 的断言时出错: {e}")
                continue
        
        # 保存到文件
        output_file = "rvv_trap_assertions.sv"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_text)
        
        print("\n" + "=" * 60)
        print("断言生成完成！")
        print(f"输出文件: {output_file}")
        print(f"总共生成了 {generated_count} 条指令的断言")
        print(f"生成代码总行数: {len([line for line in final_text.splitlines() if line.strip()])}")
        print("=" * 60)
        
    except Exception as e:
        print(f"程序执行出错: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()