import re

def rm_cn_punc(text):
    # 匹配中文标点的正则表达式
    chinese_punctuation_pattern = "[\u3000\u3001-\u3011\u2014\u2018-\u201D\u2022\u2026\u2030\u25EF，！？：；（）——]+"
    # 使用正则表达式替换中文标点为空格
    cleaned_text = re.sub(chinese_punctuation_pattern, "", text)
    return cleaned_text


def is_approximately_equal(char1, char2):
    # 检查两个字符是否完全相同
    if char1 == char2:
        return True
    
    # 检查两个字符是否为同一字母的不同大小写形式
    if char1.lower() == char2.lower():
        return True
    
    # 定义数字的不同表达形式
    digit_forms = {
        '0': ['0', '０', '〇', '零'],
        '1': ['1', '１', '一'],
        '2': ['2', '２', '二'],
        '3': ['3', '３', '三'],
        '4': ['4', '４', '四'],
        '5': ['5', '５', '五'],
        '6': ['6', '６', '六'],
        '7': ['7', '７', '七'],
        '8': ['8', '８', '八'],
        '9': ['9', '９', '九']
    }
    
    # 检查两个字符是否为同一数字的不同表达形式
    for digit, forms in digit_forms.items():
        if char1 in forms and char2 in forms:
            return True
    
    # 若以上条件都不满足，则认为两个字符不近似相同
    return False


if __name__ == '__main__':
    text = "这是一个示例，包含中文标点————：；，。！？《》……“”（）"
    print(rm_cn_punc(text))

    print(is_approximately_equal('A', 'a'))  # True
    print(is_approximately_equal('1', '一'))  # True
    print(is_approximately_equal('b', 'c'))  # False