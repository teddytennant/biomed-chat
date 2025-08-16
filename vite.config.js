import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // We don't need a dev server proxy if we run the Node server and Vite dev server separately.
  // The Node server will serve the API, and the Vite server will serve the frontend.
  // The browser will make requests to the Node server API at http://localhost:3000.
  build: {
    // Output the built files to a directory that can be served by the Node server.
    outDir: 'dist/client',
    // Empty the output directory before building.
    emptyOutDir: true,
  },
});
