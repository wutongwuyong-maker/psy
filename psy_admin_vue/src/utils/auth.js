// JWT工具函数
import jwtDecode from "jwt-decode";

/**
 * 检查token是否过期
 * @param {string} token - JWT token
 * @returns {boolean} - 是否过期
 */
export function isTokenExpired(token) {
  if (!token) return true;

  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    console.error("Token解析失败:", error);
    return true;
  }
}

/**
 * 获取token过期时间
 * @param {string} token - JWT token
 * @returns {Date|null} - 过期时间
 */
export function getTokenExpiration(token) {
  if (!token) return null;

  try {
    const decoded = jwtDecode(token);
    return new Date(decoded.exp * 1000);
  } catch (error) {
    console.error("Token解析失败:", error);
    return null;
  }
}

/**
 * 检查并清理过期的token
 */
export function checkAndCleanExpiredToken() {
  const token = localStorage.getItem("access_token");
  if (token && isTokenExpired(token)) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_info");
    return true;
  }
  return false;
}

/**
 * 获取token剩余时间（秒）
 * @param {string} token - JWT token
 * @returns {number} - 剩余秒数
 */
export function getTokenRemainingTime(token) {
  if (!token) return 0;

  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return Math.max(0, decoded.exp - currentTime);
  } catch (error) {
    console.error("Token解析失败:", error);
    return 0;
  }
}
