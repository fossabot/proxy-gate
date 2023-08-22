// https://levelup.gitconnected.com/your-own-button-for-sign-in-with-google-e732192d0476
import utils from "../utils.js";
const google = {};

google.workflowSetup = function workflowSetup() {};

google.workflowStepStart = function workflowStepStart(buttonId) {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const { protocol, host } = window.location;
  const redirectParam = urlSearchParams.get("redirect");

  var random = {
    x: getRandomValues(),
    y: getRandomValues(),
    nonce: getRandomValues(),
  };
  const state = utils.base64UrlEncode(redirectParam)
  oauthSignIn(utils.proxyGateMetaz["google_auth"]["client_id"], state);
};

google.workflowStepCallback = function workflowStepCallback() {
  const fragmentIdentifier = window.location.hash; // Get the fragment identifier including the hash

  // Remove the leading '#' and split the fragment identifier into individual parameters
  const parameterPairs = fragmentIdentifier.substring(1).split('&');

  // Create an object to store the parameters
  const hashParameters = {};

  // Loop through the parameter pairs and split them into keys and values
  parameterPairs.forEach(pair => {
    const [key, value] = pair.split('=');
    hashParameters[key] = value;
  });

  const redirectParam = utils.base64UrlDecode(hashParameters.state)
  const redirectParamBase64Encoded = hashParameters.state
  const accessToken = hashParameters.access_token;
  getProxyGateSession(accessToken, redirectParamBase64Encoded)
  .then((data) => {
    window.location.href = redirectParam;
  })
  .catch((error) => {
    console.error("getProxyGateSession API call failed:", error);
    utils.showError(error);
  });

}
export default google;

function sha256(a) {
  return window.crypto.subtle
    .digest("SHA-256", new TextEncoder().encode(a))
    .then(function (out) {
      return Array.from(new Uint8Array(out))
        .map(function (x) {
          return x.toString(16).padStart(2, 0);
        })
        .join("");
    });
}

function getRandomValues() {
  var arr = new Uint32Array(16);
  window.crypto.getRandomValues(arr);
  return Array.from(arr)
    .map(function (x) {
      return x.toString(36);
    })
    .join("")
    .substr(0, 16);
}

function oauthSignIn(clientId, state) {
  // Google's OAuth 2.0 endpoint for requesting an access token
  const oauth2Endpoint = "https://accounts.google.com/o/oauth2/v2/auth";
  const { protocol, host } = window.location;
  const callbackUrl = `${protocol}//${host}/login?method=google&workflowStep=callback`;

  // Create <form> element to submit parameters to OAuth 2.0 endpoint.
  var form = document.createElement("form");
  form.setAttribute("method", "GET"); // Send as a GET request.
  form.setAttribute("action", oauth2Endpoint);

  // Parameters to pass to OAuth 2.0 endpoint.
  var params = {
    client_id: clientId,
    redirect_uri: callbackUrl,
    response_type: "token",
    scope: "https://www.googleapis.com/auth/userinfo.email",
    state: state,
    prompt: "select_account",
  };

  // Add form parameters as hidden input values.
  for (var p in params) {
    var input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", p);
    input.setAttribute("value", params[p]);
    form.appendChild(input);
  }

  // Add form to page and submit it to open the OAuth 2.0 endpoint.
  document.body.appendChild(form);
  form.submit();
}

async function getProxyGateSession(
  accessToken,
  redirectParamBase64Encoded
) {
  const { protocol, host } = window.location;
  const apiUrl = `${protocol}//${host}${utils.proxyGateMetaz["google_auth"]["session_endpoint"]}?googleAccessToken=${accessToken}&redirect=${redirectParamBase64Encoded}`;
  try {
    // Make the API call using fetch()
    const response = await fetch(apiUrl, {
      method: "get",
    });

    // Check if the response was successful (status code 200-299)
    if (!response.ok) {
      throw new Error("PRoxy Gate get session response was not ok");
    }

    return true;
  } catch (error) {
    console.error("Error fetching data:", error);
    return false;
  }
}