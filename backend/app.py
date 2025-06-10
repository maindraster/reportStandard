from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 添加utils目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from utils.text_processor import TextProcessor

app = Flask(__name__)
CORS(app)

# 初始化文本处理器
text_processor = TextProcessor()

# 初始化AI客户端
def get_ai_client():
    """获取AI客户端，优先使用硅基流动"""
    siliconflow_key = os.getenv('SILICONFLOW_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if siliconflow_key:
        return OpenAI(
            api_key=siliconflow_key,
            base_url="https://api.siliconflow.cn/v1"
        ), "deepseek-ai/DeepSeek-V3"
    elif openai_key:
        return OpenAI(api_key=openai_key), "gpt-3.5-turbo"
    else:
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_text():
    """处理文本格式化"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        reporter_name = data.get('reporter_name', 'XXX')
        report_date = data.get('report_date', '')
        
        if not text:
            return jsonify({'success': False, 'error': '文本内容不能为空'})
        
        # 处理文本
        pages = text_processor.process_text(text, reporter_name, report_date)
        
        if not pages:
            return jsonify({'success': False, 'error': '处理后没有生成任何页面'})
        
        # 检查行首标点符号
        punctuation_marks = text_processor.check_punctuation_errors(pages)
        
        return jsonify({
            'success': True,
            'pages': pages,
            'punctuation_marks': punctuation_marks,
            'total_pages': len(pages)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_report():
    """生成思想汇报范文"""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        if not user_input:
            return jsonify({'success': False, 'error': '用户输入不能为空'})
        
        # 获取AI客户端
        client, model = get_ai_client()
        
        if not client:
            return jsonify({
                'success': False, 
                'error': '未配置AI API密钥，请在.env文件中设置SILICONFLOW_API_KEY或OPENAI_API_KEY'
            })
        
        # 构建提示词
        current_date = datetime.now()
        month_year = f"{current_date.year}年{current_date.month}月"
        
        system_prompt = """你是一个专业的思想汇报写作助手。请根据用户提供的个人情况，按照思想收获、学习工作情况和不足以及改正措施三个主要部分撰写一篇结构完整、内容充实的思想汇报。语言正式、态度诚恳、思想积极向上。总共800字。以下是一篇示例：寒假过后，我们迎来了新的学期，同时也迎来了全国上下学习雷锋精神的新高潮。雷锋的名字伴随着国人度过了四十多年风风雨雨每到三月，人们便开始以不同的方式来纪念这位英雄人物。\n几十年来，许许多多的榜样、模范，曾一个又一个走进中国人的生活，他们在不同的历史时期被树立起来，成为人们学习的榜样;其中雷锋精神产生了尤为深刻、广泛、深远的影响。关于雷锋的先进事迹我们每个人都耳熟能详，从小到大我们一直都被教育要向雷锋同志学习，学习他毫不为己，专门利人的精神。\n雷锋精神很博大，它是一种庄严的责任感和伟大的激情，它体现在人际关系、职业态度和志愿行为这几个方面。它为我们的社会开仓了一代新风，它的实质和核心就是一种为共产主义而奋斗的无私奉南的精神;忠于党和人民、舍己为公、大公无私的奉献精神:立足本职在平凡的工作中创造出不平凡业绩的“螺丝钉精神”;苦干实干、不计报酬、争做贡献的艰苦奋斗精神，归根结底就是全心全意为人民服务的精神。\n当前，我国正在努力发展社会主义市场经济，社会生活正在发生深刻的变化。因而有人担心和怀疑:在竞争日益激烈的今天，雷锋精神还能与我们同行吗?改革开放、建设社会主义现代化强国二十多年的实践告诉我们，发展经济，不仅要讲究效益、鼓励竞争，还必须在全社会形成团结友爱、相互帮助、共同前进的良好人际关系。在经济动中，我们要强调按照市场规律办事。在思想道德领域，则必须大才提倡尊重人、关心人、热爱集体，扶贫帮困、崇尚诚信的美德，建立与社会主义市场经济相适应的思想道德体系。雷锋以春天般的温暖对待同志、对待群众，孜孩不倦地实践“把有限的生命投入到无限的为人民服务中去”的奋斗誓言。雷锋精神表现了中华儿女的高尚道德情操和崇高思想境界，代表了社会进步的方向，不仅在四十年前闪烁着共产党人的道德光辉，而且在今天也完全适应推进建设中国特色社会主义伟大事业的时代要求。\n值得说明的是，在不同时期，雷锋精神的表现内容与表现形式应该有所不同。而在过去很多时间里，学习雷锋活动从百姓自发、主动的道德行为，慢慢变成了一种程式化的“规定动作”，结果出现了每到三月初，福利院、敬老院等公益场所便成了大家争抢去服务的尴尬局面。而在程式化的行动之中，雷锋精神的实质很难发扬光大，雷锋精神中那种生机勃勃的活力也因此有所减弱。\n建设中国特色社会主义事业，是一项充满艰辛、充满创造的壮丽事业。伟大的事业需要并将产出崇高的精神，崇高的精神支撑和推动着伟大的事业。没有坚强精神的民族，是没有前途的。雷锋精神是推动我们社会进步的巨大精神财富，我们应该以理性的态度全面理解雷锋精神，让雷锋精神与时代同行，以饱满的激情、与时俱进地开展学雷锋活动，并将其代代相传下去。这是时代的需要、人民的呼唤，这也正是广大党员和群众共同努力的方向。\n以上是我这一阶段以来对“学雷锋”活动的一点感想，俗话说，“说起来容易做起来难”，要想真正达到雷锋那种无私忘我的精神境界是十分不易的，但我会努力从小事做起、从身边做起，以一名党员的标准来要求自己，以自己的实际行动投入到“学雷锋”活动中。\""""

        user_prompt = f"""请根据以下个人情况，为{month_year}生成一份思想汇报：

个人情况和感悟：
{user_input}

请生成完整的思想汇报内容。"""

        # 调用AI生成
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        
        # 收集流式响应
        generated_text = ""
        for chunk in response:
            if not chunk.choices:
                continue
            if chunk.choices[0].delta.content:
                generated_text += chunk.choices[0].delta.content
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                generated_text += chunk.choices[0].delta.reasoning_content
        
        if not generated_text.strip():
            return jsonify({'success': False, 'error': 'AI生成内容为空'})
        
        return jsonify({
            'success': True,
            'generated_text': generated_text.strip()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'生成失败: {str(e)}'})

@app.route('/api/stream-generate', methods=['POST'])
def stream_generate_report():
    """流式生成思想汇报范文"""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        if not user_input:
            return jsonify({'success': False, 'error': '用户输入不能为空'})
        
        # 获取AI客户端
        client, model = get_ai_client()
        
        if not client:
            return jsonify({
                'success': False, 
                'error': '未配置AI API密钥，请在.env文件中设置SILICONFLOW_API_KEY或OPENAI_API_KEY'
            })
        
        def generate():
            try:
                # 构建提示词
                current_date = datetime.now()
                month_year = f"{current_date.year}年{current_date.month}月"
                
                system_prompt = """你是一个专业的思想汇报写作助手。请根据用户提供的个人情况，生成一份完整、规范的思想汇报。

要求：
1. 格式规范，包含标准的开头和结尾
2. 内容充实，体现积极向上的思想态度
3. 语言正式，符合党组织汇报的语言风格
4. 结构清晰，分为思想、学习、工作、不足、努力方向等方面
5. 字数控制在800-1200字左右
6. 融入用户提供的个人情况和感悟"""

                user_prompt = f"""请根据以下个人情况，为{month_year}生成一份思想汇报：

个人情况和感悟：
{user_input}

请生成完整的思想汇报内容。"""

                # 调用AI生成
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2048,
                    stream=True
                )
                
                # 流式返回数据
                for chunk in response:
                    if not chunk.choices:
                        continue
                    
                    content = ""
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                    if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                        content += chunk.choices[0].delta.reasoning_content
                    
                    if content:
                        yield f"data: {content}\\n\\n"
                
                yield "data: [DONE]\\n\\n"
                
            except Exception as e:
                yield f"data: [ERROR] {str(e)}\\n\\n"
        
        return app.response_class(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'流式生成失败: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)