#!/usr/bin/env python3
"""
导航菜单组件测试套件
"""
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from psy_admin_vue.src.components.NavigationMenu import NavigationMenu
from psy_admin_vue.src.router.index import routes

class TestNavigationMenu:
    """导航菜单组件测试"""
    
    def test_menu_structure(self):
        """测试菜单结构"""
        # 渲染导航菜单组件
        menu = NavigationMenu()
        
        # 验证菜单项
        menu_items = menu.$el.querySelectorAll('.menu-item')
        assert len(menu_items) == 5  # 假设菜单有5个项
        
        # 验证菜单项文本
        expected_texts = ['首页', '学生管理', '检测记录', '报表中心', '系统设置']
        for item, expected_text in zip(menu_items, expected_texts):
            assert item.textContent.strip() == expected_text
    
    def test_active_menu_item(self):
        """测试活动菜单项高亮"""
        # 模拟路由变化
        with patch('vue-router') as router_mock:
            router_mock.currentRoute.value = '/students'
            
            # 渲染导航菜单
            menu = NavigationMenu()
            
            # 验证活动菜单项
            active_item = menu.$el.querySelector('.menu-item.active')
            assert active_item.textContent.strip() == '学生管理'
    
    def test_menu_click_handler(self):
        """测试菜单点击处理程序"""
        # 模拟点击事件
        with patch.object(NavigationMenu.methods, 'handleMenuItemClick') as mock_click:
            menu = NavigationMenu()
            menu.handleMenuItemClick({ target: { textContent: '学生管理' } })
            
            # 验证点击处理程序被调用
            mock_click.assert_called_once()
    
    def test_menu_icon_display(self):
        """测试菜单图标显示"""
        # 渲染导航菜单
        menu = NavigationMenu()
        
        # 验证每个菜单项都有图标
        menu_items = menu.$el.querySelectorAll('.menu-item')
        for item in menu_items:
            icon_element = item.querySelector('.menu-icon')
            assert icon_element is not None
    
    def test_menu_collapsed_state(self):
        """测试菜单折叠状态"""
        # 模拟小屏幕设备
        with patch('window.innerWidth', 768):
            menu = NavigationMenu()
            
            # 验证菜单处于折叠状态
            collapsed_class = menu.$el.classList.contains('collapsed')
            assert collapsed_class is True
            
            # 验证折叠状态下菜单项显示正确
            menu_items = menu.$el.querySelectorAll('.menu-item')
            for item in menu_items:
                assert 'hidden-xs' in item.className

class TestNavigationMenuIntegration:
    """导航菜单集成测试"""
    
    def test_route_change_on_menu_click(self):
        """测试点击菜单项时的路由变化"""
        # 模拟路由器
        router = Mock()
        router.push = Mock()
        
        # 渲染导航菜单并注入路由器
        menu = NavigationMenu()
        menu.$router = router
        
        # 点击菜单项
        menu.handleMenuItemClick({ target: { textContent: '检测记录' } })
        
        # 验证路由跳转
        router.push.assert_called_once_with('/test-records')

class TestNavigationMenuAccessibility:
    """导航菜单可访问性测试"""
    
    def test_keyboard_navigation(self):
        """测试键盘导航"""
        # 渲染导航菜单
        menu = NavigationMenu()
        
        # 模拟键盘焦点
        menu_items = menu.$el.querySelectorAll('.menu-item')
        menu_items[0].focus()
        
        # 验证焦点样式
        focused_item = document.activeElement
        assert focused_item === menu_items[0]
        
        # 测试Tab键导航
        from selenium.webdriver.common.keys import Keys
        focused_item.send_keys(Keys.TAB)
        
        # 验证下一个菜单项获得焦点
        next_focused_item = document.activeElement
        assert next_focused_item === menu_items[1]

if __name__ == '__main__':
    # 运行测试
    import pytest
    pytest.main([__file__, '-v'])
