var theme = window.localStorage.currentTheme;

$("body").addClass(theme);

if ($("body").hasClass("night")) {
  $(".dntoggle").addClass("fas fa-sun");
  $(".dntoggle").removeClass("fas fa-moon");
} else {
  $(".dntoggle").removeClass("fas fa-sun");
  $(".dntoggle").addClass("fas fa-moon");
}

$(".dntoggle").click(function () {
  $(".dntoggle").toggleClass("fas fa-sun");
  $(".dntoggle").toggleClass("fas fa-moon");

  if ($("body").hasClass("night")) {
    $("body").toggleClass("night");
    localStorage.removeItem("currentTheme");
    localStorage.currentTheme = "day";
  } else {
    $("body").toggleClass("night");
    localStorage.removeItem("currentTheme");
    localStorage.currentTheme = "night";
  }
});
