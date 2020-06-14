import base64
import json
import sqlite3
import time

import requests

# face++的key和secret
api_key = 'o5a8Dj4AB0pvx1oCqFTdfKaq3DMSjHIZ'
api_secret = 'NwPQMZoMLsLo3VbGrnCz3FQL10wpbASM'
# 接入face++的api
detect_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
add_face_url = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/addface'
get_detail_url = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/getdetail'
search_url = 'https://api-cn.faceplusplus.com/facepp/v3/search'
private_outer_id = 'persons_set'


# 获取faceSet的信息，outer_id是集合的自定义标识
def get_face_set_detail(outer_id):
    data = {
        'api_key': api_key,
        'api_secret': api_secret,
        'outer_id': outer_id
    }
    request = requests.post(get_detail_url, data)
    return request.json()


# 向集合中添加人脸标识，face_token为图片上传到detectAPI后返回的人脸标识
def add_face(face_token, outer_id):
    data = {
        'api_key': api_key,
        'api_secret': api_secret,
        'face_tokens': face_token,
        'outer_id': outer_id
    }
    request = requests.post(add_face_url, data)
    return request.json()


# 人脸分析,需要传入base64编码的二进制图片数据，
# 返回face_token人脸标识,需要保存到本地和上传到FaceSet,如果没有人脸，就会返回null
def detect_face(image_base64):
    data = {
        'api_key': api_key,
        'api_secret': api_secret,
        'image_base64': image_base64
    }
    request = requests.post(detect_url, data)
    return request.json()


def search_face(face_token, outer_id):
    data = {
        'api_key': api_key,
        'api_secret': api_secret,
        'face_token': face_token,
        'outer_id': outer_id
    }
    request = requests.post(search_url, data)
    return request.json()
