// Simple interaction: click the logo to toggle the "active" state
document.addEventListener("DOMContentLoaded", () => {
  const logo = document.querySelector(".skillin-logo");

  if (!logo) return;

  logo.addEventListener("click", () => {
    logo.classList.toggle("active");
  });
});
