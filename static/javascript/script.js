// DARK MODE 1



// var theme = window.localStorage.currentTheme;

// $("body").addClass(theme);

// if ($("body").hasClass("night")) {
//   $(".dntoggle").addClass("fas fa-sun");
//   $(".dntoggle").removeClass("fas fa-moon");
// } else {
//   $(".dntoggle").removeClass("fas fa-sun");
//   $(".dntoggle").addClass("fas fa-moon");
// }

// $(".dntoggle").click(function () {
//   $(".dntoggle").toggleClass("fas fa-sun");
//   $(".dntoggle").toggleClass("fas fa-moon");

//   if ($("body").hasClass("night")) {
//     $("body").toggleClass("night");
//     localStorage.removeItem("currentTheme");
//     localStorage.currentTheme = "day";
//   } else {
//     $("body").toggleClass("night");
//     localStorage.removeItem("currentTheme");
//     localStorage.currentTheme = "night";
//   }
// });


// function darkmode(){
//     var SetTheme = document.body;
//     SetTheme.classList.toggle("night")
//     var theme;
//     if(SetTheme.classList.contains("night")){
//         console.log("Dark mode");
//         theme = "DARK";
//     }else{
//         console.log("Light mode");
//         theme = "LIGHT";
//     }
//     // save to localStorage
//     localStorage.setItem("PageTheme", JSON.stringify(theme));
//     // ensure you convert to JSON like i have done -----JSON.stringify(theme)
// }

// setInterval(() => {
//     let GetTheme = JSON.parse(localStorage.getItem("PageTheme"));
//     console.log(GetTheme);
//     if(GetTheme === "DARK"){
//         document.body.classList = "night";
//     }else{
//         document.body.classList = "";
//     }
// }, 5);





// DARK MODE 2

// // check for saved 'darkMode' in localStorage
// let darkMode = localStorage.getItem('darkMode'); 

// const darkModeToggle = document.querySelector('#dark-mode-toggle');

// const enableDarkMode = () => {
//   // 1. Add the class to the body
//   document.body.classList.add('night');
//   // 2. Update darkMode in localStorage
//   localStorage.setItem('darkMode', 'enabled');
// }

// const disableDarkMode = () => {
//   // 1. Remove the class from the body
//   document.body.classList.remove('night');
//   // 2. Update darkMode in localStorage 
//   localStorage.setItem('darkMode', null);
// }
 
// // If the user already visited and enabled darkMode
// // start things off with it on
// if (darkMode === 'enabled') {
//   enableDarkMode();
// }

// // When someone clicks the button
// darkModeToggle.addEventListener('click', () => {
//   // get their darkMode setting
//   darkMode = localStorage.getItem('darkMode'); 
  
//   // if it not current enabled, enable it
//   if (darkMode !== 'enabled') {
//     enableDarkMode();
//   // if it has been enabled, turn it off  
//   } else {  
//     disableDarkMode(); 
//   }
// });





// DARK MODE 3


const darkBtn = document.querySelector('.dntoggle');
const bodyEl = document.querySelector('body');
const navbar = document.querySelector('#navbar')
const darkMode = () => {
    bodyEl.classList.toggle('night');
    navbar.classList.toggle('night')
}

darkBtn.addEventListener('click', () => {
    // Get the value of the "dark" item from the local storage on every click
    setDarkMode = localStorage.getItem('dark');

    if(setDarkMode !== "on") {
        darkMode();
        // Set the value of the itwm to "on" when dark mode is on
        setDarkMode = localStorage.setItem('dark', 'on');
    } else {
        darkMode();
        // Set the value of the item to  "null" when dark mode if off
        setDarkMode = localStorage.setItem('dark', null);
    }
});

// Get the value of the "dark" item from the local storage
let setDarkMode = localStorage.getItem('dark');

// Check dark mode is on or off on page reload
if(setDarkMode === 'on') {
    darkMode();
}