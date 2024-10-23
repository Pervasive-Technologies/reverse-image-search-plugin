import { defineConfig } from "@voxel51/fiftyone-js-plugin-build";
import { dirname } from "path";
import { fileURLToPath } from "url";

const dir = dirname(fileURLToPath(import.meta.url));

const myPluginThirdPartyDependencies = [
    "react-dropzone",
    "lodash"
];

const myAdditionalVitePlugins = [
    // add any additional Vite plugins here
];

export default defineConfig(dir, {
  buildConfigOverride: { sourcemap: true },
  forceBundleDependencies: myPluginThirdPartyDependencies,
  plugins: myAdditionalVitePlugins
});
