# How to get your Junior.so token

Junior.so uses magic-link login (email code, no password), so junior2api uses a static token from your browser.

## 方式一：一行脚本（推荐，最简单）

1. 打开 [junior.so](https://junior.so)，登录
2. 按 **F12** 打开 DevTools → 点击 **Console** 标签
3. 粘贴以下代码，按回车：

```javascript
(function(){const o=window.fetch;let d=false;window.fetch=function(u,p={}){if(!d&&typeof u==='string'&&u.includes('/messages')){const h=p.headers||{};const t=h['token']||'';const uid=h['uid']||'';const tid=h['junior-id']||'';if(t){d=true;const e=`JUNIOR_TOKEN=${t}\nJUNIOR_UID=${uid}\nJUNIOR_TENANT_ID=${tid}`;navigator.clipboard.writeText(e).then(()=>console.log('%c\u2705 已复制！粘贴到 .env 即可\n\n'+e,'color:green;font-size:14px')).catch(()=>console.log('%c\u2705 请手动复制：\n\n'+e,'color:green'));window.fetch=o;}}return o.apply(this,arguments);};console.log('%c\ud83d\udfe1 已就绪，请发一条消息给 Junior...','color:orange;font-size:14px');})();
```

4. **发一条消息**给 Junior
5. Console 里会显示 `.env` 内容，同时自动复制到剪贴板 ✅

---

## 方式二：书签工具（Bookmarklet）

将以下代码保存为浏览器书签（URL 字段），在 junior.so 页面点击书签后发一条消息即可：

```
javascript:(function(){const o=window.fetch;let d=false;window.fetch=function(u,p={}){if(!d&&typeof u==='string'&&u.includes('/messages')){const h=p.headers||{};const t=h['token']||'';const uid=h['uid']||'';const tid=h['junior-id']||'';if(t){d=true;const e='JUNIOR_TOKEN='+t+'\nJUNIOR_UID='+uid+'\nJUNIOR_TENANT_ID='+tid;navigator.clipboard.writeText(e).then(()=>alert('\u2705 \u5df2\u590d\u5236\u5230\u526a\u8d34\u677f\uff01\n\n\u7c98\u8d34\u5230 .env \u6587\u4ef6\uff1a\n\n'+e)).catch(()=>alert('\u2705 \u8bf7\u624b\u52a8\u590d\u5236\uff1a\n\n'+e));window.fetch=o;}}return o.apply(this,arguments);};alert('\ud83d\udfe1 \u76d1\u542c\u5df2\u542f\u52a8\uff0c\u8bf7\u53d1\u4e00\u6761\u6d88\u606f\u7ed9 Junior...');})();
```

---

## 方式三：DevTools Network（手动）

1. F12 → **Network** 标签
2. 发一条消息
3. 点击 `messages` 请求 → **Headers** → 复制 `token`、`uid`、`junior-id`

---

## 复制完成后

把内容粘贴到 `.env`：

```env
JUNIOR_TOKEN=niwQc7CoO0VCVLx4d...
JUNIOR_UID=u_1f054c3ec4560fb4
JUNIOR_TENANT_ID=tm_90c590ee8b67f70f
```

## Token 有效期

Token 是长期 session token，退出 Junior.so 登录才会失效。失效后重复上面步骤即可。
