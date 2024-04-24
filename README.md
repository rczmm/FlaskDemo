## Flask 与 MySQL 结合的 Web 示例

本示例演示了如何使用 Flask 和 MySQL 创建一个简单的电子商务网站。用户可以登录，搜索商品，查看商品详情，进行点赞和取消点赞，将商品添加到购物车，并在购物车中查看商品信息和计算总价。

### 环境准备

确保系统中已安装以下软件：

- Python 3.x

### 安装依赖

使用提供的 `requirements.txt` 文件安装所需的 Python 包：

```bash
pip install -r requirements.txt

## 数据库设置
在 MySQL 中创建一个数据库，并执行以下命令创建所需的表：
```bash
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    likes INT DEFAULT 0
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

## 运行应用
```bash
python app.py

## 功能实现
用户登录用户可以通过提供用户名和密码登录到系统中。
搜索商品用户可以在搜索页面输入关键字搜索商品。
查看商品详情用户可以点击商品进入详情页面查看商品的详细信息。
点赞和取消点赞在商品详情页面，用户可以点赞或取消点赞商品。
添加商品到购物车在商品详情页面，用户可以将商品添加到购物车中。
查看购物车用户可以在购物车页面中查看所有已添加到购物车中的商品，并根据价格和数量计算出总价。

## 文件结构
app.py: Flask 应用程序的主要入口点。
templates/: 包含 HTML 模板文件。
static/: 包含静态文件，如 CSS、JavaScript 等。
requirements.txt: 包含项目依赖的 Python 包列表。
README.md: 项目说明文档。

## 注意事项
本示例为演示性质，未实现安全性和性能优化。在生产环境中需进行适当的安全性检查和性能优化。
