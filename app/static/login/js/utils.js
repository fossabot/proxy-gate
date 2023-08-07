const utils = {};

utils.showError = function showError(error, errorTitle = "Error") {
  utils.resetDynamicContent();
  console.log("Showing error.");
  const errorContent = document.getElementById("divError");
  errorContent.hidden = false;
  const errorChildElements = errorContent.children;
  for (let i = 0; i < errorChildElements.length; i++) {
    errorChildElements[i].hidden = false;
  }

  const errorTitleElement = document.getElementById("errorCardTitle");
  errorTitleElement.innerHTML = errorTitle;

  const errorText = document.getElementById("errorCardText");
  errorText.innerHTML = error.message;
  console.log("Completed showing error.");
};

utils.resetDynamicContent = function resetDynamicContent() {
  console.log("Reseting all dynamic content.");
  const dynamicContent = document.getElementById("dynamicContent");
  const dynamicChildElements = dynamicContent.children;
  for (let i = 0; i < dynamicChildElements.length; i++) {
    dynamicChildElements[i].hidden = true;
  }
  console.log("Completed reseting all dynamic content.");
};

utils.showProcessing = function showProcessing(title = "Processing") {
  utils.resetDynamicContent();
  console.log("Showing processing.");
  const errorContent = document.getElementById("divProcessing");
  errorContent.hidden = false;
  const errorChildElements = errorContent.children;
  for (let i = 0; i < errorChildElements.length; i++) {
    errorChildElements[i].hidden = false;
  }

  if (title != null) {
    const containerTitle = document.getElementById("containerTitle");
    containerTitle.innerHTML = title;
    containerTitle.hidden = false;
  } else {
    containerTitle.hidden = false;
  }

  console.log("Completed showing processing.");
};

utils.showForbidden = function showForbidden(error, errorTitle = "Error") {
  utils.resetDynamicContent();
  auth.setup();
  console.log("Showing forbidden.");
  utils.showError(
    "You do not have permission to access the given resource",
    (errorTitle = "Forbidden")
  );
  console.log("Completed showing forbidden.");
};

utils.getValueFromHeader = function getValueFromHeader(
  headerName,
  defaultValue = null
) {
  // Get the current script element
  const scriptElement = document.currentScript;

  // Check if the current script element has a response property
  if (scriptElement && scriptElement.response) {
    // Get the value of the specified header from the response
    const headerValue = scriptElement.response.headers.get(
      headerName,
      defaultValue
    );

    return myVariable;
  }

  return defaultValue;
};

utils.checkURLDoesNotRequireAuth = async function checkURLDoesNotRequireAuth(
  url,
  method = "GET"
) {
  try {
    const headers = initializeHeaders();
    const response = await fetch(url, {
      method: method,
    });

    // Check if the response was successful (status code 200-299)
    if (response.status == 403 || response.status == 401) {
      return false;
    }

    return true;
  } catch (error) {
    throw new Error(
      `Failed to check if URL no longer requires authentication. ${error.message}`
    );
  }
};

export default utils;
