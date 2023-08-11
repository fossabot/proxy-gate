// reference: https://developers.google.com/identity/gsi/web/guides/overview
import utils from "../utils.js";

// we call the namespace gsi to avoid name collisions with google namespace
const gsi = {};

gsi.workflowSetup = function workflowSetup() {
  const googleAuthMetaz = utils.proxyGateMetaz["google_auth"];
  if (!googleAuthMetaz) {
    utils.showError(new Error("No Google Auth Metaz provided."));
    console.error("No Google Auth Metaz provided.");
    return;
  }

  const googleClientId = googleAuthMetaz["client_id"];
  console.log("Google Client ID: " + googleClientId);

  if (!googleClientId) {
    utils.showError(new Error("No Google Client ID specified."));
    console.error("No Google Client ID specified.");
    return;
  }

  window.onload = function () {
    google.accounts.id.initialize({
      client_id: googleClientId,
      auto_select: true,
      callback: gsi.workflowStepCallback,
    //   context: "signin",
      ux_mode: "redirect",
    });
  };
};

gsi.workflowStepStart = function workflowStepStart(buttonId) {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const authWithGoogleButton = document.getElementById(buttonId);
  if (!authWithGoogleButton) {
    return;
  }
  google.accounts.id.prompt((notification) => {
    console.log(notification);
    if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        document.cookie =  `g_state=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT`;
        gsi.workflowStepStart(buttonId);
    }
    
  });
};

gsi.workflowStepCallback = function workflowStepCallback(CredentialResponse) {
    console.log(CredentialResponse)
  };

export default gsi;
