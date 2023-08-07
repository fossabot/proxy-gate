import apple from "./auth/apple.js";
import facebook from "./auth/facebook.js";
import google from "./auth/google.js";
import plex from "./auth/plex.js";

const auth = {};

const methodsObj = {
  apple: apple,
  facebook: facebook,
  google: google,
  plex: plex,
};

auth.methods = {
  apple: apple,
  facebook: facebook,
  google: google,
  plex: plex,
};

// Depending on whats needed show the auth buttons
auth.setup = function setup() {
  console.log("Doing auth setup");
  const urlSearchParams = new URLSearchParams(window.location.search);
  let methods = urlSearchParams.get("methods");

  // Check if methods is null or not a string
  if (!methods || typeof methods !== "string") {
    // Set default methods
    methods = ["apple", "facebook", "google", "plex"];
  } else {
    // Split the string into an array using the comma separator
    methods = methods.split(",");
  }

  methods.forEach((method) => {
    const elementId =
      "authWith" + method.charAt(0).toUpperCase() + method.slice(1) + "Button";
    const authButton = document.getElementById(elementId);
    if (authButton) {
      authButton.hidden = false;
      authButton.addEventListener(
        "click",
        auth.methods[method].workflowStepStart.bind(null, elementId)
      );
    }
  });
  console.log("Completed doing auth setup");
};

export default auth;
