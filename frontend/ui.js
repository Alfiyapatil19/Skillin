window.UI = {
  toast(message, type = "info") {
    const toast = document.createElement("div");
    const color =
      type === "success" ? "#22c55e" :
      type === "error" ? "#ef4444" :
      "#3b82f6";
    toast.textContent = message;
    toast.style.cssText = [
      "position:fixed",
      "top:20px",
      "right:20px",
      "background:" + color,
      "color:#fff",
      "padding:10px 14px",
      "border-radius:10px",
      "z-index:9999",
      "font-size:14px",
      "box-shadow:0 10px 25px rgba(0,0,0,.2)",
      "transform:translateY(-8px)",
      "opacity:0",
      "transition:all .2s ease"
    ].join(";");
    document.body.appendChild(toast);
    requestAnimationFrame(() => {
      toast.style.transform = "translateY(0)";
      toast.style.opacity = "1";
    });
    setTimeout(() => {
      toast.style.transform = "translateY(-8px)";
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 220);
    }, 2200);
  },

  setLoading(el, loadingText = "Loading...") {
    if (!el) return;
    el.dataset.prevHtml = el.innerHTML;
    el.dataset.prevDisabled = String(!!el.disabled);
    el.disabled = true;
    el.innerHTML = loadingText;
    el.style.opacity = "0.8";
  },

  clearLoading(el) {
    if (!el) return;
    if (el.dataset.prevHtml !== undefined) {
      el.innerHTML = el.dataset.prevHtml;
    }
    el.disabled = el.dataset.prevDisabled === "true";
    el.style.opacity = "";
  }
};
