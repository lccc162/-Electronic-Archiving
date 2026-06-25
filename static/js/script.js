// Dark Mode Toggle
function toggleDarkMode() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Show Toast Notification
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// Simple Table Search
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.querySelector(`.${tableId} table`);
    const trs = table.getElementsByTagName('tr');

    for (let i = 1; i < trs.length; i++) {
        let match = false;
        const tds = trs[i].getElementsByTagName('td');
        for (let j = 0; j < tds.length; j++) {
            if (tds[j].textContent.toLowerCase().indexOf(filter) > -1) {
                match = true;
                break;
            }
        }
        trs[i].style.display = match ? '' : 'none';
    }
}

// Copy Table to Clipboard
function copyTableToClipboard() {
    const table = document.querySelector('table');
    let range, sel;
    if (document.createRange && window.getSelection) {
        range = document.createRange();
        sel = window.getSelection();
        sel.removeAllRanges();
        try {
            range.selectNodeContents(table);
            sel.addRange(range);
        } catch (e) {
            range.selectNode(table);
            sel.addRange(range);
        }
        document.execCommand('copy');
        sel.removeAllRanges();
        showToast('تم نسخ الجدول إلى الحافظة!');
    }
}

// Initialize Theme
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }

    // Initial check for flashed messages from Flask
    const toast = document.getElementById('toast');
    if (toast && toast.textContent.trim() !== "") {
        toast.style.display = 'block';
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }
});
