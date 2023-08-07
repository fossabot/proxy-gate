import utils from "./utils.js";
// This script is responsible for doing branding operations
const branding = {};

branding.setPageTitle = function setPageTitle(title) {
  document.title = title;
};

branding.setAppVer = function setAppVer(version) {
  const appVerElement = document.getElementById("versionFooter");
  appVerElement.innerHTML = version;
};

branding.main = function main() {
  console.log("Performing branding operations.");
  const appName = utils.getValueFromHeader("X-App-Name", "ProxyGate");
  const appVer = utils.getValueFromHeader("X-App-Version", "0.0.0");
  branding.setPageTitle(`${appName} - Login`);
  branding.setAppVer(appVer);
  console.log("Completed performing branding operations.");
};

export default branding;
