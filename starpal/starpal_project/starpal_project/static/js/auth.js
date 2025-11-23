/**
 * 认证页面逻辑模块
 * 处理登录和注册功能
 */

class AuthManager {
    constructor() {
        this.initializeEventListeners();
        this.setupPasswordToggles();
    }

    /**
     * 初始化事件监听器
     */
    initializeEventListeners() {
        // 表单切换事件
        document.getElementById('flipToRegister')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.switchToRegister();
        });
        
        document.getElementById('flipToLogin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.switchToLogin();
        });

        // 表单提交事件
        document.getElementById('loginForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        document.getElementById('registerForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });

        // 登录页头像上传与预览
        const loginAvatarInput = document.getElementById('loginAvatarInput');
        const loginUserAvatar = document.getElementById('loginUserAvatar');
        if (loginAvatarInput && loginUserAvatar) {
            // 预览已存头像
            const saved = localStorage.getItem('userAvatar');
            if (saved) loginUserAvatar.src = saved;
            loginAvatarInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = function(evt) {
                    if (evt.target.result) {
                        localStorage.setItem('userAvatar', evt.target.result);
                        loginUserAvatar.src = evt.target.result;
                    }
                };
                reader.readAsDataURL(file);
            });
        }

        // 注册页头像上传与预览
        const regAvatarInput = document.getElementById('register-avatar-input');
        const regAvatarImg = document.getElementById('register-avatar-img');
        if (regAvatarInput && regAvatarImg) {
            // 预览已存头像
            const saved = localStorage.getItem('userAvatar');
            if (saved) regAvatarImg.src = saved;
            regAvatarInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = function(evt) {
                    if (evt.target.result) {
                        localStorage.setItem('userAvatar', evt.target.result);
                        regAvatarImg.src = evt.target.result;
                    }
                };
                reader.readAsDataURL(file);
            });
        }
    }

    /**
     * 设置密码显示/隐藏功能
     */
    setupPasswordToggles() {
        const toggles = [
            { toggleId: 'loginPasswordToggle', inputId: 'login-password' },
            { toggleId: 'registerPasswordToggle', inputId: 'register-password' },
            { toggleId: 'confirmPasswordToggle', inputId: 'register-confirm' }
        ];

        toggles.forEach(({ toggleId, inputId }) => {
            this.setupPasswordToggle(toggleId, inputId);
        });
    }

    /**
     * 设置单个密码切换按钮
     * @param {string} toggleId - 切换按钮ID
     * @param {string} inputId - 输入框ID
     */
    setupPasswordToggle(toggleId, inputId) {
        const toggle = document.getElementById(toggleId);
        const input = document.getElementById(inputId);
        
        if (toggle && input) {
            toggle.addEventListener('click', () => {
                const isPassword = input.getAttribute('type') === 'password';
                const newType = isPassword ? 'text' : 'password';
                input.setAttribute('type', newType);
                
                const icon = toggle.querySelector('i');
                if (icon) {
                    icon.className = isPassword ? 'ri-eye-line' : 'ri-eye-off-line';
                }
            });
        }
    }

    /**
     * 切换到登录表单
     */
    switchToLogin() {
        const authCard = document.getElementById('authCard');
        const registerForm = document.getElementById('registerForm');
        const loginForm = document.getElementById('loginForm');
        
        authCard?.classList.remove('flipped');
        registerForm?.classList.remove('active');
        loginForm?.classList.add('active');
    }
    
    /**
     * 切换到注册表单
     */
    switchToRegister() {
        const authCard = document.getElementById('authCard');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        
        authCard?.classList.add('flipped');
        loginForm?.classList.remove('active');
        registerForm?.classList.add('active');
    }

    /**
     * 处理登录
     */
    async handleLogin() {
        const username = document.getElementById('login-username')?.value.trim();
        const password = document.getElementById('login-password')?.value;
        
        // 验证输入
        if (!this.validateLoginInput(username, password)) {
            return;
        }

        try {
            // 显示加载状态
            this.setLoginButtonLoading(true);
            
            // 调用登录API
            const data = await apiClient.login(username, password);
            
            // 登录成功
            if (data.username) {
                storageManager.setCurrentUser(data.username, data.name);
                // 登录后强制新建新对话并设为当前
                if (typeof storageManager.createNewChat === 'function') {
                    const newChat = storageManager.createNewChat();
                    storageManager.setCurrentChatId(newChat.id);
                }
                // 添加成功提示动画
                Utils.showToast('登录成功！正在跳转...', 2000);
                
                // 延迟跳转以显示提示
                setTimeout(() => {
                    window.location.href = 'chat.html';
                }, 1000);
            } else {
                Utils.showToast(data.message || '登录失败');
            }
        } catch (error) {
            console.error('登录错误:', error);
            Utils.showToast(error.message || '登录失败，请稍后重试');
        } finally {
            this.setLoginButtonLoading(false);
        }
    }

    /**
     * 处理注册
     */
    async handleRegister() {
        const name = document.getElementById('register-name')?.value.trim();
        const username = document.getElementById('register-username')?.value.trim();
        const password = document.getElementById('register-password')?.value;
        const confirm = document.getElementById('register-confirm')?.value;
        
        // 验证输入
        if (!this.validateRegisterInput(name, username, password, confirm)) {
            return;
        }

        try {
            // 显示加载状态
            this.setRegisterButtonLoading(true);
            
            // 调用注册API
            const data = await apiClient.register(name, username, password);
            
            // 注册成功
            Utils.showToast(data.message || '注册成功！');
            
            if (data.message === '注册成功，请登录！') {
                // 清空注册表单
                this.clearRegisterForm();
                
                // 延迟切换到登录表单
                setTimeout(() => {
                    this.switchToLogin();
                }, 1500);
            }
        } catch (error) {
            console.error('注册错误:', error);
            Utils.showToast(error.message || '注册失败，请稍后重试');
        } finally {
            this.setRegisterButtonLoading(false);
        }
    }

    /**
     * 验证登录输入
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {boolean} 是否验证通过
     */
    validateLoginInput(username, password) {
        if (!username || !password) {
            Utils.showToast('请填写完整的登录信息');
            return false;
        }

        if (!Utils.validateEmail(username)) {
            Utils.showEmailError('login-email-err', true, '邮箱格式不正确');
            return false;
        }

        Utils.showEmailError('login-email-err', false);
        return true;
    }

    /**
     * 验证注册输入
     * @param {string} name - 姓名
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @param {string} confirm - 确认密码
     * @returns {boolean} 是否验证通过
     */
    validateRegisterInput(name, username, password, confirm) {
        if (!name || !username || !password || !confirm) {
            Utils.showToast('请填写完整的注册信息');
            return false;
        }

        if (name.length > 20) {
            Utils.showToast('姓名长度不能超过20个字符');
            return false;
        }

        if (!Utils.validateEmail(username)) {
            Utils.showEmailError('register-email-err', true, '邮箱格式不正确');
            return false;
        }

        if (password.length < 6) {
            Utils.showToast('密码长度至少6位');
            return false;
        }

        if (password !== confirm) {
            Utils.showToast('两次输入的密码不一致！');
            return false;
        }

        Utils.showEmailError('register-email-err', false);
        return true;
    }

    /**
     * 设置登录按钮加载状态
     * @param {boolean} loading - 是否加载中
     */
    setLoginButtonLoading(loading) {
        const button = document.querySelector('#loginForm button[type="submit"]');
        const span = button?.querySelector('span');
        const icon = button?.querySelector('i');
        
        if (button && span) {
            button.disabled = loading;
            span.textContent = loading ? '登录中...' : '登录';
            
            if (icon) {
                icon.className = loading ? 'ri-loader-4-line' : 'ri-arrow-right-line';
                if (loading) {
                    icon.style.animation = 'spin 1s linear infinite';
                } else {
                    icon.style.animation = '';
                }
            }
        }
    }

    /**
     * 设置注册按钮加载状态
     * @param {boolean} loading - 是否加载中
     */
    setRegisterButtonLoading(loading) {
        const button = document.querySelector('#registerForm button[type="submit"]');
        const span = button?.querySelector('span');
        const icon = button?.querySelector('i');
        
        if (button && span) {
            button.disabled = loading;
            span.textContent = loading ? '注册中...' : '创建账户';
            
            if (icon) {
                icon.className = loading ? 'ri-loader-4-line' : 'ri-arrow-right-line';
                if (loading) {
                    icon.style.animation = 'spin 1s linear infinite';
                } else {
                    icon.style.animation = '';
                }
            }
        }
    }

    /**
     * 清空注册表单
     */
    clearRegisterForm() {
        const form = document.getElementById('registerForm');
        if (form) {
            form.reset();
        }
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// 页面加载完成后初始化认证管理器
document.addEventListener('DOMContentLoaded', () => {
    new AuthManager();
});

// 导出认证管理器类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthManager;
}
