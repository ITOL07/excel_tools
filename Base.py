import streamlit as st
import pandas as pd

def check_dates(data):
    """检查时间交叉的逻辑"""
    issues = []
    for i in range(len(data)):
        start, end = str(data.iloc[i][0]), str(data.iloc[i][1])
        if start >= end :
            issues.append(f"开始时间晚于结束时间：行 {i+1} ")
            issues.append(f"出错时间为："+start+"  " + end)
    return issues


def check_cross_dates(data):
    """检查时间交叉的逻辑"""
    issues = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            start1, end1 = str(data.iloc[i][0]), str(data.iloc[i][1])
            start2, end2 = str(data.iloc[j][0]), str(data.iloc[j][1])
            if start1 <= end2 and start2 <= end1:
                issues.append(f"时间交叉：行 {i+1} 和行 {j+1} ")
                issues.append(f"交叉时间为："+start1+"  " + end1+ "  " + start2 +"  " +end2)
    return issues

def check_project_within_work(work_data, proj_data):
    """检查项目时间是否在工作时间内"""
    issues = []
    for i, proj_row in proj_data.iterrows():
        proj_start, proj_end = str(proj_row[0]), str(proj_row[1])
        in_work_time = False
        for _, work_row in work_data.iterrows():
            work_start, work_end = str(work_row[0]), str(work_row[1])
            if proj_start >= work_start and proj_end <= work_end:
                in_work_time = True
                break
        if not in_work_time:
            issues.append(f"项目不在工作时间范围内：行 {i+2} 开始时间：" + proj_start + " ，结束时间：" + proj_end)
    return issues

def check_file(file_name):  
    # 读取Excel文件
    #file_path = 'C:/Users/nantian/Desktop/2024111-人员输送建议信息模板V1.9（更新首次参加IT领域工作时间）--待修改.xlsx'

    #df = pd.read_excel(file_name,sheet_name="人员输送建议信息模板")
    df = pd.read_excel(file_name)
    
    # 查找“工作经历”和“项目经历”的索引
    work_start_index = None
    work_end_index = None

    proj_start_index = None
    proj_end_index = None

    for index, row in df.iterrows():
        if '工作经历' in str(row.values):
            work_start_index = index
            break

    for index, row in df.iterrows():
        if '项目经历' in str(row.values):
            work_end_index = index
            proj_start_index = index + 1
            break

    for index, row in df.iterrows():
        if '技术特长' in str(row.values):
            proj_end_index = index
            break
            
    # 检查是否找到了起始和结束索引
    if work_start_index is not None and work_end_index is not None and proj_start_index is not None and proj_end_index is not None:
        # 读取“工作经历”和“项目经历”之间的行,只要前两列
        work_data = df.iloc[work_start_index + 2:work_end_index,[0,1]]
        proj_data = df.iloc[proj_start_index + 1:proj_end_index,[0,1]]
        
        work_data = work_data.dropna()
        proj_data = proj_data.dropna()
        st.write(work_data)
        st.write(proj_data)
        
        base_issues=check_dates(work_data)
        base_issues1=check_dates(proj_data)
        work_issues=check_cross_dates(work_data)
        proj_within_work_issues=check_project_within_work(work_data,proj_data)

        # 显示结果
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
            st.success("工作经历检查无问题")

        if proj_within_work_issues:
            st.error("\n".join(proj_within_work_issues))
        else:
            st.success("项目时间包含在工作时间范围内")    
    else:
        st.write("未能找到'工作经历'或'项目经历'的标记。")

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
    

