/**
 * junior2api Token Extractor
 * 
 * 粘贴到 junior.so 的 F12 > Console，然后发一条消息，token 自动复制到剪贴板
 */
(function () {
  if (!location.hostname.includes('junior.so')) {
    alert('请在 junior.so 页面运行此脚本');
    return;
  }

  const _origFetch = window.fetch;
  let captured = false;

  window.fetch = function (url, opts = {}) {
    if (!captured && typeof url === 'string' && url.includes('/messages')) {
      const h = opts.headers || {};
      const token = h['token'] || h['Token'] || '';
      const uid = h['uid'] || h['Uid'] || '';
      const tenantId = h['junior-id'] || h['Junior-Id'] || '';

      if (token) {
        captured = true;
        const envText = [
          `JUNIOR_TOKEN=${token}`,
          `JUNIOR_UID=${uid}`,
          `JUNIOR_TENANT_ID=${tenantId}`,
        ].join('\n');

        navigator.clipboard.writeText(envText)
          .then(() => {
            console.log('%c✅ Token 已复制到剪贴板！', 'color: green; font-size: 16px');
            console.log('%c复制以下内容到 .env 文件：', 'color: blue');
            console.log(envText);
          })
          .catch(() => {
            console.log('%c✅ 获取成功，请手动复制：', 'color: green; font-size: 16px');
            console.log(envText);
          });

        window.fetch = _origFetch;
      }
    }
    return _origFetch.apply(this, arguments);
  };

  console.log('%c🟡 监听已启动，请发一条消息给 Junior...', 'color: orange; font-size: 14px');
})();
