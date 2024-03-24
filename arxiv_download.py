import requests
import os
from datetime import datetime
import time
from bs4 import BeautifulSoup
from lxml import etree

# arXiv基础URL和参数
BASE_URL = 'http://export.arxiv.org'

Physics = ['astro-ph', 'cond-mat', 'gr-qc', 'hep-ex', 'hep-lat', 'hep-ph', 'hep-th', 'math-ph', 'nlin', 'nucl-ex', 'nucl-th', 'physics', 'quant-ph']
Mathematics = ['math']
Computer_Science = ['cs']
Quantitative_Biology = ['q-bio']
Quantitative_Finance = ['q-fin']
Statistics = ['stat']
Economics = ['econ']
Electrical_Engineering_and_Systems_Science = ['eess']

Subjects = [Physics, Mathematics, Computer_Science, Quantitative_Biology, Quantitative_Finance, Statistics, Economics, Electrical_Engineering_and_Systems_Science]
Subjects_name = ['Physics', 'Mathematics', 'Computer_Science', 'Quantitative_Biology', 'Quantitative_Finance', 'Statistics', 'Economics', 'Electrical_Engineering_and_Systems_Science']

# 设定请求限制
SLEEP_TIME = 1

def get_arxiv_ids(set):
    query = f'/list/{set}/new?skip=0&show=2000'
    response = requests.get(BASE_URL + query)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        arxiv_ids = [span.a.text.replace('arXiv:', '') for span in soup.find_all('span', class_='list-identifier')]

        return arxiv_ids
    else:
        print(f"Error: {response.status_code}")
        return None

def create_directory_for_today():
    today = datetime.now().strftime('%Y-%m-%d')
    today_dir = os.path.join("./Downloads/"+today)
    if not os.path.exists(today_dir):
        os.makedirs(today_dir)
    return today_dir

def download_metadata_and_pdf(arxiv_id, dir):
    metadata = f"http://export.arxiv.org/api/query?search_query=id:{arxiv_id}"
    ep = f"https://export.arxiv.org/e-print/{arxiv_id}"
    pdf = f"https://export.arxiv.org/pdf/{arxiv_id}"
    meta_response = requests.get(metadata)
    if meta_response.status_code == 200:
        # 获取响应内容
        content = meta_response.content
        
        # 解析响应内容为XML
        tree = etree.fromstring(content)
        
        # 查找所有entry节点
        entries = tree.findall('{http://www.w3.org/2005/Atom}entry')
        
        # 为输出创建新的XML根节点
        new_root = etree.Element('feed')
        
        # 将每个找到的entry节点添加到新的根节点下
        for entry in entries:
            new_root.append(entry)
        
        # 创建新的XML树
        new_tree = etree.ElementTree(new_root)
        
        # 写入文件
        with open(os.path.join(dir, arxiv_id + '.xml'), 'wb') as f:
            new_tree.write(f, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        stat_meta = 1
    else:
        stat_meta = 0

    ep_response = requests.get(ep)
    if ep_response.status_code == 200:
        # 假设我们不确定源文件的确切类型，这里直接保存为tar.gz文件，这对于大多数情况是对的。
        with open(os.path.join(dir, arxiv_id + ".tar.gz"), 'wb') as f:
            f.write(ep_response.content)
        stat_ep = 1
    else:
        stat_ep = 0

    pdf_response = requests.get(pdf)
    if pdf_response.status_code == 200:
        with open(os.path.join(dir, arxiv_id + '.pdf'), 'wb') as f:
            f.write(pdf_response.content)
        stat_pdf = 1
    else:
        stat_pdf = 0

    return [arxiv_id, stat_meta, stat_ep, stat_pdf]


def main():
    today_dir = create_directory_for_today()
    if today_dir is None:
        print("Today's directory already exists, continue!")
    for SETS, SETS_name in zip(Subjects, Subjects_name):
        print(f"Downloading {SETS_name} sets ...")
        SETS_dir = os.path.join(today_dir, SETS_name)
        if not os.path.exists(SETS_dir):
            os.makedirs(SETS_dir)
        for sub_set in SETS:
            print(f"Downloading {sub_set} set ..")
            state_list = []
            set_dir = os.path.join(SETS_dir, sub_set)
            os.makedirs(set_dir, exist_ok=True)
            arxiv_ids = get_arxiv_ids(sub_set)
            if arxiv_ids is None:
                print(f"Error: {sub_set} set not found!")
                continue
            for arxiv_id in arxiv_ids:
                print(f"Downloading {arxiv_id}")
                paper_dir = os.path.join(set_dir, arxiv_id)
                if not os.path.exists(paper_dir):
                    os.makedirs(paper_dir, exist_ok=True)
                    # 这里添加下载元数据和PDF的代码
                    download_status = download_metadata_and_pdf(arxiv_id, paper_dir)
                    print(download_status)
                    state_list.append(str(download_status))
                    
                    time.sleep(SLEEP_TIME)
                else:
                    print(f"{arxiv_id} already exists, skipping!")
                    state_list.append(str([arxiv_id, 2]))
            with open(os.path.join(set_dir, 'dl_state.txt'), 'w') as f:
                    f.writelines(state_list)
        time.sleep(10)
    print(today_dir + "All sets downloaded!")

if __name__ == "__main__":
    main()




