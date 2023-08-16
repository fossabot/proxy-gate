function loadAuthJSFile(filename) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = filename;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function loadAuthMethods() {
  const methods = ["plex"];

  methods.forEach((method) => {
    const filename = `js/auth/${method}.js`;
    loadAuthJSFile(filename)
      .then(() => console.log(`${filename} loaded successfully.`))
      .catch((error) => console.error(`Failed to load ${filename}.`, error));
  });
}

try {
  loadAuthMethods();
} catch (error) {
  console.error(error.message);
}
