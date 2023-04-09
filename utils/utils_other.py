import hashlib

def MD5(password: str):
    hash_object = hashlib.md5()

    # 对数据进行哈希计算
    hash_object.update(password.encode())
    
    # 获取哈希值
    hashed_password = hash_object.hexdigest()
    return hashed_password

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
    # 增加children_string==None的一个判断
    if (children_string == None):
        return []
    else:
        children_list = children_string.split('$')
        return children_list[1:]  # 去除最前面的一个空格

def delete_child(children_string, child:int):
    # 从children_string中删除掉一个child
    substr = '$' + str(child)
    pos = children_string.find(substr)

    if pos != -1:
        new_string = children_string[:pos] + children_string[pos+len(substr):]
    else:
        new_string = children_string
        print(f"{substr} not found in string")
    
    return new_string