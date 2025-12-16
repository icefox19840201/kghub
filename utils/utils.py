import hashlib
from typing import Union

def sha256_encrypt(data: Union[str, bytes]) -> str:
    """
    对输入数据进行 SHA256 加密，返回十六进制字符串
    :param data: 待加密字符串或字节
    :return: 加密后的十六进制字符串
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def sha256_verify(data: Union[str, bytes], digest: str) -> bool:
    """
    验证输入数据与给定 SHA256 摘要是否一致
    :param data: 待验证字符串或字节
    :param digest: 已知的 SHA256 十六进制摘要
    :return: 一致返回 True，否则 False
    """
    return sha256_encrypt(data) == digest
