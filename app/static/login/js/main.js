import auth from "./auth.js";
import utils from "./utils.js";
import branding from "./branding.js";

function loadJSFile(filename) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = filename;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function loadJSFiles(filenames) {
  filenames.forEach((filename) => {
    loadJSFile(filename)
      .then(() => console.log(`${filename} loaded successfully.`))
      .catch((error) => console.error(`Failed to load ${filename}.`, error));
  });
}

function pageSetup() {
  branding.main();
  utils.resetDynamicContent();
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
}

const urlSearchParams = new URLSearchParams(window.location.search);
const workflowStep = urlSearchParams.get("workflowStep") || "start";
document.addEventListener("DOMContentLoaded", pageSetup);

if (workflowStep == "start" || workflowStep == "forbidden") {
  const redirectParam = urlSearchParams.get("redirect");
  if (workflowStep == "forbidden") {
    document.addEventListener(
      "DOMContentLoaded",
      workflowStart.bind(null, redirectParam, true)
    );
  } else {
    document.addEventListener(
      "DOMContentLoaded",
      workflowStart.bind(null, redirectParam, false)
    );
  }
} else if (workflowStep == "callback") {
  document.addEventListener("DOMContentLoaded", workflowCallback);
} else {
  document.addEventListener("DOMContentLoaded", function () {
    const error = new Error("Invalid workflow step specified.");
    utils.showError(error);
  });
  console.error("Invalid workflow step specified.");
}
