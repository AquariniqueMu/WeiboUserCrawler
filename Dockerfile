# 使用官方的Python基础镜像
FROM python:3.12.5-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录所有文件到工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 运行Flask应用
CMD ["python", "app.py"]
