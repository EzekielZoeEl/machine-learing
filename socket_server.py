import base64
import datetime
import socket
import sys
import threading
from Backend_Shapshot import face
import sqlite3

'''
socket服务器
需要单独开启，接收数据示例如下：
def socket_client(path):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 6666))  # 连接某ip的某端口
    except socket.error as msg:  # 打印错误信息
        print(msg)
        sys.exit(1)
    print(s.recv(1024))
    pic = open(path, 'rb')  # 图片路径
    str_pic = base64.b64encode(pic.read())  # 转base64编码
    s.send(str_pic)  # 发送二进制数据
    pic.close()
'''
def socket_server():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 防止socket server重启后端口被占用（socket.error: [Errno 98] Address already in use）
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 6666))  # 绑定端口
        s.listen(10)  # 最多连接数
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:  # 等待连接
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()


def deal_data(conn, addr):
    print('Accept new connection from {0}'.format(addr))
    conn.send('Hi, Welcome to the server!'.encode('utf-8'))
    data = bytes()  # 存放二进制数据
    while 1:
        buf = conn.recv(1024)  # 接收来自客户端的字节流
        if not buf:
            break
        data = data + buf
    face_token = face.detect_face(data)
    if 'faces' in face_token and face_token['faces'] != []:
        face_token = face_token['faces'][0]['face_token']  # 获取上传的图片的face_token
    else:
        return
    result = face.search_face(face_token, face.private_outer_id)['results']  # 在人脸集合中寻找最接近的
    face_token_in_set = result[0]['face_token']  # 返回结果中最接近的人脸的face_token
    confidence = result[0]['confidence']  # 对比的置信度
    if confidence >= 50:
        conn2sql = sqlite3.connect('../db.sqlite3')
        cur = conn2sql.cursor()  # 游标
        cur.execute(
            f"select workNumber from HelmetDb_PersonMessages where face_token='{face_token_in_set}'")  # 根据face_token在数据库中查找对应的人的工号
        d_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S')
        fa = cur.fetchall()
        if fa == []: return
        d_workNumber = fa[0][0]  # 获取查询结果
        d_url = '../static/criminal_records/' + str(d_workNumber) + '_' + str(d_date) + '.jpg'  # 违规照片存放url
        cur.execute(
            f"insert into HelmetDb_CriminalRecords values (null ,'{d_date}','{d_workNumber}','{d_url}')")  # 向违规记录表中插入数据
        conn2sql.commit()  # 提交修改
        conn2sql.close()
        pic_data = base64.b64decode(data)  # 解码二进制数据
        with open(d_url, 'wb') as f:  # 写图片到指定文件目录
            f.write(pic_data)
            f.close()
        print('record one person!')


if __name__ == '__main__':
    socket_server()
