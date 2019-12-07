// Start Dark Mode
document.addEventListener('DOMContentLoaded', function () {
const checkbox = document.querySelector('.dark-mode-checkbox');

checkbox.checked = localStorage.getItem('darkMode') === 'true';

checkbox.addEventListener('change', function (event) {
  localStorage.setItem('darkMode', event.currentTarget.checked);
});
});
// End Dark Mode
