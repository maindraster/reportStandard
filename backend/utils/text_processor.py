import re
from typing import List, Tuple
from datetime import datetime

class TextProcessor:
    def __init__(self):
        self.rows_per_page = 20
        self.cols_per_row = 20
        self.chars_per_page = 400
        
    def process_text(self, text: str, reporter_name: str = "XXX", report_date: str = "") -> List[List[List[str]]]:
        """
        处理文本，返回多页格式化后的内容
        返回格式: [页面][行][列]
        """
        # 清理文本
        text = text.strip()
        if not text:
            return []
        
        # 处理文本内容
        formatted_chars = self._format_content(text, reporter_name, report_date)
        
        # 分页
        pages = self._paginate(formatted_chars)
        
        return pages
    
    def _format_content(self, text: str, reporter_name: str, report_date: str) -> List[str]:
        """格式化全部内容"""
        formatted_chars = []
        
        # 第一行：居中显示"思想汇报"
        first_row = [''] * 20
        title = "思想汇报"
        for i, char in enumerate(title):
            first_row[8 + i] = char  # 第9-12个位置（索引8-11）
        formatted_chars.extend(first_row)
        
        # 第二行：开头显示"敬爱的党组织："
        second_row = [''] * 20
        greeting = "敬爱的党组织："
        for i, char in enumerate(greeting):
            if i < 20:
                second_row[i] = char
        formatted_chars.extend(second_row)
        
        # 第三行开始：用户文本内容
        user_content = self._process_user_text(text)
        formatted_chars.extend(user_content)
        
        # 添加结尾
        ending = self._format_ending(reporter_name, report_date)
        formatted_chars.extend(ending)
        
        return formatted_chars
    
    def _process_user_text(self, text: str) -> List[str]:
        """处理用户文本"""
        formatted_chars = []
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        for paragraph in paragraphs:
            paragraph_start = len(formatted_chars)
            
            # 段落开头空两格
            formatted_chars.extend(['　', '　'])
            
            # 处理段落中的每个字符，包括连续数字
            i = 0
            while i < len(paragraph):
                char = paragraph[i]
                
                # 检查是否是连续数字的开始
                if char.isdigit() and i + 1 < len(paragraph) and paragraph[i + 1].isdigit():
                    # 找到连续数字的结束位置
                    j = i
                    while j < len(paragraph) and paragraph[j].isdigit():
                        j += 1
                    
                    # 处理连续数字，每两个数字占一格
                    numbers = paragraph[i:j]
                    for k in range(0, len(numbers), 2):
                        if k + 1 < len(numbers):
                            # 两个数字占一格
                            formatted_chars.append(numbers[k] + numbers[k + 1])
                        else:
                            # 单个数字占一格
                            formatted_chars.append(numbers[k])
                    
                    i = j
                elif char in '，。！？；：""''（）《》【】':
                    # 标点符号单独占一格
                    formatted_chars.append(char)
                    i += 1
                elif char == ' ':
                    # 空格转换为全角空格
                    formatted_chars.append('　')
                    i += 1
                else:
                    # 普通字符
                    formatted_chars.append(char)
                    i += 1
            
            # 计算当前段落的字符数
            paragraph_length = len(formatted_chars) - paragraph_start
            
            # 只有当段落长度不是20的倍数时才添加换行
            if paragraph_length % 20 != 0:
                formatted_chars.append('\n')
        
        return formatted_chars
  
    def _format_ending(self, reporter_name: str, report_date: str) -> List[str]:
        """格式化结尾部分"""
        formatted_chars = []
        
        # 处理日期
        if report_date:
            # 用户提供了日期，解析格式
            try:
                # 尝试解析不同的日期格式
                if len(report_date) == 8 and report_date.isdigit():
                    # 格式：20240315
                    year = report_date[:4]
                    month = report_date[4:6]
                    day = report_date[6:8]
                elif '-' in report_date:
                    # 格式：2024-03-15
                    parts = report_date.split('-')
                    year = parts[0]
                    month = f"{int(parts[1]):02d}"
                    day = f"{int(parts[2]):02d}"
                elif '/' in report_date:
                    # 格式：2024/03/15
                    parts = report_date.split('/')
                    year = parts[0]
                    month = f"{int(parts[1]):02d}"
                    day = f"{int(parts[2]):02d}"
                else:
                    # 默认使用今天日期
                    current_date = datetime.now()
                    year = str(current_date.year)
                    month = f"{current_date.month:02d}"
                    day = f"{current_date.day:02d}"
            except:
                # 解析失败，使用今天日期
                current_date = datetime.now()
                year = str(current_date.year)
                month = f"{current_date.month:02d}"
                day = f"{current_date.day:02d}"
        else:
            # 用户没有提供日期，使用今天日期
            current_date = datetime.now()
            year = str(current_date.year)
            month = f"{current_date.month:02d}"
            day = f"{current_date.day:02d}"
        
        # 汇报人行：最后七个字是"汇报人：XXX"
        reporter_line = [''] * 20
        reporter_text = f"汇报人：{reporter_name}"
        start_pos = 20 - len(reporter_text)
        for i, char in enumerate(reporter_text):
            if start_pos + i < 20:
                reporter_line[start_pos + i] = char
        formatted_chars.extend(reporter_line)
        
        # 日期行：格式为"20xx年xx月xx日"，数字两位一格
        date_line = [''] * 20
        
        # 构建日期字符串：20xx年xx月xx日
        date_parts = [
            year[:2],  # "20"
            year[2:],  # "xx"
            "年",
            month,     # "xx"
            "月", 
            day,       # "xx"
            "日"
        ]
        
        # 右对齐放置日期
        start_pos = 20 - len(date_parts)
        for i, part in enumerate(date_parts):
            if start_pos + i < 20:
                date_line[start_pos + i] = part
        
        formatted_chars.extend(date_line)
        formatted_chars.append('\n')
        
        return formatted_chars
    
    def _paginate(self, chars: List[str]) -> List[List[List[str]]]:
        """分页处理"""
        pages = []
        current_page = []
        current_row = []
        row_count = 0
        
        i = 0
        while i < len(chars):
            char = chars[i]
            
            if char == '\n':
                # 换行处理
                while len(current_row) < self.cols_per_row:
                    current_row.append('')
                current_page.append(current_row)
                current_row = []
                row_count += 1
                
                # 检查是否需要新页面
                if row_count >= self.rows_per_page:
                    # 填充当前页面剩余行
                    while len(current_page) < self.rows_per_page:
                        empty_row = [''] * self.cols_per_row
                        current_page.append(empty_row)
                    pages.append(current_page)
                    current_page = []
                    row_count = 0
            else:
                current_row.append(char)
                
                # 检查行是否满了
                if len(current_row) >= self.cols_per_row:
                    current_page.append(current_row)
                    current_row = []
                    row_count += 1
                    
                    # 检查页面是否满了
                    if row_count >= self.rows_per_page:
                        while len(current_page) < self.rows_per_page:
                            empty_row = [''] * self.cols_per_row
                            current_page.append(empty_row)
                        pages.append(current_page)
                        current_page = []
                        row_count = 0
            
            i += 1
        
        # 处理最后的内容
        if current_row:
            while len(current_row) < self.cols_per_row:
                current_row.append('')
            current_page.append(current_row)
            row_count += 1
        
        if current_page:
            while len(current_page) < self.rows_per_page:
                empty_row = [''] * self.cols_per_row
                current_page.append(empty_row)
            pages.append(current_page)
        
        return pages if pages else [self._create_empty_page()]
    
    def _create_empty_page(self) -> List[List[str]]:
        """创建空白页面"""
        return [[''] * self.cols_per_row for _ in range(self.rows_per_page)]
    
    def check_punctuation_errors(self, pages: List[List[List[str]]]) -> List[List[List[bool]]]:
        """
        检测每行第一个非空字符是否为标点符号
        返回格式: [页面][行][列] -> bool
        """
        punctuation_marks = set('，。！？；：""“”''（）《》【】、')
        result = []
        
        for page in pages:
            page_result = []
            for row in page:
                row_result = []
                first_char_found = False
                
                for col_idx, char in enumerate(row):
                    is_first_punctuation = False
                    
                    if not first_char_found and char and char.strip():
                        first_char_found = True
                        # 检查第一个非空字符是否为标点
                        if char in punctuation_marks:
                            is_first_punctuation = True
                    
                    row_result.append(is_first_punctuation)
                
                page_result.append(row_result)
            result.append(page_result)
        
        return result
