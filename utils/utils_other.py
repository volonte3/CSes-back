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