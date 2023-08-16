import utils from "../utils.js";
const plex = {};

plex.workflowStepStart = function workflowStepStart(buttonId) {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const authWithPlexButton = document.getElementById(buttonId);
  if (!authWithPlexButton) {
    return;
  }
  const redirectParam = urlSearchParams.get("redirect");
  getPlexPins()
    .then((data) => {
      const plexClientId = data.clientIdentifier;
      const code = data.code;
      const pinId = data.id;

      const { protocol, host } = window.location;
      const callbackUrl = `${protocol}//${host}/login?method=plex&workflowStep=callback&pinId=${pinId}&code=${code}&plexClientId=${plexClientId}&redirect=${redirectParam}`;
      const callbackUrlEncode = encodeURIComponent(callbackUrl);

      const authAppUrl = `https://app.plex.tv/auth#?clientID=${plexClientId}&code=${code}&forwardUrl=${callbackUrlEncode}`;

      console.log("Callback URL:", callbackUrl);
      console.log("Redirect URL:", authAppUrl);

      // Uncomment the line below to redirect the user to the authentication URL
      window.location.href = authAppUrl;
    })
    .catch((error) => {
      console.error("API call failed:", error);
      // Optionally, you can show an error message to the user here
    });
};

plex.workflowStepCallback = function workflowStepCallback() {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const redirectParam = urlSearchParams.get("redirect");
  const redirectUrlEncode = encodeURIComponent(redirectParam);
  getPlexTokenWithRetry()
    .then((data) => {
      const plexAuthToken = data.authToken;
      const plexClientId = data.clientIdentifier;
      getProxyGateSession(plexAuthToken, plexClientId, redirectUrlEncode)
        .then((data) => {
          window.location.href = redirectParam;
        })
        .catch((error) => {
          console.error("getProxyGateSession API call failed:", error);
        });
    })
    .catch((error) => {
      console.error("getPlexToken API call failed:", error);
      utils.showError(error);
      // Optionally, you can show an error message to the user here
    });
};

export default plex;

function parseUserAgent() {
  const parser = new UAParser();
  const result = parser.getResult();
  return result;
}

function initializeHeaders() {
  const userAgent = parseUserAgent();
  const headers = new Headers({
    Accept: "application/json",
    // "Content-Type": "application/json",
    "X-Plex-Client-Identifier": getPlexClientId(),
    "X-Plex-Device": userAgent.os.name || "Windows",
    "X-Plex-Device-Name":
      userAgent.browser.name + " (PlexGate)" || "Unknown" + " (PlexGate)",
    "X-Plex-Device-Screen-Resolution":
      window.screen.width + "x" + window.screen.height,
    "X-Plex-Language": "en",
    "X-Plex-Model": "Plex OAuth",
    "X-Plex-Platform": userAgent.browser.name || "Unknown",
    "X-Plex-Platform-Version": userAgent.browser.version || "0.1.0",
    "X-Plex-Product": "PlexGate",
    "X-Plex-Version": "Plex OAuth",
  });
  return headers;
}

function uuidv4() {
  function getRandomHexString(length) {
    const randomHexString = [...Array(length)].map(() =>
      Math.floor(Math.random() * 16).toString(16)
    );
    return randomHexString.join("");
  }

  return (
    getRandomHexString(8) +
    "-" +
    getRandomHexString(4) +
    "-" +
    getRandomHexString(4) +
    "-" +
    getRandomHexString(4) +
    "-" +
    getRandomHexString(12)
  );
}

function getPlexClientId() {
  let plexClientId = localStorage.getItem("plex-client-id");
  if (!plexClientId) {
    plexClientId = uuidv4();
    localStorage.setItem("plex-client-id", plexClientId);
  }
  return plexClientId;
}

// async function getPlexPins() {
//   const apiUrl = "https://plex.tv/api/v2/pins?strong=true";

//   // Set up the headers for the API call
//   const headers = initializeHeaders();

//   try {
//     // Make the API call using fetch()
//     const response = await fetch(apiUrl, {
//       method: "POST",
//       headers: headers,
//     });

//     // Check if the response was successful (status code 200-299)
//     if (!response.ok) {
//       throw new Error("Network response was not ok");
//     }

//     // Parse the response as JSON and return the data
//     const jsonData = await response.json();
//     return jsonData;
//   } catch (error) {
//     console.error("Error fetching data:", error);
//     return null; // or throw the error to handle it in the calling code
//   }
// }

async function getPlexPins() {
  try {
    const apiUrl = "https://plex.tv/api/v2/pins?strong=true";
    const headers = initializeHeaders();
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: headers,
    });

    // Check if the response was successful (status code 200-299)
    if (!response.ok) {
      throw new Error("Network response from getting pin was not ok");
    }

    const data = await response.json();
    console.log("Plex API response:", data);
    return data;
  } catch (error) {
    console.error("API call failed:", error);
    throw error;
  }
}

async function getPlexTokenWithRetry(
  retries = 3,
  delayMs = 2000,
  startDelayMs = 2000
) {
  if (startDelayMs > 0) {
    await new Promise((resolve) => setTimeout(resolve, startDelayMs)); // Wait for the specified delay
  }
  const urlSearchParams = new URLSearchParams(window.location.search);
  const pinId = urlSearchParams.get("pinId");
  const apiUrl = `https://plex.tv/api/v2/pins/${pinId}`;

  // Set up the headers for the API call
  const headers = initializeHeaders();

  try {
    // Make the API call using fetch()
    const response = await fetch(apiUrl, {
      method: "get",
      headers: headers,
    });

    // Check if the response was successful (status code 200-299)
    if (!response.ok) {
      throw new Error("Plex response was not ok");
    }

    // Parse the response as JSON and return the data
    const jsonData = await response.json();
    return jsonData;
  } catch (error) {
    console.error("Error fetching data:", error);

    // Retry the API call if there are remaining retries
    if (retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, delayMs)); // Wait for the specified delay
      return getPlexTokenWithRetry(retries - 1, delayMs); // Retry the API call with one less retry and the same delay
    }

    throw error;
  }
}

async function getProxyGateSession(
  plexAuthToken,
  plexClientId,
  redirectUrlEncode
) {
  const { protocol, host } = window.location;
  const apiUrl = `${protocol}//${host}/plexauth/session?plexAuthToken=${plexAuthToken}&plexClientId=${plexClientId}&redirect=${redirectUrlEncode}`;
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
