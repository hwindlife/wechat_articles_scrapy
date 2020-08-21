from scrapy.utils.project import get_project_settings

from wechat_articles_scrapy.util import HttpUtils

settings = get_project_settings()


def push_wxart_obj_batch(localpatharr):
    """
    批量推送微信公众号文件到腾讯云
    :param localpatharr: 本地文件路径数组
    :return:
    """
    for localpath in localpatharr:
        push_wxart_obj_single(localpath)


def push_wxart_obj_single(localpath: str):
    """
    单个推送微信公众号文件到腾讯云
    :param localpath: 本地文件路径
    :return:
    """
    objtype = localpath.split('.')[1]
    put_single_obj('0', 0, settings['TXCOS_COSSTR_WXART'], objtype, localpath)


def put_single_obj(bucket_type: str, days: int, cosstr: str, objtype: str, localpath: str):
    """
    单个对象推送
    :param bucket_type: bucket类型标识，0：共有，1：私有
    :param days: 保存天数 0：永久
    :param cosstr: cos路径标识字段，作为腾讯云二级目录
    :param objtype: 文件类型，例如：jpg，mp4
    :param localpath: 本地文件完整路径
    :return:
    """
    resp_json = get_sign_v5(bucket_type, days, 1, cosstr, objtype)
    if resp_json['rspCode'] == "0":
        file_auth = resp_json['info']['list'][0]['authList'][0]
        # 推送文件到腾讯云
        HttpUtils.put_binary(file_auth['reqUrl'], {'Authorization': file_auth['authStr'], 'Content-Type': 'binary'},
                             localpath)


def get_sign_v5(bucket_type: str, days: int, signnum: int, cosstr: str, objtype: str):
    """
    获取腾讯云5.0版本签名信息
    :param bucket_type: bucket类型标识，0：共有，1：私有
    :param days: 保存天数 0：永久
    :param signnum: 签名个数
    :param cosstr: cos路径标识字段，作为腾讯云二级目录
    :param objtype: 文件类型，例如：jpg，mp4
    :return:
    """
    file_info = {'signNum': str(signnum), 'cosStr': cosstr, 'type': objtype}
    resp = HttpUtils.post_json(settings['TXCOS_GETV5SIGN_URL'],
                               {'type': bucket_type, 'days': str(days), 'list': [file_info]})
    resp_json = resp.json()
    return resp_json


if __name__ == '__main__':
    push_wxart_obj_batch(["D:/construct.jpg"])
