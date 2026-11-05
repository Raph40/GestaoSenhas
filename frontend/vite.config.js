import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    plugins: [tailwindcss()],
    root: "paginasHTML",
    server: {
    port: 3000, // define aqui a porta pretendida
    // strictPort: true, // (opcional) se a porta estiver ocupada, falha em vez de tentar a próxima automaticamente
  }
});