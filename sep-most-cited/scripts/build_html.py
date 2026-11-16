import json
head = open('site/v3_head.html', encoding='utf-8').read()
js = open('site/v3.js', encoding='utf-8').read()
tpl = head + '<script>\n' + js + '</script>\n</body>\n</html>\n'
open('site/template_v3.html', 'w', encoding='utf-8').write(tpl)
D = json.load(open('page_data_v3.json', encoding='utf-8'))
data = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
open('site/index_v3.html', 'w', encoding='utf-8').write(tpl.replace('__DATA__', data))
import os; print(os.path.getsize('site/index_v3.html'))
