// Content script: provides page metadata on request
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "get.page_metadata") {
    sendResponse({
      url: window.location.href,
      title: document.title,
      text: document.body?.innerText?.slice(0, 2000) || "",
    });
  }
  return false;
});
