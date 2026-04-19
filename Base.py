import streamlit as st
import pandas as pd

def check_dates(data):
    issues = []
    
    # 安全检查：确保DataFrame至少有2列
    if data.shape[1] < 2:
        issues.append("错误：数据必须包含至少两列（开始时间、结束时间）")
        return issues

    for i in range(len(data)):
        try:
            # ✅ 安全取第1列、第2列（不会触发KeyError）
            start_val = data.iloc[i, 0]
            end_val = data.iloc[i, 1]

            # 转成时间类型（正确比较大小）
            start = pd.to_datetime(start_val, errors="coerce")
            end = pd.to_datetime(end_val, errors="coerce")

            # 空值检查
            if pd.isna(start) or pd.isna(end):
                issues.append(f"时间格式错误或为空：行 {i+1}")
                continue

            # ✅ 正确的时间比较
            if start >= end:
                issues.append(f"开始时间晚于结束时间：行 {i+1}")
                issues.append(f"出错时间为：{start_val}  |  {end_val}")

        except Exception as e:
            issues.append(f"行 {i+1} 数据异常：{str(e)}")

    return issues


def check_cross_dates(data):
    issues = []
    
    # 安全检查：确保至少有2列
    if data.shape[1] < 2:
        issues.append("错误：数据必须包含至少两列（开始时间、结束时间）")
        return issues

    # 遍历所有时间对
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            try:
                # ✅ 绝对安全取值，不会报 KeyError
                start1_val = data.iloc[i, 0]
                end1_val = data.iloc[i, 1]
                start2_val = data.iloc[j, 0]
                end2_val = data.iloc[j, 1]

                # ✅ 转成时间类型（正确判断交叉）
                start1 = pd.to_datetime(start1_val, errors="coerce")
                end1 = pd.to_datetime(end1_val, errors="coerce")
                start2 = pd.to_datetime(start2_val, errors="coerce")
                end2 = pd.to_datetime(end2_val, errors="coerce")

                # 时间格式错误直接跳过并提示
                if pd.isna(start1) or pd.isna(end1) or pd.isna(start2) or pd.isna(end2):
                    issues.append(f"行 {i+1} 或 行 {j+1} 时间格式错误/为空")
                    continue

                # ✅ 正确的时间交叉判断
                if start1 < end2 and start2 < end1:
                    issues.append(f"时间交叉：行 {i+1} 和 行 {j+1}")
                    issues.append(f"交叉时间为：{start1_val}  {end1_val}  |  {start2_val}  {end2_val}")

            except Exception as e:
                issues.append(f"行 {i+1} 与 行 {j+1} 数据异常：{str(e)}")

    return issues

def check_project_within_work(work_data, proj_data):
    """检查项目时间是否在工作时间内（修复版：安全、无KeyError、时间正确比较）"""
    issues = []

    # 安全检查：确保数据有至少两列
    if work_data.shape[1] < 2 or proj_data.shape[1] < 2:
        issues.append("错误：工作时间/项目时间数据必须包含至少两列（开始、结束）")
        return issues

    # 遍历项目行
    for i, proj_row in proj_data.iterrows():
        try:
            # ✅ 安全取时间（绝对不会报 KeyError）
            proj_start_val = proj_row.iloc[0]
            proj_end_val = proj_row.iloc[1]

            # ✅ 转成真正的时间类型
            proj_start = pd.to_datetime(proj_start_val, errors="coerce")
            proj_end = pd.to_datetime(proj_end_val, errors="coerce")

            # 检查时间是否有效
            if pd.isna(proj_start) or pd.isna(proj_end):
                issues.append(f"项目时间格式错误/为空：行 {i+2}")
                continue

            in_work_time = False

            # 遍历工作时间
            for _, work_row in work_data.iterrows():
                work_start_val = work_row.iloc[0]
                work_end_val = work_row.iloc[1]

                work_start = pd.to_datetime(work_start_val, errors="coerce")
                work_end = pd.to_datetime(work_end_val, errors="coerce")

                if pd.isna(work_start) or pd.isna(work_end):
                    continue

                # ✅ 正确的时间范围判断
                if proj_start >= work_start and proj_end <= work_end:
                    in_work_time = True
                    break

            if not in_work_time:
                issues.append(f"项目不在工作时间范围内：行 {i+2} 开始时间：{proj_start_val}，结束时间：{proj_end_val}")

        except Exception as e:
            issues.append(f"项目行 {i+2} 数据异常：{str(e)}")

    return issues

def check_file(file_name):  
    try:
        df = pd.read_excel(file_name)
    except Exception as e:
        st.error(f"读取Excel失败：{str(e)}")
        return

    work_start_index = None
    work_end_index = None
    proj_start_index = None
    proj_end_index = None

    # 🔥 关键修复：一次循环找完所有标记，不乱序
    for index, row in df.iterrows():
        cell = str(row.values).strip()

        # 匹配工作经历（支持长标题）
        if "工作经历" in cell and work_start_index is None:
            work_start_index = index

        # 匹配项目经历
        if "项目经历" in cell and work_end_index is None:
            work_end_index = index
            proj_start_index = index

        # 匹配技术特长
        if "技术特长" in cell:
            proj_end_index = index
            break  # 找到最后一个标记就停

    # 打印定位信息，方便你看问题
    st.write("工作经历行：", work_start_index)
    st.write("项目经历行：", work_end_index)
    st.write("技术特长行：", proj_end_index)

    if None in [work_start_index, work_end_index, proj_end_index]:
        st.error("未找到 工作经历/项目经历/技术特长 标记")
        return

    # 🔥 再微调偏移量（根据你的实际模板）
    work_data = df.iloc[work_start_index + 2: work_end_index, [0, 1]]
    proj_data = df.iloc[proj_start_index + 2: proj_end_index, [0, 1]]

    work_data = work_data.dropna()
    proj_data = proj_data.dropna()

    st.subheader("工作经历")
    st.dataframe(work_data)
    st.subheader("项目经历")
    st.dataframe(proj_data)

    # 下面检查逻辑不变
    base_issues = check_dates(work_data)
    base_issues1 = check_dates(proj_data)
    work_issues = check_cross_dates(work_data)
    proj_within_work_issues = check_project_within_work(work_data, proj_data)

    if base_issues:
        st.error("\n".join(base_issues))
    else:
        st.success("工作经历日期基本检查无问题")

    if base_issues1:
        st.error("\n".join(base_issues1))
    else:
        st.success("项目经历日期基本检查无问题")

    if work_issues:
        st.error("\n".join(work_issues))
    else:
        st.success("工作经历无时间交叉")

    if proj_within_work_issues:
        st.error("\n".join(proj_within_work_issues))
    else:
        st.success("项目时间都在工作时间范围内")
    
# 页面标题和图标
st.set_page_config(page_title="日期检查工具", page_icon=":file-ear-docx:")


#try:
#    while True:
# 创建一个文件上传器
uploaded_files = st.file_uploader("选择一个表格文件",  accept_multiple_files=True,type=["xlsx", "xls"])
# 提供重置功能
if st.button("清空已上传文件"):
    st.session_state["uploaded_files"] = []
    st.success("已清空所有上传记录。")    

# 创建一个按钮来控制输出
if st.button("清空输出"):
    st.session_state.clear()  # 清空会话状态

# 显示一些输出
if 'output' in st.session_state:
    st.write(st.session_state.output)
    
if st.button("重新加载"):
    st.experimental_rerun()    
    
for uploaded_file in  uploaded_files:
    # 如果用户上传了文件，处理文件
    st.write(f"正在处理文件：{uploaded_file.name}")
    if uploaded_file is not None:
        check_file(uploaded_file)
#except KeyboardInterrupt:
 #   print("循环被用户中断。")
    

