!function n(i,a,s){function r(o,t){if(!a[o]){if(!i[o]){var e="function"==typeof require&&require;if(!t&&e)return e(o,!0);if(l)return l(o,!0);throw new Error("Cannot find module '"+o+"'")}t=a[o]={exports:{}};i[o][0].call(t.exports,function(t){var e=i[o][1][t];return r(e||t)},t,t.exports,n,i,a,s)}return a[o].exports}for(var l="function"==typeof require&&require,t=0;t<s.length;t++)r(s[t]);return r}({1:[function(t,e,o){const n=$("#header");getComputedStyle(document.body);function i(){if($(".s-tabs-01__nav").length){let t=$(".s-tabs-01__nav .nav-item-dropdown"),e=Math.round(t.outerWidth(!0));var o=$(".s-tabs-01__nav").outerWidth(!0);$(".s-tabs-01__nav .nav-item").each(function(){e+=Math.round($(this).outerWidth(!0))}),e>=o&&($(".s-tabs-01__nav .nav-item .nav-link").last().clone().removeClass("nav-link").prependTo(".s-tabs-01__nav .dropdown-menu"),$(".s-tabs-01__nav .nav-item").last().remove(),t.css("visibility","visible"),i())}}$(window).on("load",function(){$('[data-toggle="popover"]').popover(),$('[data-toggle="tooltip"]').tooltip(),i(),$(".alert-dismissible-once").length&&$(".alert-dismissible-once").each(function(){var t=$(this),e=$(t).attr("id");null===localStorage.getItem(e)&&$(t).removeClass("d-none")})}),$(window).on("resize orientationchange",function(){i()}),$(window).on("scroll",function(){}),$("[data-toggle=burger]").on("click tap",function(t){t.preventDefault(),n.data("top",n.offset().top),n.toggleClass("is-opened")}).on("keypress",function(t){13==t.which&&(t.preventDefault(),n.data("top",n.offset().top),n.toggleClass("is-opened"))}),$(".input-group .form-control").on("focus",function(t){t.preventDefault(),$(this).parent(".input-group").toggleClass("has-focus")}).on("blur",function(t){t.preventDefault(),$(this).parent(".input-group").toggleClass("has-focus")}),$("body").on("keydown input","textarea[data-expandable]",function(){this.style.removeProperty("height"),this.style.height=this.scrollHeight+2+"px"}).on("mousedown focus","textarea[data-expandable]",function(){this.style.removeProperty("height"),this.style.height=this.scrollHeight+2+"px"}),$("[data-target-conseil]").on("focus",function(t){t.preventDefault();t=$(this).data("target-conseil");$(t).toggleClass("is-openable")}).on("blur",function(t){t.preventDefault();t=$(this).data("target-conseil");$(t).toggleClass("is-openable")}),$("[data-clipboard=copy]").on("click tap",function(){$(this).tooltip("show");var t=$(this).closest(".input-group"),t=$(t).find(".form-control").val();navigator.clipboard.writeText(t).then(()=>{}).catch(()=>{})}),$("[data-clipboard=copy]").on("blur",function(){$(this).tooltip("hide")}),$(".alert-dismissible-once .close").on("click tap",function(){var t=$(this).closest(".alert-dismissible-once"),e=$(t).attr("id");localStorage.setItem(e,"seen"),$(t).addClass("d-none")})},{}]},{},[1]);