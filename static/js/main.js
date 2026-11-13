
document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menuToggle");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    if (!menuToggle || !sidebar || !overlay) {
        return;
    }

    function openMenu() {
        sidebar.classList.add("open");
        overlay.classList.add("show");
        menuToggle.setAttribute("aria-expanded", "true");
    }

    function closeMenu() {
        sidebar.classList.remove("open");
        overlay.classList.remove("show");
        menuToggle.setAttribute("aria-expanded", "false");
    }

    menuToggle.addEventListener("click", function () {
        if (sidebar.classList.contains("open")) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    overlay.addEventListener("click", closeMenu);

    document.querySelectorAll(".nav-link").forEach(function (link) {
        link.addEventListener("click", closeMenu);
    });
});
