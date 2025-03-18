/**
 * 股票回测平台主JavaScript文件
 */

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化搜索框
    initSearchBox();
    
    // 设置活动导航项
    setActiveNavItem();
});

/**
 * 初始化Bootstrap工具提示
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * 初始化搜索框功能
 */
function initSearchBox() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const symbol = searchInput.value.trim().toUpperCase();
            if (symbol) {
                window.location.href = `/stock/${symbol}`;
            }
        }
    });
}

/**
 * 设置当前活动导航项
 */
function setActiveNavItem() {
    const pathname = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (pathname === href || (href !== '/' && pathname.startsWith(href))) {
            link.classList.add('active');
        }
    });
}

/**
 * 格式化数字为千分位分隔的字符串
 * @param {number} num - 要格式化的数字
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的字符串
 */
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined || isNaN(num)) {
        return '-';
    }
    return new Intl.NumberFormat('zh-CN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
}

/**
 * 格式化百分比
 * @param {number} value - 要格式化的值 (0.01 = 1%)
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的百分比字符串
 */
function formatPercent(value, decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) {
        return '-';
    }
    // 确保值是数字类型
    const percent = parseFloat(value);
    return new Intl.NumberFormat('zh-CN', {
        style: 'percent',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(percent / 100);
}

/**
 * 格式化货币
 * @param {number} value - 要格式化的金额
 * @param {string} currency - 货币代码, 默认USD
 * @returns {string} 格式化后的货币字符串
 */
function formatCurrency(value, currency = 'USD') {
    if (value === null || value === undefined || isNaN(value)) {
        return '-';
    }
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期对象或字符串
 * @param {string} format - 格式 ('short', 'medium', 'long')
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(date, format = 'short') {
    if (!date) return '-';
    
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (isNaN(dateObj.getTime())) {
        return '-';
    }
    
    let options = {};
    switch (format) {
        case 'short':
            options = { year: 'numeric', month: '2-digit', day: '2-digit' };
            break;
        case 'medium':
            options = { year: 'numeric', month: 'short', day: 'numeric' };
            break;
        case 'long':
            options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
            break;
    }
    
    return dateObj.toLocaleDateString('zh-CN', options);
}

/**
 * 工具函数：防抖
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖处理后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

/**
 * 工具函数：节流
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 节流处理后的函数
 */
function throttle(func, limit) {
    let lastFunc;
    let lastRan;
    return function() {
        const context = this;
        const args = arguments;
        if (!lastRan) {
            func.apply(context, args);
            lastRan = Date.now();
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(function() {
                if ((Date.now() - lastRan) >= limit) {
                    func.apply(context, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
} 