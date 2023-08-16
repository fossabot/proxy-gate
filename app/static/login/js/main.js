import auth from "./auth.js";
import utils from "./utils.js";
import branding from "./branding.js";

function pageSetup() {
  console.log("Running page setup");
  branding.main();
  utils.resetDynamicContent();
  console.log("Completed running page setup");
}

function workflowCallback() {
  utils.resetDynamicContent();
  utils.showProcessing("Loading");
  const urlSearchParams = new URLSearchParams(window.location.search);
  const method = urlSearchParams.get("method");
  let containerTitle = document.getElementById("containerTitle");
  containerTitle.hidden = false;

  if (!method) {
    utils.showError(new Error("No method specified."));
    console.error("No method specified.");
  } else {
    utils.showProcessing("Logging in");
    auth.methods[method].workflowStepCallback();
  }
}

function workflowStart(redirectParam, forbidden = false) {
  console.log("Running workflow start");
  utils.resetDynamicContent();

  let redirectHostname = "the given resource";
  if (redirectParam != null) {
    const url = new URL(redirectParam);
    redirectHostname = url.hostname;
  }
  if (forbidden) {
    let forbiddenCard = document.getElementById("forbiddenCard");
    forbiddenCard.hidden = false;
    let forbiddenCardText = document.getElementById("forbiddenCardText");
    forbiddenCardText.innerHTML = `You do not have permission to access ${redirectHostname}.`;
    forbiddenCardText.innerHTML +=
      "</br>Try logging in with another credential or contact the application administrator.";
  }
  let containerTitle = document.getElementById("containerTitle");
  containerTitle.innerHTML = `Login to ${redirectHostname}`;
  containerTitle.hidden = false;

  let divAuthButtons = document.getElementById("divAuthButtons");
  divAuthButtons.hidden = false;
  auth.setup();
  console.log("Completed running workflow start");
}

function main() {
  console.log("Running main");
  const urlSearchParams = new URLSearchParams(window.location.search);
  const workflowStep = urlSearchParams.get("workflowStep") || "start";
  pageSetup();

  if (workflowStep == "start" || workflowStep == "forbidden") {
    const redirectParam = urlSearchParams.get("redirect");
    if (workflowStep == "forbidden") {
      workflowStart(redirectParam, true);
    } else {
      workflowStart(redirectParam, false);
    }
  } else if (workflowStep == "callback") {
    workflowCallback();
  } else {
    const error = new Error("Invalid workflow step specified.");
    utils.showError(error);

    console.error("Invalid workflow step specified.");
  }
  console.log("Completed running main");
}

if (document.readyState !== "loading") {
  console.log("document is already ready, executing main");
  main();
} else {
  console.log("document was not ready, adding event");
  document.addEventListener("DOMContentLoaded", function () {
    console.log("DOMContentLoaded event fired");
    main();
  });
}
