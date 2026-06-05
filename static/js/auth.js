// auth.js
document.addEventListener('DOMContentLoaded', () => {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const username = localStorage.getItem('loggedInUser') || 'User';
    const userRole = localStorage.getItem('userRole') || 'user';

    // Protect Dashboard, Upload and Admin pages if not logged in
    const currentPage = window.location.pathname.split('/').pop() || '';
    const protectedPages = ['upload.html', 'dashboard.html'];

    if (!isLoggedIn && protectedPages.includes(currentPage)) {
        alert("You must be logged in to access this page.");
        window.location.href = 'login.html';
        return;
    }

    // Role-based protection for the admin page
    if (currentPage === 'admin.html' && userRole !== 'admin') {
        alert("Access Denied: Admins only.");
        window.location.href = 'index.html';
        return;
    }

    // Redirect logged in users away from login/signup pages
    const guestOnlyPages = ['login.html', 'signup.html'];
    if (isLoggedIn && guestOnlyPages.includes(currentPage)) {
        window.location.href = 'index.html';
        return;
    }

    const navs = document.querySelectorAll('nav');
    navs.forEach(nav => {
        const links = Array.from(nav.querySelectorAll('a'));

        if (isLoggedIn) {
            links.forEach(link => {
                if (link.getAttribute('href') === 'login.html' || link.getAttribute('href') === 'signup.html') {
                    link.style.display = 'none';
                }
            });

            if (!nav.querySelector('.logout-btn')) {
                let extraLinksHtml = '';
                if (currentPage !== 'dashboard.html') {
                    extraLinksHtml += `<a href="dashboard.html" class="medical-btn medical-btn-success dashboard-btn"><i class="fas fa-chart-line"></i> Dashboard</a>`;
                }
                
                if (userRole === 'admin' && currentPage !== 'admin.html') {
                    extraLinksHtml += `<a href="admin.html" class="medical-btn medical-btn-secondary admin-btn"><i class="fas fa-cog"></i> Admin Panel</a>`;
                }

                const logoutHtml = `<a href="#" class="medical-btn medical-btn-danger logout-btn"><i class="fas fa-sign-out-alt"></i> Logout (${username} - ${userRole})</a>`;
                nav.insertAdjacentHTML('beforeend', extraLinksHtml + logoutHtml);

                nav.querySelector('.logout-btn').addEventListener('click', (e) => {
                    e.preventDefault();
                    localStorage.setItem('isLoggedIn', 'false');
                    localStorage.removeItem('loggedInUser');
                    localStorage.removeItem('userRole');
                    window.location.href = 'index.html';
                });
            }
        }
    });
});
