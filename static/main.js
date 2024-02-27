function set_active(id) {
 let element = document.getElementById(id);
 element.classList.add('active');
 element.setAttribute("aria-current", "page");
}