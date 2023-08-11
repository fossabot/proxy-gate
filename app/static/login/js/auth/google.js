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

  function handleCredentialResponse(response) {
    console.log("Encoded JWT ID token: " + response.credential);
  }
  window.onload = function () {
    google.accounts.id.initialize({
      client_id: googleClientId,
      callback: gsi.workflowStepCallback,
    });
    google.accounts.id.renderButton(
      // style="width: auto" class="w-100 btn btn-lg btn-primary btn-google text-wrap fs-md"
      document.getElementById("authWithGoogleButton"),
      { theme: "outline", size: "large", text: "continue_with", width: "300", shape: "rectangular" } // customization attributes
    );

    // document.getElementById("authWithGoogleButton").classList.add("w-100");
    // document.getElementById("authWithGoogleButton").classList.add("btn");
    // document.getElementById("authWithGoogleButton").classList.add("btn-lg");
    // document.getElementById("authWithGoogleButton").classList.add("btn-primary");
    // document.getElementById("authWithGoogleButton").classList.add("fs-md");
    // only do the id prompt if method is google todo later
    // google.accounts.id.prompt(); // also display the One Tap dialog
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
      document.cookie = `g_state=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT`;
      gsi.workflowStepStart(buttonId);
    }
  });
};

gsi.workflowStepCallback = function workflowStepCallback(CredentialResponse) {
  console.log(CredentialResponse);
};

export default gsi;
