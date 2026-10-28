/* Ghost Light — Android app shim.
   Runs before the main page script. Provides AI through the user's own Anthropic API key
   (claude.ai's built-in AI is only available inside claude.ai) and a small settings sheet. */
(function () {
  var KEY = "ghostlight.apikey";
  var MODEL = "claude-haiku-5-5";
  function getKey() { try { return localStorage.getItem(KEY) || ""; } catch (e) { return ""; } }

  window.GL_AI_OFF = "AI 功能需要你自己的 Anthropic API Key：点右上角的齿轮填写。";

  function err(code, message) { var e = new Error(message); e.code = code; return e; }

  async function call(input, opts) {
    opts = opts || {};
    var key = getKey();
    if (!key) throw err("not_granted", window.GL_AI_OFF);
    var messages = typeof input === "string" ? [{ role: "user", content: input }] : input;
    var res;
    try {
      res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": key,
          "anthropic-version": "2023-06-01",
          "anthropic-dangerous-direct-browser-access": "true"
        },
        body: JSON.stringify({ model: MODEL, max_tokens: 1500, messages: messages }),
        signal: opts.signal
      });
    } catch (e) { throw err("network", "网络连接失败"); }
    if (res.status === 401 || res.status === 403) throw err("not_granted", "API Key 无效，请在设置里检查。");
    if (res.status === 429) throw err("rate_limited", "请求太频繁");
    if (!res.ok) throw err("unavailable", "AI 暂时不可用 (" + res.status + ")");
    var data = await res.json();
    var text = (data.content || []).filter(function (b) { return b.type === "text"; }).map(function (b) { return b.text; }).join("");
    if (opts.onText) opts.onText({ text: text, delta: text });
    return { text: text, truncated: data.stop_reason === "max_tokens" };
  }

  function parseJSON(t) {
    try { return JSON.parse(t); } catch (e) {}
    var f = t.match(/```(?:json)?\s*([\s\S]*?)```/); if (f) { try { return JSON.parse(f[1]); } catch (e) {} }
    var a = Math.min.apply(null, [t.indexOf("{"), t.indexOf("[")].filter(function (i) { return i >= 0; }));
    var b = Math.max(t.lastIndexOf("}"), t.lastIndexOf("]"));
    if (a >= 0 && b > a) { try { return JSON.parse(t.slice(a, b + 1)); } catch (e) {} }
    throw err("invalid_json", "AI 的回答格式不对，请再试一次。");
  }

  var ai = function (input, opts) { return call(input, opts); };
  ai.json = async function (input, opts) {
    var inp = typeof input === "string" ? input + "\n\nReply with only the JSON value, no other text." : input;
    var r = await call(inp, opts);
    return parseJSON(r.text);
  };
  window.GL_AI = ai;

  /* Settings sheet */
  document.addEventListener("DOMContentLoaded", function () {
    var head = document.querySelector("header.top");
    if (!head) return;
    var btn = document.createElement("button");
    btn.className = "btn sm"; btn.setAttribute("aria-label", "设置"); btn.textContent = "⚙";
    btn.style.marginLeft = "auto";
    head.appendChild(btn);
    var sheet = document.createElement("div");
    sheet.className = "panel"; sheet.hidden = true;
    sheet.innerHTML = '<h3>设置</h3>' +
      '<label class="small" for="glKey">Anthropic API Key（用于 AI 讲解、对手戏、整剧解释）</label>' +
      '<input type="text" id="glKey" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">' +
      '<div class="hint">Key 只保存在这台手机上。可以在 console.anthropic.com 申请。</div>' +
      '<div class="row"><button class="btn primary sm" id="glSave">保存</button><button class="btn sm" id="glClear">清除</button><button class="btn sm" id="glClose">关闭</button></div>' +
      '<div class="small" id="glMsg"></div>';
    head.insertAdjacentElement("afterend", sheet);
    var input = sheet.querySelector("#glKey");
    btn.onclick = function () { sheet.hidden = !sheet.hidden; input.value = getKey(); };
    sheet.querySelector("#glClose").onclick = function () { sheet.hidden = true; };
    sheet.querySelector("#glClear").onclick = function () { try { localStorage.removeItem(KEY); } catch (e) {} input.value = ""; sheet.querySelector("#glMsg").textContent = "已清除"; };
    sheet.querySelector("#glSave").onclick = function () {
      try { localStorage.setItem(KEY, input.value.trim()); } catch (e) {}
      sheet.querySelector("#glMsg").textContent = input.value.trim() ? "已保存，AI 功能可以用了。" : "已清除";
    };
  });
})();
