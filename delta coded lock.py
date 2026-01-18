import tkinter as tk
import random
import time
import json
import os

# 游戏设置
COLUMNS = 5
ROWS = 7
SYMBOL_SET = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9","!","@","#","$","%","^","&","*"]

# 账户数据文件路径
ACCOUNTS_FILE = "accounts.json"

# 账户管理类
class AccountManager:
    def __init__(self):
        self.accounts = {}
        self.load_accounts()
        
    def load_accounts(self):
        """从文件加载账户数据"""
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, 'r') as f:
                    self.accounts = json.load(f)
            except:
                self.accounts = {}
        else:
            # 创建默认管理员账户
            self.accounts = {
                "admin": {
                    "password": "admin123",
                    "account_type": "admin",
                    "banned": False,
                    "haf_coin": 999,
                    "unlocked_features": ["scroll_speed", "auto_aim", "error_hint", "extra_life"]
                }
            }
            self.save_accounts()
    
    def save_accounts(self):
        """保存账户数据到文件"""
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(self.accounts, f, indent=2)
    
    def login(self, username, password):
        """登录验证"""
        if username in self.accounts:
            account = self.accounts[username]
            if account["password"] == password:
                if account["banned"]:
                    return None, "账户已被封禁！"
                return account, "登录成功！"
            else:
                return None, "密码错误！"
        else:
            return None, "用户名不存在！"
    
    def register(self, username, password):
        """注册新账户"""
        if username in self.accounts:
            return False, "用户名已存在！"
        
        # 创建新账户
        self.accounts[username] = {
            "password": password,
            "account_type": "user",
            "banned": False,
            "haf_coin": 0,
            "unlocked_features": [],
            "enabled_features": {}  # 初始化功能开启状态
        }
        self.save_accounts()
        return True, "注册成功！"
    
    def ban_account(self, username):
        """封禁账户"""
        if username in self.accounts and self.accounts[username]["account_type"] == "user":
            self.accounts[username]["banned"] = True
            self.save_accounts()
            return True
        return False
    
    def unban_account(self, username):
        """解除账户封禁"""
        if username in self.accounts and self.accounts[username]["account_type"] == "user":
            self.accounts[username]["banned"] = False
            self.save_accounts()
            return True
        return False
    
    def update_account(self, username, data):
        """更新账户信息"""
        if username in self.accounts:
            self.accounts[username].update(data)
            self.save_accounts()
            return True
        return False
    
    def get_user_list(self):
        """获取所有普通用户列表"""
        users = []
        for username, account in self.accounts.items():
            if account["account_type"] == "user":
                users.append({
                    "username": username,
                    "banned": account["banned"]
                })
        return users
    
    def save_player_data(self, player):
        """保存玩家数据到账户文件"""
        if player.username and player.username in self.accounts:
            self.accounts[player.username] = player.to_dict()
            self.save_accounts()

# 玩家数据
class PlayerData:
    def __init__(self, username=None, account_type="user"):
        self.username = username
        self.account_type = account_type
        self.haf_coin = 0
        self.unlocked_features = []
        self.enabled_features = {}
        self.banned = False
    
    def load_from_account(self, account_data):
        """从账户数据加载玩家信息"""
        self.username = account_data.get("username", self.username)
        self.account_type = account_data.get("account_type", "user")
        self.haf_coin = account_data.get("haf_coin", 0)
        self.unlocked_features = account_data.get("unlocked_features", [])
        
        # 修复：确保enabled_features始终是一个字典
        self.enabled_features = account_data.get("enabled_features", {})
        if not isinstance(self.enabled_features, dict):
            self.enabled_features = {}
        
        self.banned = account_data.get("banned", False)
        
        # 确保所有已解锁功能都有默认开启状态
        for feature in self.unlocked_features:
            if feature not in self.enabled_features:
                self.enabled_features[feature] = True
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "username": self.username,
            "account_type": self.account_type,
            "haf_coin": self.haf_coin,
            "unlocked_features": self.unlocked_features,
            "enabled_features": self.enabled_features,
            "banned": self.banned
        }

# 游戏主类
class DeltaLockGame:
    def __init__(self, root):
        self.root = root
        self.root.title("三角洲开锁模拟器")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # 账户管理
        self.account_manager = AccountManager()
        self.current_account = None
        self.player_data = PlayerData()
        self.current_level = 1
        
        self.show_login_screen()
    
    def show_login_screen(self):
        """显示登录界面"""
        # 清除当前窗口
        for widget in self.root.winfo_children(): 
            widget.destroy()
        
        # 标题
        title_label = tk.Label(self.root, text="三角洲开锁模拟器", font=("Arial", 24, "bold"), fg="#00FF00", bg="#000000")
        title_label.pack(fill=tk.X, pady=20)
        
        # 登录框架
        login_frame = tk.Frame(self.root, bg="#000000")
        login_frame.pack(expand=True)
        
        # 用户名输入
        tk.Label(login_frame, text="用户名:", font=("Arial", 16), fg="#FFFFFF", bg="#000000").grid(row=0, column=0, pady=10, padx=10)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 16), width=20)
        self.username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # 密码输入
        tk.Label(login_frame, text="密码:", font=("Arial", 16), fg="#FFFFFF", bg="#000000").grid(row=1, column=0, pady=10, padx=10)
        self.password_entry = tk.Entry(login_frame, font=("Arial", 16), width=20, show="*")
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # 消息标签
        self.login_message = tk.Label(login_frame, text="", font=("Arial", 14), fg="#FF0000", bg="#000000")
        self.login_message.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 按钮框架
        button_frame = tk.Frame(login_frame, bg="#000000")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # 登录按钮
        login_button = tk.Button(button_frame, text="登录", font=("Arial", 16), width=10, 
                              bg="#00FF00", fg="#000000", command=self.handle_login)
        login_button.pack(side=tk.LEFT, padx=10)
        
        # 注册按钮
        register_button = tk.Button(button_frame, text="注册", font=("Arial", 16), width=10, 
                                 bg="#FFD700", fg="#000000", command=self.show_register_screen)
        register_button.pack(side=tk.LEFT, padx=10)
        
        # 回车键登录
        self.root.bind("<Return>", lambda event: self.handle_login())
    
    def handle_login(self):
        """处理登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.login_message.config(text="用户名和密码不能为空！")
            return
        
        account, message = self.account_manager.login(username, password)
        if account:
            # 登录成功
            self.current_account = account
            self.player_data.load_from_account(account)
            self.show_main_menu()
        else:
            # 登录失败
            self.login_message.config(text=message)
    
    def show_register_screen(self):
        """显示注册界面"""
        # 清除当前窗口
        for widget in self.root.winfo_children(): 
            widget.destroy()
        
        # 标题
        title_label = tk.Label(self.root, text="注册新账户", font=("Arial", 24, "bold"), fg="#00FF00", bg="#000000")
        title_label.pack(fill=tk.X, pady=20)
        
        # 注册框架
        register_frame = tk.Frame(self.root, bg="#000000")
        register_frame.pack(expand=True)
        
        # 用户名输入
        tk.Label(register_frame, text="用户名:", font=("Arial", 16), fg="#FFFFFF", bg="#000000").grid(row=0, column=0, pady=10, padx=10)
        self.reg_username_entry = tk.Entry(register_frame, font=("Arial", 16), width=20)
        self.reg_username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # 密码输入
        tk.Label(register_frame, text="密码:", font=("Arial", 16), fg="#FFFFFF", bg="#000000").grid(row=1, column=0, pady=10, padx=10)
        self.reg_password_entry = tk.Entry(register_frame, font=("Arial", 16), width=20, show="*")
        self.reg_password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # 确认密码
        tk.Label(register_frame, text="确认密码:", font=("Arial", 16), fg="#FFFFFF", bg="#000000").grid(row=2, column=0, pady=10, padx=10)
        self.reg_confirm_entry = tk.Entry(register_frame, font=("Arial", 16), width=20, show="*")
        self.reg_confirm_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # 消息标签
        self.register_message = tk.Label(register_frame, text="", font=("Arial", 14), fg="#FF0000", bg="#000000")
        self.register_message.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 按钮框架
        button_frame = tk.Frame(register_frame, bg="#000000")
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 注册按钮
        register_button = tk.Button(button_frame, text="注册", font=("Arial", 16), width=10, 
                                 bg="#00FF00", fg="#000000", command=self.handle_register)
        register_button.pack(side=tk.LEFT, padx=10)
        
        # 返回登录
        back_button = tk.Button(button_frame, text="返回登录", font=("Arial", 16), width=10, 
                             bg="#FFD700", fg="#000000", command=self.show_login_screen)
        back_button.pack(side=tk.LEFT, padx=10)
    
    def handle_register(self):
        """处理注册"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm_password = self.reg_confirm_entry.get().strip()
        
        if not username or not password:
            self.register_message.config(text="用户名和密码不能为空！")
            return
        
        if password != confirm_password:
            self.register_message.config(text="两次输入的密码不一致！")
            return
        
        success, message = self.account_manager.register(username, password)
        if success:
            # 注册成功，返回登录界面
            self.register_message.config(text=message, fg="#00FF00")
            # 清空输入
            self.reg_username_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_confirm_entry.delete(0, tk.END)
            # 2秒后返回登录界面
            self.root.after(2000, self.show_login_screen)
        else:
            # 注册失败
            self.register_message.config(text=message)
    
    def show_main_menu(self):
        # 清除当前窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 标题
        title_label = tk.Label(self.root, text="三角洲开锁模拟器", font=("Arial", 24, "bold"), fg="#00FF00", bg="#000000")
        title_label.pack(fill=tk.X, pady=20)
        
        # 账户信息显示
        account_frame = tk.Frame(self.root, bg="#000000")
        account_frame.pack(pady=10)
        
        # 用户名显示
        account_type = "管理员" if self.player_data.account_type == "admin" else "普通用户"
        tk.Label(account_frame, text=f"当前账户: {self.player_data.username}", font=("Arial", 14), fg="#FFFFFF", bg="#000000").pack(side=tk.LEFT, padx=10)
        tk.Label(account_frame, text=f"账户类型: {account_type}", font=("Arial", 14), fg="#FFFF00", bg="#000000").pack(side=tk.LEFT, padx=10)
        
        # 哈夫币显示
        coin_label = tk.Label(self.root, text=f"哈夫币: {self.player_data.haf_coin}", font=("Arial", 16), fg="#FFD700", bg="#000000")
        coin_label.pack(pady=10)
        
        # 按钮框架 - 使用side=tk.TOP确保在退出登录按钮之前
        button_frame = tk.Frame(self.root, bg="#000000")
        button_frame.pack(side=tk.TOP, expand=True)
        
        # 开始游戏按钮 - 减小高度和字体大小
        start_button = tk.Button(button_frame, text="开始游戏", font=("Arial", 16), width=20, height=1, 
                               bg="#00FF00", fg="#000000", command=self.start_game)
        start_button.pack(pady=12)
        
        # 商店按钮
        shop_button = tk.Button(button_frame, text="商店", font=("Arial", 16), width=20, height=1, 
                              bg="#00FF00", fg="#000000", command=self.show_shop)
        shop_button.pack(pady=12)
        
        # 功能设置按钮
        settings_button = tk.Button(button_frame, text="功能设置", font=("Arial", 16), width=20, height=1, 
                                 bg="#00FF00", fg="#000000", command=self.show_feature_settings)
        settings_button.pack(pady=12)
        
        # 管理员功能
        if self.player_data.account_type == "admin":
            admin_button = tk.Button(button_frame, text="管理员控制台", font=("Arial", 16), width=20, height=1, 
                                 bg="#FF0000", fg="#FFFFFF", command=self.show_admin_console)
            admin_button.pack(pady=12)
        
        # 退出登录按钮 - 使用更醒目的位置和样式
        logout_button = tk.Button(self.root, text="退出登录", font=("Arial", 14, "bold"), 
                               bg="#FF0000", fg="#FFFFFF", command=self.show_login_screen)
        logout_button.pack(side=tk.BOTTOM, pady=20, padx=20)
        
        # 设置背景
        self.root.configure(bg="#000000")
    
    def show_admin_console(self):
        """显示管理员控制台"""
        # 清除当前窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 标题
        title_label = tk.Label(self.root, text="管理员控制台", font=("Arial", 24, "bold"), fg="#FF0000", bg="#000000")
        title_label.pack(fill=tk.X, pady=20)
        
        # 返回按钮
        back_button = tk.Button(self.root, text="返回主菜单", font=("Arial", 14), 
                               bg="#00FF00", fg="#000000", command=self.show_main_menu)
        back_button.pack(anchor=tk.NW, padx=10, pady=10)
        
        # 用户管理框架
        user_frame = tk.Frame(self.root, bg="#000000")
        user_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(user_frame, text="用户管理", font=("Arial", 20, "bold"), fg="#FFFFFF", bg="#000000").pack(pady=10)
        
        # 用户列表
        self.user_listbox = tk.Listbox(user_frame, font=("Arial", 14), width=50, height=15, 
                                     bg="#333333", fg="#FFFFFF", selectbackground="#00FF00")
        self.user_listbox.pack(pady=10)
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#333333", fg="#FFFFFF")
        self.context_menu.add_command(label="封禁账号", command=self.ban_selected_user)
        self.context_menu.add_command(label="解封账号", command=self.unban_selected_user)
        self.context_menu.add_separator()  # 添加分隔线
        self.context_menu.add_command(label="设置哈夫币", command=self.show_set_coins_dialog)
        self.context_menu.add_command(label="切换商店状态", command=self.toggle_shop_access)
        
        # 绑定右键菜单事件
        def show_context_menu(event):
            # 确保点击的是有效项目
            index = self.user_listbox.nearest(event.y)
            if index >= 0 and index < self.user_listbox.size():
                self.user_listbox.selection_clear(0, tk.END)
                self.user_listbox.selection_set(index)
                self.user_listbox.activate(index)
                
                # 获取选中的用户信息
                selected_item = self.user_listbox.get(index)
                username = selected_item.split(" ")[-1]
                if "[封禁]" in selected_item:
                    # 用户已封禁，只显示解封选项
                    self.context_menu.entryconfig(0, state=tk.DISABLED)
                    self.context_menu.entryconfig(1, state=tk.NORMAL)
                else:
                    # 用户正常，只显示封禁选项
                    self.context_menu.entryconfig(0, state=tk.NORMAL)
                    self.context_menu.entryconfig(1, state=tk.DISABLED)
                
                # 显示右键菜单
                self.context_menu.post(event.x_root, event.y_root)
                # 保存当前选中的用户名
                self.current_selected_user = username
        
        # 绑定右键点击事件
        self.user_listbox.bind('<Button-3>', show_context_menu)
        
        # 刷新用户列表
        self.refresh_user_list()
        
        # 刷新按钮
        button_frame = tk.Frame(user_frame, bg="#000000")
        button_frame.pack(pady=20)
        
        refresh_button = tk.Button(button_frame, text="刷新列表", font=("Arial", 16), width=15, 
                                 bg="#FFD700", fg="#000000", command=self.refresh_user_list)
        refresh_button.pack(pady=10)
    
    def refresh_user_list(self):
        """刷新用户列表"""
        # 清空列表
        self.user_listbox.delete(0, tk.END)
        
        # 获取所有用户
        users = self.account_manager.get_user_list()
        
        for user in users:
            status = "[封禁]" if user["banned"] else "[正常]"
            self.user_listbox.insert(tk.END, f"{status} {user['username']}")
    
    def ban_selected_user(self):
        """封禁选中的用户"""
        selected_index = self.user_listbox.curselection()
        if not selected_index:
            return
        
        # 获取选中的用户名
        selected_item = self.user_listbox.get(selected_index)
        username = selected_item.split(" ")[-1]
        
        # 封禁用户
        if self.account_manager.ban_account(username):
            # 刷新列表
            self.refresh_user_list()
    
    def unban_selected_user(self):
        """解封选中的用户"""
        selected_index = self.user_listbox.curselection()
        if not selected_index:
            return
        
        # 获取选中的用户名
        selected_item = self.user_listbox.get(selected_index)
        username = selected_item.split(" ")[-1]
        
        # 解封用户
        if self.account_manager.unban_account(username):
            # 刷新列表
            self.refresh_user_list()
    
    def set_user_coins(self):
        """设置选中用户的金币数量"""
        selected_index = self.user_listbox.curselection()
        if not selected_index:
            return
        
        try:
            coins = int(self.coin_entry.get())
            if coins < 0:
                return
            
            # 获取选中的用户名
            selected_item = self.user_listbox.get(selected_index)
            username = selected_item.split(" ")[-1]
            
            # 更新金币数量
            self.account_manager.update_account(username, {"haf_coin": coins})
            
            # 更新界面信息
            self.refresh_user_list()
            self.update_selected_user_info(username)
            
        except ValueError:
            pass
    
    def set_user_shop_access(self):
        """设置选中用户是否可以使用商店"""
        selected_index = self.user_listbox.curselection()
        if not selected_index:
            return
        
        # 获取选中的用户名
        selected_item = self.user_listbox.get(selected_index)
        username = selected_item.split(" ")[-1]
        
        # 更新商店禁用状态
        shop_disabled = self.shop_disabled_var.get()
        self.account_manager.update_account(username, {"shop_disabled": shop_disabled})
        
        # 更新界面信息
        self.refresh_user_list()
        self.update_selected_user_info(username)
    
    def show_set_coins_dialog(self):
        """显示设置哈夫币的对话框"""
        if not hasattr(self, 'current_selected_user') or not self.current_selected_user:
            return
        
        # 获取当前选中的用户
        username = self.current_selected_user
        account = self.account_manager.accounts.get(username)
        if not account:
            return
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("设置哈夫币")
        dialog.geometry("300x150")
        dialog.configure(bg="#000000")
        dialog.resizable(False, False)
        
        # 对话框居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # 标签
        label = tk.Label(dialog, text="设置哈夫币数量:", font=("Arial", 12), 
                        fg="#FFFFFF", bg="#000000")
        label.pack(pady=10)
        
        # 输入框
        coin_var = tk.StringVar(value=str(account.get("haf_coin", 0)))
        coin_entry = tk.Entry(dialog, textvariable=coin_var, font=("Arial", 12), width=15)
        coin_entry.pack(pady=5)
        
        # 确认按钮
        def confirm_set_coins():
            try:
                coins = int(coin_var.get())
                if coins >= 0:
                    # 更新金币数量
                    self.account_manager.update_account(username, {"haf_coin": coins})
                    # 刷新列表
                    self.refresh_user_list()
                    # 关闭对话框
                    dialog.destroy()
            except ValueError:
                pass
        
        confirm_button = tk.Button(dialog, text="确认", font=("Arial", 12), 
                                  bg="#00FF00", fg="#000000", command=confirm_set_coins)
        confirm_button.pack(pady=10)
        
        # 让对话框获得焦点
        dialog.grab_set()
    
    def toggle_shop_access(self):
        """切换选中用户的商店访问状态"""
        if not hasattr(self, 'current_selected_user') or not self.current_selected_user:
            return
        
        # 获取当前选中的用户
        username = self.current_selected_user
        account = self.account_manager.accounts.get(username)
        if not account:
            return
        
        # 切换商店禁用状态
        current_status = account.get("shop_disabled", False)
        new_status = not current_status
        
        # 更新状态
        self.account_manager.update_account(username, {"shop_disabled": new_status})
        
        # 刷新列表
        self.refresh_user_list()
    
    def show_feature_settings(self):
        """显示功能设置界面"""
        # 清除当前窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 标题
        title_label = tk.Label(self.root, text="功能设置", font=("Arial", 24, "bold"), fg="#00FF00", bg="#000000")
        title_label.pack(fill=tk.X, pady=20)
        
        # 返回按钮
        back_button = tk.Button(self.root, text="返回主菜单", font=("Arial", 14), 
                               bg="#00FF00", fg="#000000", command=self.show_main_menu)
        back_button.pack(anchor=tk.NW, padx=10, pady=10)
        
        # 功能设置框架
        settings_frame = tk.Frame(self.root, bg="#000000")
        settings_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # 功能列表标题
        tk.Label(settings_frame, text="已购买功能", font=(
        "Arial", 20, "bold"), fg="#FFFFFF", bg="#000000").pack(pady=10)
        
        # 创建带滚动条的功能区域
        canvas = tk.Canvas(settings_frame, bg="#000000", bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#000000")
        
        # 配置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 功能描述字典
        feature_descriptions = {
            "scroll_speed": "快速滚动：增加滚动速度",
            "auto_aim": "自动瞄准：正确符号接近中间时提示",
            "error_hint": "错误提示：显示错误的符号（橙色）",
            "extra_life": "额外生命：允许一次错误"
        }
        
        # 功能开关字典，用于保存开关状态
        self.feature_toggles = {}
        
        # 创建功能开关
        for feature in self.player_data.unlocked_features:
            feature_frame = tk.Frame(scrollable_frame, bg="#333333", bd=2, relief=tk.RAISED)
            feature_frame.pack(pady=10, fill=tk.X, padx=10)
            
            # 功能名称和描述
            desc_text = feature_descriptions.get(feature, feature)
            feature_label = tk.Label(feature_frame, text=desc_text, font=(
            "Arial", 14), fg="#FFFFFF", bg="#333333")
            feature_label.pack(side=tk.LEFT, padx=20, pady=10)
            
            # 开关按钮
            toggle_var = tk.BooleanVar(value=self.player_data.enabled_features.get(feature, True))
            toggle_button = tk.Checkbutton(feature_frame, text="开启", font=(
            "Arial", 14), 
                                          variable=toggle_var, bg="#333333", fg="#FFFFFF", 
                                          selectcolor="#00FF00")
            toggle_button.pack(side=tk.RIGHT, padx=20, pady=10)
            
            self.feature_toggles[feature] = toggle_var
        
        # 放置滚动区域和滚动条
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # 允许使用鼠标滚轮滚动
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 保存按钮
        save_button = tk.Button(settings_frame, text="保存设置", font=(
        "Arial", 18), width=20, height=2, 
                              bg="#00FF00", fg="#000000", command=self.save_feature_settings)
        save_button.pack(pady=20)
        
        # 如果没有已购买的功能
        if not self.player_data.unlocked_features:
            empty_label = tk.Label(settings_frame, text="您还没有购买任何功能，请先去商店购买！", 
                                 font=("Arial", 16), fg="#FFFF00", bg="#000000")
            empty_label.pack(pady=50)
    
    def save_feature_settings(self):
        """保存功能设置"""
        # 更新功能开启状态
        for feature, toggle_var in self.feature_toggles.items():
            self.player_data.enabled_features[feature] = toggle_var.get()
        
        # 保存到账户
        if self.player_data.username:
            self.account_manager.update_account(self.player_data.username, {
                "enabled_features": self.player_data.enabled_features
            })
        
        # 显示保存成功提示
        success_label = tk.Label(self.root, text="设置保存成功！", font=("Arial", 16), fg="#00FF00", bg="#000000")
        success_label.pack(pady=10)
        
        # 2秒后返回主菜单
        self.root.after(2000, self.show_main_menu)
    
    def start_game(self):
        # 清除当前窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建游戏界面
        self.game_frame = tk.Frame(self.root, bg="#000000")
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        
        # 返回按钮
        back_button = tk.Button(self.game_frame, text="返回主菜单", font=("Arial", 12), 
                              bg="#FF0000", fg="#FFFFFF", command=self.show_main_menu)
        back_button.pack(anchor=tk.NW, padx=10, pady=10)
        
        # 哈夫币显示
        self.coin_label = tk.Label(self.game_frame, text=f"哈夫币: {self.player_data.haf_coin}", 
                                 font=("Arial", 14), fg="#FFD700", bg="#000000")
        self.coin_label.pack(anchor=tk.NE, padx=10, pady=10)
        
        # 密码锁框架
        self.lock_frame = tk.Frame(self.game_frame, bg="#000000")
        self.lock_frame.pack(expand=True, fill=tk.BOTH)
        
        # 创建五列符号
        self.columns = []
        self.locked = [False] * COLUMNS
        self.target_symbols = []
        
        # 生成目标密码
        for i in range(COLUMNS):
            target = random.choice(SYMBOL_SET)
            self.target_symbols.append(target)
        
        # 为每列随机分配不同的行位置放置正确符号
        target_rows = []
        while len(target_rows) < COLUMNS:
            row = random.randint(0, ROWS - 1)
            if row not in target_rows:
                target_rows.append(row)
        
        # 创建每列
        for col in range(COLUMNS):
            column_frame = tk.Frame(self.lock_frame, bg="#000000", bd=2, relief=tk.RAISED)
            column_frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
            
            # 设置列权重
            self.lock_frame.grid_columnconfigure(col, weight=1)
            
            column_symbols = []
            for row in range(ROWS):
                # 根据分配的行位置放置正确的符号
                if row == target_rows[col]:
                    symbol = self.target_symbols[col]
                else:
                    symbol = random.choice(SYMBOL_SET)
                    
                label = tk.Label(column_frame, text=symbol, font=("Courier", 20), 
                               width=4, height=2, bg="#333333", fg="#FFFFFF")
                label.grid(row=row, column=0, sticky="nsew")
                column_frame.grid_rowconfigure(row, weight=1)
                column_symbols.append(label)
            
            # 标记正确符号为绿色
            column_symbols[target_rows[col]].config(fg="#00FF00")
            self.columns.append(column_symbols)
        
        # 设置行权重
        self.lock_frame.grid_rowconfigure(0, weight=1)
        
        # 状态标签
        self.status_label = tk.Label(self.game_frame, text="使用 ← → 键选择列，按空格键锁定正确的符号", 
                                   font=("Arial", 16), fg="#00FF00", bg="#000000")
        self.status_label.pack(pady=20)
        
        # 开始滚动
        # 根据是否购买了快速滚动且已开启来设置速度
        if 'scroll_speed' in self.player_data.unlocked_features and self.player_data.enabled_features.get('scroll_speed', True):
            self.scroll_speed = 800  # 快速滚动 - 0.8秒
        else:
            self.scroll_speed = 1000  # 正常滚动 - 1秒
            
        self.is_rolling = True
        self.lock_count = 0
        self.game_start_time = time.time()
        self.current_column = 0  # 当前选中的列
        self.errors_allowed = 0  # 允许的错误次数
        
        # 检查是否购买了额外生命且已开启
        if 'extra_life' in self.player_data.unlocked_features and self.player_data.enabled_features.get('extra_life', True):
            self.errors_allowed = 1
        
        # 加倍下注状态
        if not hasattr(self, 'is_double_bet'):
            self.is_double_bet = False
            self.double_bet_amount = 0
        
        # 绑定键盘事件
        self.root.bind("<space>", self.lock_symbol)
        self.root.bind("<Left>", self.select_previous_column)
        self.root.bind("<Right>", self.select_next_column)
        
        # 高亮当前选中的列
        self.highlight_current_column()
        
        # 开始滚动动画
        self.roll_symbols()
    
    def roll_symbols(self):
        if not self.is_rolling:
            return
        
        try:
            for col in range(COLUMNS):
                if not self.locked[col]:
                    # 滚动符号
                    column = self.columns[col]
                    # 获取当前所有符号
                    symbols = []
                    for label in column:
                        try:
                            symbols.append(label.cget("text"))
                        except tk.TclError:
                            # 标签已被销毁，停止滚动
                            self.is_rolling = False
                            return
                    
                    # 将最后一个符号移到最前面
                    symbols.insert(0, symbols.pop())
                    # 更新标签
                    for row in range(ROWS):
                        label = column[row]
                        try:
                            label.config(text=symbols[row])
                            
                            # 检查是否是目标符号，如果是则变绿
                            if symbols[row] == self.target_symbols[col]:
                                label.config(fg="#00FF00")
                            elif 'error_hint' in self.player_data.unlocked_features and self.player_data.enabled_features.get('error_hint', True) and symbols[row] != self.target_symbols[col]:
                                # 错误提示：如果购买了该功能且已开启，错误符号变为橙色
                                label.config(fg="#FFA500")
                            else:
                                label.config(fg="#FFFFFF")
                        except tk.TclError:
                            # 标签已被销毁，停止滚动
                            self.is_rolling = False
                            return
                    
                    # 自动瞄准：如果购买了该功能且已开启，当正确符号接近中间行时给出提示
                    if 'auto_aim' in self.player_data.unlocked_features and self.player_data.enabled_features.get('auto_aim', True):
                        middle_row = ROWS // 2
                        # 检查正确符号是否在中间行附近（上下各一行）
                        near_middle = False
                        for row in [middle_row-1, middle_row, middle_row+1]:
                            if row >= 0 and row < ROWS:
                                if symbols[row] == self.target_symbols[col]:
                                    near_middle = True
                                    break
                        
                        # 如果接近中间行，改变列边框颜色
                        if near_middle and not self.locked[col]:
                            try:
                                column[middle_row].config(bg="#FFFF00", fg="#000000")
                            except tk.TclError:
                                self.is_rolling = False
                                return
                        else:
                            try:
                                column[middle_row].config(bg="#333333")
                            except tk.TclError:
                                self.is_rolling = False
                                return
        except Exception:
            # 发生任何错误，停止滚动
            self.is_rolling = False
            return
        
        # 继续滚动
        self.root.after(self.scroll_speed, self.roll_symbols)
    
    def lock_symbol(self, event):
        # 只锁定当前选中的列
        col = self.current_column
        if not self.locked[col]:
            column = self.columns[col]
            current_symbol = column[ROWS // 2].cget("text")
            
            if current_symbol == self.target_symbols[col]:
                # 锁定正确
                self.locked[col] = True
                self.lock_count += 1
                column[ROWS // 2].config(bg="#00FF00", fg="#000000")
                self.status_label.config(text=f"锁定正确！已锁定 {self.lock_count}/{COLUMNS}")
                
                # 检查是否所有列都锁定正确
                if self.lock_count == COLUMNS:
                    self.win_game()
                else:
                    # 自动选择下一个未锁定的列
                    self.select_next_unlocked_column()
            else:
                # 锁定错误
                if self.errors_allowed > 0:
                    # 使用额外生命
                    self.errors_allowed -= 1
                    self.status_label.config(text=f"锁定错误！剩余额外生命: {self.errors_allowed}")
                    # 自动选择下一个未锁定的列
                    self.select_next_unlocked_column()
                else:
                    # 没有额外生命了，游戏失败
                    # 检查是否处于加倍下注状态
                    if self.is_double_bet:
                        # 加倍下注失败，显示失败信息并扣除奖金
                        self.player_data.haf_coin -= self.double_bet_amount  # 真正扣除哈夫币
                        
                        # 保存哈夫币变化
                        self.account_manager.save_player_data(self.player_data)
                        
                        self.status_label.config(text=f"锁定错误！游戏失败\n加倍下注失败！失去了 {self.double_bet_amount} 个哈夫币！")
                        self.is_double_bet = False
                        self.double_bet_amount = 0
                    else:
                        self.status_label.config(text="锁定错误！游戏失败")
                        
                    self.is_rolling = False
                    # 显示重新开始按钮
                    restart_button = tk.Button(self.game_frame, text="重新开始", font=(
                        "Arial", 16), bg="#00FF00", fg="#000000", command=self.start_game)
                    restart_button.pack(pady=20)
    
    def select_previous_column(self, event):
        # 选择上一列
        self.current_column = (self.current_column - 1) % COLUMNS
        self.highlight_current_column()
    
    def select_next_column(self, event):
        # 选择下一列
        self.current_column = (self.current_column + 1) % COLUMNS
        self.highlight_current_column()
    
    def select_next_unlocked_column(self):
        # 选择下一个未锁定的列
        start_col = self.current_column
        while True:
            self.current_column = (self.current_column + 1) % COLUMNS
            if not self.locked[self.current_column] or self.current_column == start_col:
                break
        self.highlight_current_column()
    
    def highlight_current_column(self):
        # 高亮当前选中的列
        for col in range(COLUMNS):
            column_frame = self.columns[col][0].master
            if col == self.current_column:
                column_frame.config(bg="#FFFF00", bd=3)  # 高亮为黄色
            else:
                column_frame.config(bg="#000000", bd=2)  # 恢复默认
    
    def win_game(self):
        self.is_rolling = False
        self.status_label.config(text="恭喜通关！")
        
        # 处理加倍下注奖励
        if self.is_double_bet:
            # 加倍下注成功，给予双倍奖励
            self.player_data.haf_coin += 2  # 获得2个哈夫币（双倍奖励）
            self.is_double_bet = False
            self.double_bet_amount = 0
            
            # 保存哈夫币变化
            self.account_manager.save_player_data(self.player_data)
        
        # 创建奖励界面
        self.create_reward_screen()
    
    def create_reward_screen(self):
        # 创建奖励界面窗口
        reward_window = tk.Toplevel(self.root)
        reward_window.title("奖励界面")
        reward_window.geometry("400x300")
        reward_window.configure(bg="#000000")
        reward_window.resizable(False, False)
        
        # 禁止关闭主窗口
        self.root.attributes("-disabled", True)
        
        # 奖励标题
        reward_title = tk.Label(reward_window, text="🎉 恭喜通关！ 🎉", font=(
            "Arial", 20, "bold"), fg="#FFD700", bg="#000000")
        reward_title.pack(pady=30)
        
        # 获得哈夫币标签
        coin_reward = tk.Label(reward_window, text="获得1个哈夫币！", font=(
            "Arial", 16), fg="#FFD700", bg="#000000")
        coin_reward.pack(pady=20)
        
        # 等待1秒后显示下注选项
        reward_window.after(1000, lambda: self.show_bet_options(reward_window))
    
    def show_bet_options(self, reward_window):
        # 清除当前奖励界面的内容
        for widget in reward_window.winfo_children():
            widget.destroy()
        
        # 新的标题
        bet_title = tk.Label(reward_window, text="🎰 加倍机会！ 🎰", font=(
            "Arial", 20, "bold"), fg="#FFD700", bg="#000000")
        bet_title.pack(pady=30)
        
        # 下注说明
        bet_desc = tk.Label(reward_window, text="是否加倍下注？", font=(
            "Arial", 16), fg="#00FF00", bg="#000000")
        bet_desc.pack(pady=20)
        
        # 按钮框架
        button_frame = tk.Frame(reward_window, bg="#000000")
        button_frame.pack(pady=20)
        
        # 加倍按钮
        double_button = tk.Button(button_frame, text="加倍下注", font=(
            "Arial", 14, "bold"), width=12, height=2, 
            bg="#FF0000", fg="#FFFFFF", 
            command=lambda: self.handle_bet(reward_window, True))
        double_button.pack(side=tk.LEFT, padx=10)
        
        # 停止按钮
        stop_button = tk.Button(button_frame, text="停止下注", font=(
            "Arial", 14, "bold"), width=12, height=2, 
            bg="#00FF00", fg="#000000", 
            command=lambda: self.handle_bet(reward_window, False))
        stop_button.pack(side=tk.RIGHT, padx=10)
    
    def handle_bet(self, reward_window, double_bet):
        if double_bet:
            # 加倍下注：立即扣除当前赢的奖金作为赌注
            self.player_data.haf_coin += 1  # 先给玩家当前的奖金
            self.player_data.haf_coin -= 1  # 立即扣除作为赌注
            self.is_double_bet = True
            self.double_bet_amount = 1  # 当前这把的奖金作为赌注
            result = "🎯 加倍下注成功！🎯\n已扣除1个哈夫币作为赌注。\n下一把赢了获得2倍奖金（2个哈夫币），输了失去赌注！"
            result_fg = "#FFA500"
        else:
            # 停止下注，获得1个哈夫币
            self.player_data.haf_coin += 1
            self.is_double_bet = False
            result = "获得1个哈夫币！"
            result_fg = "#FFD700"
        
        # 保存哈夫币变化
        self.account_manager.save_player_data(self.player_data)
        
        # 更新奖励界面
        for widget in reward_window.winfo_children():
            widget.destroy()
        
        # 结果标题
        result_label = tk.Label(reward_window, text=result, font=(
            "Arial", 16), fg=result_fg, bg="#000000", justify="center")
        result_label.pack(pady=50)
        
        # 最终哈夫币数量
        final_coin_label = tk.Label(reward_window, text=f"最终哈夫币: {self.player_data.haf_coin}", 
                                  font=("Arial", 14), fg="#FFD700", bg="#000000")
        final_coin_label.pack(pady=10)
        
        # 3秒后自动关闭奖励界面并返回主页
        def close_reward():
            reward_window.destroy()
            self.root.attributes("-disabled", False)  # 启用主窗口
            self.show_main_menu()
        
        reward_window.after(3000, close_reward)
    
    def show_shop(self):
        # 检查用户是否被禁用了商店
        if self.player_data.username:
            user_account = self.account_manager.accounts.get(self.player_data.username)
            if user_account and user_account.get("shop_disabled", False):
                # 显示商店禁用提示
                for widget in self.root.winfo_children():
                    widget.destroy()
                
                disabled_frame = tk.Frame(self.root, bg="#000000")
                disabled_frame.pack(fill=tk.BOTH, expand=True)
                
                # 返回按钮
                back_button = tk.Button(disabled_frame, text="返回主菜单", font=("Arial", 12), 
                                      bg="#FF0000", fg="#FFFFFF", command=self.show_main_menu)
                back_button.pack(anchor=tk.NW, padx=10, pady=10)
                
                # 禁用提示
                disabled_label = tk.Label(disabled_frame, text="商店功能已被禁用", font=("Arial", 24, "bold"), 
                                        fg="#FF0000", bg="#000000")
                disabled_label.pack(expand=True)
                
                return
        
        # 清除当前窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建商店界面
        shop_frame = tk.Frame(self.root, bg="#000000")
        shop_frame.pack(fill=tk.BOTH, expand=True)
        
        # 返回按钮
        back_button = tk.Button(shop_frame, text="返回主菜单", font=("Arial", 12), 
                              bg="#FF0000", fg="#FFFFFF", command=self.show_main_menu)
        back_button.pack(anchor=tk.NW, padx=10, pady=10)
        
        # 哈夫币显示
        coin_label = tk.Label(shop_frame, text=f"哈夫币: {self.player_data.haf_coin}", 
                            font=("Arial", 16), fg="#FFD700", bg="#000000")
        coin_label.pack(pady=20)
        
        # 商店标题
        shop_title = tk.Label(shop_frame, text="商店", font=("Arial", 20, "bold"), fg="#00FF00", bg="#000000")
        shop_title.pack(pady=10)
        
        # 创建带滚动条的商品区域
        canvas = tk.Canvas(shop_frame, bg="#000000", bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(shop_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#000000")
        
        # 配置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 商品列表
        shop_items = [
            {"name": "快速滚动", "description": "增加滚动速度", "price": 3, "effect": "scroll_speed"},
            {"name": "自动瞄准", "description": "正确符号接近中间时提示", "price": 5, "effect": "auto_aim"},
            {"name": "错误提示", "description": "显示错误的符号", "price": 4, "effect": "error_hint"},
            {"name": "额外生命", "description": "允许一次错误", "price": 6, "effect": "extra_life"},
        ]
        
        for i, item in enumerate(shop_items):
            item_frame = tk.Frame(scrollable_frame, bg="#333333", bd=2, relief=tk.RAISED)
            item_frame.grid(row=i, column=0, padx=20, pady=10, sticky="ew")
            
            # 设置商品框架的列权重
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_columnconfigure(1, weight=0)
            
            # 商品名称
            name_label = tk.Label(item_frame, text=item["name"], font=("Arial", 14, "bold"), 
                                fg="#00FF00", bg="#333333")
            name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # 商品描述
            desc_label = tk.Label(item_frame, text=item["description"], font=("Arial", 12), 
                                fg="#FFFFFF", bg="#333333")
            desc_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            
            # 价格
            price_label = tk.Label(item_frame, text=f"价格: {item['price']} 哈夫币", font=("Arial", 12), 
                                 fg="#FFD700", bg="#333333")
            price_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            
            # 购买按钮
            buy_button = tk.Button(item_frame, text="购买", font=("Arial", 12), 
                                 bg="#00FF00", fg="#000000", 
                                 command=lambda item=item: self.buy_item(item))
            buy_button.grid(row=1, column=1, padx=10, pady=5, sticky="e")
            
            # 设置已购买的商品状态
            if item["effect"] in self.player_data.unlocked_features:
                buy_button.config(text="已购买", state=tk.DISABLED, bg="#666666")
        
        # 设置可滚动区域的列权重
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # 放置滚动区域和滚动条
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # 允许使用鼠标滚轮滚动
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def buy_item(self, item):
        if self.player_data.haf_coin >= item["price"]:
            if item["effect"] not in self.player_data.unlocked_features:
                self.player_data.haf_coin -= item["price"]
                self.player_data.unlocked_features.append(item["effect"])
                # 新购买的功能默认开启
                self.player_data.enabled_features[item["effect"]] = True
                # 保存账户数据
                if self.player_data.username:
                    self.account_manager.update_account(self.player_data.username, {
                        "haf_coin": self.player_data.haf_coin,
                        "unlocked_features": self.player_data.unlocked_features,
                        "enabled_features": self.player_data.enabled_features
                    })
                self.show_main_menu()  # 返回主菜单刷新
        

# 运行游戏
if __name__ == "__main__":
    root = tk.Tk()
    game = DeltaLockGame(root)
    root.mainloop()