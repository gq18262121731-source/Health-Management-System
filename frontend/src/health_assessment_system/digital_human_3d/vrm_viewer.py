"""
VRM 3D模型查看器
================

使用PyOpenGL渲染VRM/GLB模型
"""

import sys
import os
import json
import struct
import math
from threading import Thread
import queue

# OpenGL
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("请安装 PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate")

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QOpenGLWidget
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QSurfaceFormat

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GLBLoader:
    """GLB加载器 - 支持材质和纹理"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.meshes = []  # 存储所有网格
        self.materials = []  # 材质列表
        self.textures = {}  # 纹理数据
        self.loaded = False
        
    def load(self):
        """加载GLB文件"""
        try:
            with open(self.filepath, 'rb') as f:
                # 读取头部
                magic = f.read(4)
                if magic != b'glTF':
                    print(f"不是有效的GLB文件: {magic}")
                    return False
                
                version = struct.unpack('<I', f.read(4))[0]
                length = struct.unpack('<I', f.read(4))[0]
                
                print(f"GLB版本: {version}, 总长度: {length / 1024 / 1024:.1f} MB")
                
                # 读取JSON块
                chunk_length = struct.unpack('<I', f.read(4))[0]
                chunk_type = f.read(4)
                
                if chunk_type == b'JSON':
                    json_data = f.read(chunk_length).decode('utf-8')
                    self.gltf = json.loads(json_data)
                    
                    # 读取BIN块
                    if f.tell() < length:
                        bin_chunk_length = struct.unpack('<I', f.read(4))[0]
                        bin_chunk_type = f.read(4)
                        if bin_chunk_type == b'BIN\x00':
                            self.binary_data = f.read(bin_chunk_length)
                    
                    # 解析材质
                    self.parse_materials()
                    # 解析纹理
                    self.parse_textures()
                    # 解析所有网格
                    self.parse_all_meshes()
                    
                    self.loaded = True
                    return True
                    
        except Exception as e:
            print(f"加载GLB失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def parse_materials(self):
        """解析材质"""
        if 'materials' not in self.gltf:
            return
        
        for i, mat in enumerate(self.gltf['materials']):
            material = {
                'name': mat.get('name', f'Material_{i}'),
                'color': [0.8, 0.8, 0.8, 1.0],
                'texture_idx': None
            }
            
            # 获取基础颜色
            if 'pbrMetallicRoughness' in mat:
                pbr = mat['pbrMetallicRoughness']
                if 'baseColorFactor' in pbr:
                    material['color'] = pbr['baseColorFactor']
                if 'baseColorTexture' in pbr:
                    material['texture_idx'] = pbr['baseColorTexture'].get('index')
            
            self.materials.append(material)
        
        print(f"  材质数: {len(self.materials)}")
    
    def parse_textures(self):
        """解析纹理"""
        if 'textures' not in self.gltf or 'images' not in self.gltf:
            return
        
        for i, tex in enumerate(self.gltf['textures']):
            if 'source' in tex:
                img_idx = tex['source']
                img = self.gltf['images'][img_idx]
                
                # 从bufferView获取图像数据
                if 'bufferView' in img:
                    bv = self.gltf['bufferViews'][img['bufferView']]
                    offset = bv.get('byteOffset', 0)
                    length = bv['byteLength']
                    img_data = self.binary_data[offset:offset + length]
                    self.textures[i] = {
                        'data': img_data,
                        'mimeType': img.get('mimeType', 'image/png')
                    }
        
        print(f"  纹理数: {len(self.textures)}")
    
    def parse_all_meshes(self):
        """解析所有网格"""
        if 'meshes' not in self.gltf:
            return
        
        total_verts = 0
        total_indices = 0
        
        for mesh in self.gltf['meshes']:
            for primitive in mesh.get('primitives', []):
                mesh_data = {
                    'vertices': [],
                    'normals': [],
                    'texcoords': [],
                    'indices': [],
                    'material_idx': primitive.get('material', 0)
                }
                
                # 顶点
                if 'POSITION' in primitive['attributes']:
                    mesh_data['vertices'] = self.get_accessor_data(
                        primitive['attributes']['POSITION'])
                
                # 法线
                if 'NORMAL' in primitive['attributes']:
                    mesh_data['normals'] = self.get_accessor_data(
                        primitive['attributes']['NORMAL'])
                
                # 纹理坐标
                if 'TEXCOORD_0' in primitive['attributes']:
                    mesh_data['texcoords'] = self.get_accessor_data(
                        primitive['attributes']['TEXCOORD_0'])
                
                # 索引
                if 'indices' in primitive:
                    mesh_data['indices'] = self.get_accessor_data(
                        primitive['indices'], is_index=True)
                
                self.meshes.append(mesh_data)
                total_verts += len(mesh_data['vertices']) // 3
                total_indices += len(mesh_data['indices'])
        
        print(f"  网格数: {len(self.meshes)}")
        print(f"  总顶点: {total_verts}")
        print(f"  总索引: {total_indices}")
    
    def get_accessor_data(self, accessor_idx, is_index=False):
        """获取accessor数据"""
        accessor = self.gltf['accessors'][accessor_idx]
        buffer_view = self.gltf['bufferViews'][accessor['bufferView']]
        
        offset = buffer_view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        
        component_type = accessor['componentType']
        count = accessor['count']
        
        # 确定每个元素的组件数
        type_map = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
        num_components = type_map.get(accessor['type'], 1)
        
        total_count = count * num_components
        
        if component_type == 5126:  # FLOAT
            data = self.binary_data[offset:offset + total_count * 4]
            return list(struct.unpack(f'<{total_count}f', data))
        elif component_type == 5123:  # UNSIGNED_SHORT
            data = self.binary_data[offset:offset + total_count * 2]
            return list(struct.unpack(f'<{total_count}H', data))
        elif component_type == 5125:  # UNSIGNED_INT
            data = self.binary_data[offset:offset + total_count * 4]
            return list(struct.unpack(f'<{total_count}I', data))
        elif component_type == 5121:  # UNSIGNED_BYTE
            data = self.binary_data[offset:offset + total_count]
            return list(struct.unpack(f'<{total_count}B', data))
        
        return []


class ModelGLWidget(QOpenGLWidget):
    """OpenGL 3D模型渲染组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = 3.0
        self.is_talking = False
        self.anim_time = 0
        
        # 鼠标控制
        self.last_pos = None
        
        # 动画定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
    
    def load_model(self, filepath):
        """加载模型"""
        self.model = GLBLoader(filepath)
        if self.model.load():
            print("✓ 模型加载成功")
            # 加载纹理到OpenGL
            self.gl_textures = {}
            self.load_textures()
            self.update()
            return True
        return False
    
    def load_textures(self):
        """加载纹理到OpenGL"""
        if not self.model or not self.model.textures:
            return
        
        from io import BytesIO
        from PIL import Image
        
        for tex_idx, tex_data in self.model.textures.items():
            try:
                # 从二进制数据加载图片
                img = Image.open(BytesIO(tex_data['data']))
                img = img.convert('RGBA')
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                img_data = img.tobytes()
                
                # 创建OpenGL纹理
                tex_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, tex_id)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height,
                           0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                
                self.gl_textures[tex_idx] = tex_id
                print(f"    纹理 {tex_idx}: {img.width}x{img.height}")
            except Exception as e:
                print(f"    纹理 {tex_idx} 加载失败: {e}")
    
    def initializeGL(self):
        """初始化OpenGL"""
        glClearColor(0.15, 0.18, 0.25, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)
        
        # 主光源
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.98, 0.95, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.45, 1])
        
        # 补光
        glLightfv(GL_LIGHT1, GL_POSITION, [-1, 0.5, -1, 0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.4, 0.45, 0.5, 1])
    
    def resizeGL(self, w, h):
        """调整视口"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h > 0 else 1, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """绘制场景"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 相机位置
        gluLookAt(0, 0, self.zoom, 0, 0, 0, 0, 1, 0)
        
        # 应用旋转
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # 呼吸动画
        breath = math.sin(self.anim_time * 2) * 0.02
        glTranslatef(0, breath, 0)
        
        # 说话动画
        if self.is_talking:
            sway = math.sin(self.anim_time * 8) * 2
            glRotatef(sway, 0, 1, 0)
        
        # 绘制模型
        if self.model and self.model.loaded:
            self.draw_model()
        else:
            self.draw_placeholder()
        
        # 绘制地面网格
        self.draw_grid()
    
    def draw_model(self):
        """绘制模型 - 支持材质和纹理"""
        
        # 遍历所有网格
        for mesh in self.model.meshes:
            vertices = mesh['vertices']
            normals = mesh['normals']
            texcoords = mesh['texcoords']
            indices = mesh['indices']
            mat_idx = mesh['material_idx']
            
            # 获取材质
            if mat_idx < len(self.model.materials):
                mat = self.model.materials[mat_idx]
                color = mat['color']
                tex_idx = mat.get('texture_idx')
                
                # 设置颜色
                glColor4f(color[0], color[1], color[2], color[3] if len(color) > 3 else 1.0)
                
                # 绑定纹理
                if tex_idx is not None and hasattr(self, 'gl_textures') and tex_idx in self.gl_textures:
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, self.gl_textures[tex_idx])
                else:
                    glDisable(GL_TEXTURE_2D)
            else:
                glColor3f(0.8, 0.75, 0.7)
                glDisable(GL_TEXTURE_2D)
            
            # 绘制三角形
            if indices:
                glBegin(GL_TRIANGLES)
                for i in range(0, len(indices), 3):
                    for j in range(3):
                        idx = indices[i + j]
                        
                        # 法线
                        if normals and idx * 3 + 2 < len(normals):
                            glNormal3f(normals[idx * 3], normals[idx * 3 + 1], normals[idx * 3 + 2])
                        
                        # 纹理坐标
                        if texcoords and idx * 2 + 1 < len(texcoords):
                            glTexCoord2f(texcoords[idx * 2], texcoords[idx * 2 + 1])
                        
                        # 顶点
                        if idx * 3 + 2 < len(vertices):
                            glVertex3f(vertices[idx * 3], vertices[idx * 3 + 1], vertices[idx * 3 + 2])
                glEnd()
        
        glDisable(GL_TEXTURE_2D)
    
    def draw_placeholder(self):
        """绘制占位符"""
        # 身体
        glColor3f(0.3, 0.5, 0.7)
        glPushMatrix()
        glScalef(0.4, 0.6, 0.25)
        self.draw_cube()
        glPopMatrix()
        
        # 头
        glColor3f(0.9, 0.8, 0.75)
        glPushMatrix()
        glTranslatef(0, 0.8, 0)
        glScalef(0.25, 0.3, 0.25)
        self.draw_cube()
        glPopMatrix()
        
        # 眼睛
        glColor3f(0.3, 0.5, 0.8)
        glPushMatrix()
        glTranslatef(-0.08, 0.85, -0.2)
        glScalef(0.04, 0.04, 0.02)
        self.draw_cube()
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.08, 0.85, -0.2)
        glScalef(0.04, 0.04, 0.02)
        self.draw_cube()
        glPopMatrix()
    
    def draw_cube(self):
        """绘制立方体"""
        glBegin(GL_QUADS)
        # 前
        glNormal3f(0, 0, -1)
        glVertex3f(-1, -1, -1); glVertex3f(1, -1, -1)
        glVertex3f(1, 1, -1); glVertex3f(-1, 1, -1)
        # 后
        glNormal3f(0, 0, 1)
        glVertex3f(-1, -1, 1); glVertex3f(-1, 1, 1)
        glVertex3f(1, 1, 1); glVertex3f(1, -1, 1)
        # 左
        glNormal3f(-1, 0, 0)
        glVertex3f(-1, -1, -1); glVertex3f(-1, 1, -1)
        glVertex3f(-1, 1, 1); glVertex3f(-1, -1, 1)
        # 右
        glNormal3f(1, 0, 0)
        glVertex3f(1, -1, -1); glVertex3f(1, -1, 1)
        glVertex3f(1, 1, 1); glVertex3f(1, 1, -1)
        # 上
        glNormal3f(0, 1, 0)
        glVertex3f(-1, 1, -1); glVertex3f(1, 1, -1)
        glVertex3f(1, 1, 1); glVertex3f(-1, 1, 1)
        # 下
        glNormal3f(0, -1, 0)
        glVertex3f(-1, -1, -1); glVertex3f(-1, -1, 1)
        glVertex3f(1, -1, 1); glVertex3f(1, -1, -1)
        glEnd()
    
    def draw_grid(self):
        """绘制地面网格"""
        glDisable(GL_LIGHTING)
        glColor4f(0.3, 0.35, 0.4, 0.5)
        glBegin(GL_LINES)
        for i in range(-5, 6):
            glVertex3f(i, -1.5, -5)
            glVertex3f(i, -1.5, 5)
            glVertex3f(-5, -1.5, i)
            glVertex3f(5, -1.5, i)
        glEnd()
        glEnable(GL_LIGHTING)
    
    def update_animation(self):
        """更新动画"""
        self.anim_time += 0.03
        self.update()
    
    def mousePressEvent(self, event):
        self.last_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.last_pos:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.last_pos = event.pos()
            self.update()
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom = max(1, min(10, self.zoom - delta * 0.3))
        self.update()
    
    def start_talking(self):
        self.is_talking = True
    
    def stop_talking(self):
        self.is_talking = False


class VRMViewerApp(QMainWindow):
    """VRM查看器应用"""
    
    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.response_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_agent()
        
        # 加载模型
        if OPENGL_AVAILABLE:
            QTimer.singleShot(100, self.load_model)
        
        # 响应检查
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_response)
        self.check_timer.start(100)
        
        QTimer.singleShot(500, self.show_greeting)
    
    def setup_ui(self):
        self.setWindowTitle("🦈 Little Shark - 3D Digital Human")
        self.setMinimumSize(1300, 800)
        self.setStyleSheet("background: #1a2035;")
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 3D视图
        if OPENGL_AVAILABLE:
            self.gl_widget = ModelGLWidget()
            layout.addWidget(self.gl_widget, 3)
        else:
            placeholder = QLabel("OpenGL不可用\n请安装: pip install PyOpenGL")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: white; font-size: 18px;")
            layout.addWidget(placeholder, 3)
        
        # 聊天面板
        chat_panel = QWidget()
        chat_panel.setStyleSheet("background: rgba(25, 35, 55, 240);")
        chat_layout = QVBoxLayout(chat_panel)
        
        # 标题
        title = QLabel("💬 Chat with Little Shark")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet("color: #7AB8F5; padding: 15px;")
        chat_layout.addWidget(title)
        
        # 聊天区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: rgba(20, 30, 50, 220);
                border: 1px solid rgba(100, 180, 255, 100);
                border-radius: 10px;
                padding: 10px;
                color: #E0E8F0;
            }
        """)
        chat_layout.addWidget(self.chat_display)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 45, 70, 220);
                border: 2px solid rgba(100, 180, 255, 100);
                border-radius: 20px;
                padding: 12px 20px;
                color: white;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("发送")
        send_btn.setStyleSheet("""
            QPushButton {
                background: #4A90D9;
                border-radius: 20px;
                padding: 12px 25px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background: #5AA0E9; }
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        chat_layout.addLayout(input_layout)
        layout.addWidget(chat_panel, 2)
        
        self.statusBar().setStyleSheet("color: #8090A0;")
        self.statusBar().showMessage("鼠标拖动旋转 | 滚轮缩放")
    
    def load_model(self):
        if hasattr(self, 'gl_widget'):
            self.gl_widget.load_model(self.model_path)
    
    def setup_agent(self):
        try:
            from agents.multi_agent_system import MultiAgentSystem
            self.agent = MultiAgentSystem(user_id="shark_user", enable_assessment=False)
        except Exception as e:
            print(f"Agent error: {e}")
            self.agent = None
    
    def show_greeting(self):
        if self.agent:
            greeting = self.agent.get_greeting()
            self.add_bot_message(greeting)
            if hasattr(self, 'gl_widget'):
                self.gl_widget.start_talking()
                QTimer.singleShot(2000, self.gl_widget.stop_talking)
    
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        
        self.input_field.clear()
        self.add_user_message(text)
        
        if hasattr(self, 'gl_widget'):
            self.gl_widget.start_talking()
        
        Thread(target=self.process_msg, args=(text,), daemon=True).start()
    
    def process_msg(self, text):
        try:
            resp = self.agent.chat(text) if self.agent else "系统不可用"
            self.response_queue.put(("ok", resp))
        except Exception as e:
            self.response_queue.put(("err", str(e)))
    
    def add_user_message(self, msg):
        self.chat_display.append(
            f'<div style="text-align:right; margin:8px;">'
            f'<span style="background:#4A90D9; color:white; padding:8px 12px; '
            f'border-radius:12px;">{msg}</span></div>'
        )
    
    def add_bot_message(self, msg):
        self.chat_display.append(
            f'<div style="text-align:left; margin:8px;">'
            f'<span style="background:#2a3a50; color:#E0E8F0; padding:8px 12px; '
            f'border-radius:12px;">{msg}</span></div>'
        )
    
    def check_response(self):
        try:
            status, resp = self.response_queue.get_nowait()
            if status == "ok":
                self.add_bot_message(resp)
                if hasattr(self, 'gl_widget'):
                    talk_time = min(len(resp) * 25, 4000)
                    QTimer.singleShot(talk_time, self.gl_widget.stop_talking)
            else:
                self.add_bot_message(f"错误: {resp}")
                if hasattr(self, 'gl_widget'):
                    self.gl_widget.stop_talking()
        except queue.Empty:
            pass


def main():
    print("=" * 55)
    print("  🦈 Little Shark - 3D Digital Human")
    print("=" * 55)
    
    model_path = r"D:\工坊\智能诊断项目\health_assessment_system\digital_human_3d\models\shark.glb"
    
    if os.path.exists(model_path):
        print(f"✓ 找到模型")
    else:
        print("✗ 模型文件不存在")
    
    print()
    print("控制方式:")
    print("  鼠标拖动: 旋转模型")
    print("  滚轮: 缩放")
    print()
    
    # 设置OpenGL格式
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)
    
    app = QApplication(sys.argv)
    window = VRMViewerApp(model_path)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
