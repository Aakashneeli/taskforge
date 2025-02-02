document.getElementById('runTask').addEventListener('click', async () => {
    const task = document.getElementById('taskInput').value;
    
    // Get current tab
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    
    // Send task to background script
    chrome.runtime.sendMessage({
      action: "executeTask",
      task: task,
      tabId: tab.id
    });
  });