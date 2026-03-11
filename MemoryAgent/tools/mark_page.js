(() => {
  const CATEGORY_CONFIG = {
    input: { color: "#1E88E5", selector: "input, textarea, select, [contenteditable='true']" },
    action: { color: "#2E7D32", selector: "button, input[type='submit'], input[type='button']" },
    navigation: { color: "#6A1B9A", selector: "a, [role='link']" },
    info: { color: "#EF6C00", selector: "[role='label'], [readonly]" },
    other: { color: "#616161", selector: "[role]" }
  };

  const isVisible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  const getText = (el) => el.innerText?.trim() || el.value?.trim() || el.getAttribute("aria-label")?.trim() || "";

  const getXPath = (el) => {
    if (el.id) return `//*[@id="${el.id}"]`;
    const parts = [];
    while (el && el.nodeType === Node.ELEMENT_NODE) {
      let index = 1, sib = el.previousSibling;
      while (sib) {
        if (sib.nodeType === Node.ELEMENT_NODE && sib.tagName === el.tagName) index++;
        sib = sib.previousSibling;
      }
      parts.unshift(`${el.tagName.toLowerCase()}[${index}]`);
      el = el.parentNode;
    }
    return "/" + parts.join("/");
  };

  // Overlay 根节点
  const overlayRoot = document.createElement("div");
  overlayRoot.id = "__som_overlay_root__";
  overlayRoot.style.position = "absolute";
  overlayRoot.style.left = "0";
  overlayRoot.style.top = "0";
  overlayRoot.style.zIndex = "2147483647";
  overlayRoot.style.pointerEvents = "none";
  document.body.appendChild(overlayRoot);

  const elementMap = {};
  let somId = 1;

  Object.entries(CATEGORY_CONFIG).forEach(([category, cfg]) => {
    const elements = Array.from(document.querySelectorAll(cfg.selector));
    elements.forEach((el) => {
      if (!isVisible(el) || el.__som_marked__) return;
      el.__som_marked__ = true;

      const rect = el.getBoundingClientRect();
      const id = somId++;

      // 可视化 outline
      el.style.outline = `2px solid ${cfg.color}`;
      el.style.outlineOffset = "1px";

      // 序号标签
      const label = document.createElement("div");
      label.innerText = id;
      label.style.position = "absolute";
      label.style.left = `${rect.right + window.scrollX - 12}px`; // 右上角偏移
      label.style.top = `${rect.top + window.scrollY - 8}px`;
      label.style.background = cfg.color;
      label.style.color = "#FFFFFF";
      label.style.fontSize = "10px";       // 更小字体
      label.style.fontWeight = "bold";
      label.style.padding = "0px 2px";     // 缩小 padding
      label.style.borderRadius = "3px";
      label.style.opacity = "0.85";        // 半透明
      label.style.boxShadow = "0 1px 2px rgba(0,0,0,0.3)";
      overlayRoot.appendChild(label);

      // 结构化数据
      elementMap[id] = {
        som_id: id,
        category,
        tag: el.tagName.toLowerCase(),
        type: el.type || null,
        text: getText(el),
        id_attr: el.id || null,
        name: el.name || null,
        class: el.className || null,
        required: el.required || false,
        disabled: el.disabled || false,
        readonly: el.readOnly || false,
        bbox: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height)
        },
        xpath: getXPath(el)
      };
    });
  });

  return elementMap;
})();
