'''
@Author: xiaoming
@Date: 2018-12-05 11:12:34
@LastEditors: xiaoming
@LastEditTime: 2018-12-05 11:57:30
@Description: use  call auto build 
'''
import paramiko


def connect_linux(ip, username='root', password='Juzhen123!'):
    '''
    Description:连接linux服务器
    params:
        @ip:服务器ip
        @username:用户名
        @password:密码
    return:
        @ssh:ssh实例，用于执行命令 ssh.exec_command(cmd)
        @sftp:文件传输实例，用于上传下载文件 sftp.get(a,b)将a下载到b,sftp.put(a,b)把a上传到b
        @t:连接实例，用于关闭连接 t.close()
    '''
    t = paramiko.Transport((ip, 22))
    t.connect(username=username, password=password)
    ssh = paramiko.SSHClient()
    ssh._transport = t
    sftp = paramiko.SFTPClient.from_transport(t)
    return ssh, sftp, t


def call_auto_build_sh(ip, username, password, sh_path):
    '''
    @Description: 用于调用自动打包的sh脚本
    @param:
        @ip:服务器ip
        @username:服务器用户名
        @password:服务器密码
        @sh_path:服务器中sh脚本的路径
    @return: bool
        @True:表示打包成功
        @False:打包失败 
    '''
    ssh, sftp, t = connect_linux(ip, username, password)
    _, out, err = ssh.exec_command('bash {}'.format(sh_path), get_pty=True)
    result = out.readlines()
    error = err.readlines()
    if error:
        raise Exception("自动打包失败-{}".format(error))
    for i in result:
        if "函数projectCompile()已执行完成,打包完成" in i:
            return True
    print(result)
    return False


if __name__ == "__main__":
    result = call_auto_build_sh(
        '192.168.9.178', 'juzhen', 'juzhen', './sss.sh')
    if not result:
        raise Exception("打包失败")
    print("打包成功")
