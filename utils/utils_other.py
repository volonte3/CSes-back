import hashlib

def sha256(password: str):
    # 对密码进行SHA256加密
    # 创建 SHA-256 哈希对象
    hash_object = hashlib.sha256()
    
    # 对数据进行哈希计算
    hash_object.update(password.encode())
    
    # 获取哈希值
    hashed_password = hash_object.hexdigest()
    return hashed_password

# 用于调试打印
def debug_print(name, content):
    print("----------------------------------------")
    print(name, content)
    print("----------------------------------------")

def parse_children(children_string):
    # 这里要不要增加children_string==None的一个判断
    children_list = children_string.split('$')
    return children_list[1:]  # 去除最前面的一个空格